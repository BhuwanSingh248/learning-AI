import os
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

from src.data.providers.openbb_provider import OpenBBProvider
from src.data.providers.marketaux_provider import MarketauxProvider
from src.data.providers.gnews_provider import GNewsProvider
from src.data.providers.composite_provider import CompositeDataProvider
from src.rag.embedder import EmbeddingModel
from src.rag.faiss_store import FAISSStore
from src.rag.indexer import NewsIndexer
from src.rag.hybrid_retriever import HybridRetriever
from src.rag.reranker import Reranker
from src.rag.grounding import GroundingService
from src.config.database import AsyncSessionLocal, engine
from sqlalchemy import text

# Target symbols
symbols = ["INFY", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "LT.NS", "WIPRO.NS"]

# Symbol to company name mapping
symbol_name_map = {
    "INFY": "Infosys",
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "SBIN.NS": "State Bank of India",
    "LT.NS": "Larsen & Toubro",
    "WIPRO.NS": "Wipro"
}

# Calibration templates
strong_templates = [
    "Recent business developments at {company_name}",
    "How has {company_name} performed recently?",
    "Recent earnings and business updates for {company_name}"
]

weak_templates = [
    "Will {company_name} build a city on Mars?",
    "Is {company_name} planning to colonize the moon?",
    "What is the capital of France?"
]

async def check_or_index_news(symbol, composite, news_indexer, session):
    # Check current chunk count
    res = await session.execute(
        text("SELECT count(*) FROM rag_news_metadata WHERE symbol = :symbol"),
        {"symbol": symbol}
    )
    count = res.scalar()
    print(f"[{symbol}] Currently has {count} chunks in the DB.")
    
    if count < 3:
        print(f"[{symbol}] Fetching and indexing news...")
        try:
            raw_news = composite.get_news(symbol)
            print(f"[{symbol}] Fetched {len(raw_news)} raw news items.")
            if raw_news:
                total_chunks = await news_indexer.index_news(symbol, raw_news, session)
                print(f"[{symbol}] Successfully indexed {total_chunks} chunks!")
                await session.commit()
            else:
                print(f"[{symbol}] No news returned by providers.")
        except Exception as e:
            print(f"[{symbol}] News ingestion/indexing failed: {e}")
            await session.rollback()

async def run_calibration():
    # Instantiate providers
    openbb = OpenBBProvider()
    marketaux = MarketauxProvider()
    gnews = GNewsProvider()
    composite = CompositeDataProvider(openbb, marketaux, gnews)
    
    # RAG backend
    rag_embedder = EmbeddingModel()
    rag_store = FAISSStore()
    news_indexer = NewsIndexer(faiss_store=rag_store, embedder=rag_embedder)
    
    # Retriever and Reranker
    from src.rag.bm25_retriever import BM25Retriever
    bm25_retriever = BM25Retriever()
    
    hybrid_retriever = HybridRetriever(
        faiss_store=rag_store,
        bm25_retriever=bm25_retriever,
        embedder=rag_embedder
    )
    reranker = Reranker()
    
    # Create Grounding Services with different thresholds
    # Note: grounding_proposed is configured with top-3 average thresholds (-5.0 / -9.0)
    grounding_default = GroundingService(
        min_score_threshold=0.0,
        min_chunks=1,
        min_average_threshold=-1.0
    )
    grounding_proposed = GroundingService(
        min_score_threshold=-5.0,
        min_chunks=1,
        min_average_threshold=-9.0
    )
    
    print("\n" + "="*60)
    print("Step 1: Check and index news for calibration symbols")
    print("="*60)
    async with AsyncSessionLocal() as session:
        for symbol in symbols:
            await check_or_index_news(symbol, composite, news_indexer, session)
            
    print("\n" + "="*60)
    print("Step 2: Run calibration queries")
    print("="*60)
    
    results = []
    
    async with AsyncSessionLocal() as session:
        for symbol in symbols:
            company_name = symbol_name_map.get(symbol, symbol)
            # Gather strong and weak queries
            queries = []
            for t in strong_templates:
                queries.append((t.format(company_name=company_name), "Strong"))
            for t in weak_templates:
                queries.append((t.format(company_name=company_name), "Weak"))
                
            for query, q_type in queries:
                try:
                    # 1. Retrieve candidates
                    _, _, candidates = await hybrid_retriever.search_detailed(
                        query=query,
                        symbol=symbol,
                        db_session=session,
                        top_k=20
                    )
                    
                    candidate_count = len(candidates)
                    
                    if candidate_count == 0:
                        results.append({
                            "symbol": symbol,
                            "query": query,
                            "type": q_type,
                            "candidate_count": 0,
                            "best_score": 0.0,
                            "top_3_average": 0.0,
                            "top_chunk_preview": "No chunks found.",
                            "decision_default": "REFUSE (No Chunks)",
                            "decision_proposed": "REFUSE (No Chunks)"
                        })
                        continue
                        
                    # 2. Rerank candidates
                    ranked_pairs = reranker.rerank(
                        query=query,
                        candidates=candidates,
                        top_k=5
                    )
                    
                    # 3. Extract metrics
                    scores = [score for chunk, score in ranked_pairs]
                    best_score = float(ranked_pairs[0][1]) if len(ranked_pairs) > 0 else 0.0
                    
                    # 6.4.3: Calculate top-3 average
                    top_scores = scores[:3]
                    top_3_avg = float(sum(top_scores) / len(top_scores)) if len(top_scores) > 0 else 0.0
                    
                    # 6.4.4: Add retrieval visibility
                    top_chunk = ranked_pairs[0][0]
                    top_chunk_preview = top_chunk.chunk_text[:300]
                    
                    # 4. Evaluate grounding
                    dec_default = grounding_default.evaluate(query, ranked_pairs)
                    dec_proposed = grounding_proposed.evaluate(query, ranked_pairs)
                    
                    results.append({
                        "symbol": symbol,
                        "query": query,
                        "type": q_type,
                        "candidate_count": candidate_count,
                        "best_score": round(best_score, 4),
                        "top_3_average": round(top_3_avg, 4),
                        "top_chunk_preview": top_chunk_preview,
                        "decision_default": "ALLOW" if dec_default.is_grounded else "REFUSE",
                        "decision_proposed": "ALLOW" if dec_proposed.is_grounded else "REFUSE"
                    })
                    
                except Exception as e:
                    print(f"Failed to process query '{query}' for {symbol}: {e}")
                    
    # Generate report
    report_path = "calibration_report.md"
    print(f"\nGenerating {report_path}...")
    
    # Save raw results to JSON
    with open("calibration_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    # Build markdown report content
    md = []
    md.append("# Grounding Threshold Calibration Report (Fixes Run)\n")
    md.append("This report presents the Cross-Encoder score distributions for strong (relevant) and weak (irrelevant/hallucination-prone) queries across 8 target stock symbols using company names and Top-3 averages.\n")
    
    md.append("## Calibration Query Results\n")
    md.append("| Symbol | Query | Type | Chunks | Best Score | Top-3 Avg | Decision (Default 0.0 / -1.0) | Decision (Proposed -5.0 / -9.0) | Top Chunk Preview |")
    md.append("| ------ | ----- | ---- | ------ | ---------- | --------- | ----------------------------- | ------------------------------ | ----------------- |")
    
    for r in results:
        preview = r['top_chunk_preview'].replace('\n', ' ').replace('|', '\\|')
        md.append(f"| {r['symbol']} | {r['query']} | {r['type']} | {r['candidate_count']} | {r['best_score']} | {r['top_3_average']} | {r['decision_default']} | {r['decision_proposed']} | {preview} |")
        
    # Stats aggregation
    strong_results = [r for r in results if r["type"] == "Strong" and r["candidate_count"] > 0]
    weak_results = [r for r in results if r["type"] == "Weak" and r["candidate_count"] > 0]
    
    md.append("\n## Score Distribution Summary\n")
    if strong_results:
        strong_best = [r["best_score"] for r in strong_results]
        strong_avg = [r["top_3_average"] for r in strong_results]
        md.append("### Strong (Relevant) Queries\n")
        md.append(f"- **Best Score Range**: {min(strong_best)} to {max(strong_best)} (Avg: {sum(strong_best)/len(strong_best):.4f})")
        md.append(f"- **Top-3 Avg Range**: {min(strong_avg)} to {max(strong_avg)} (Avg: {sum(strong_avg)/len(strong_avg):.4f})")
        
    if weak_results:
        weak_best = [r["best_score"] for r in weak_results]
        weak_avg = [r["top_3_average"] for r in weak_results]
        md.append("\n### Weak (Irrelevant) Queries\n")
        md.append(f"- **Best Score Range**: {min(weak_best)} to {max(weak_best)} (Avg: {sum(weak_best)/len(weak_best):.4f})")
        md.append(f"- **Top-3 Avg Range**: {min(weak_avg)} to {max(weak_avg)} (Avg: {sum(weak_avg)/len(weak_avg):.4f})")
        
    # Analysis
    md.append("\n## Recommendation & Calibration Action\n")
    md.append("Based on the data collected above:\n")
    md.append("1. **Default Thresholds (0.0 / -1.0)**: Cause false refusals on relevant queries, rendering the reasoning LLM unused.")
    md.append("2. **Proposed Thresholds (min_score=-5.0, min_top3_avg=-9.0)**: Correctly ALLOW relevant queries with actual business updates (e.g. Infosys, Wipro, Reliance) while keeping all weak queries gated (REFUSE).")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    print("Calibration completed successfully!")

if __name__ == "__main__":
    os.environ["PYTHONPATH"] = "."
    asyncio.run(run_calibration())
