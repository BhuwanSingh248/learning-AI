"""
API Routing Module

Defines the FastAPI routes exposing the underlying orchestrated StockAgent 
to HTTP requests securely.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db

from src.config.logger import setup_logger
from src.api.schemas import (
    SuggestRequest,
    SuggestResponse,
    SuggestionItem,
    HealthResponse,
    HealthCheckItem,
    AnalyzeRequest,
    AnalyzeResponse
)
from src.config.settings import settings
from src.llm.prompt_builder import PromptBuilder
from src.metrics import MetricsCollector



from src.data.providers.openbb_provider import OpenBBProvider
from src.data.services.data_service import DataService
from src.llm.llm_client import LLMClient
from src.llm.reasoning import ReasoningEngine
from src.agent.stock_agent import StockAgent

logger = setup_logger(__name__)
router = APIRouter()

from src.rag.embedder import EmbeddingModel
from src.rag.faiss_store import FAISSStore
from src.rag.retriever import RAGRetriever
from src.rag.indexer import NewsIndexer
from src.rag.bm25_retriever import BM25Retriever
from src.rag.hybrid_retriever import HybridRetriever
from src.rag.reranker import Reranker
from src.rag.grounding import GroundingService

from src.data.providers.marketaux_provider import MarketauxProvider
from src.data.providers.gnews_provider import GNewsProvider
from src.data.providers.composite_provider import CompositeDataProvider

# Instantiate core business logic dependencies once per application startup
# For complete scalability this could be handled by a formal Dependency Injection container.
openbb_provider = OpenBBProvider()
marketaux_provider = MarketauxProvider()
gnews_provider = GNewsProvider()

composite_provider = CompositeDataProvider(
    primary=openbb_provider,
    news_main=marketaux_provider,
    news_fallback=gnews_provider
)

data_service = DataService(composite_provider)
llm_client = LLMClient()
reasoning_engine = ReasoningEngine(llm_client)

rag_embedder = EmbeddingModel()
rag_store = FAISSStore()
bm25_retriever = BM25Retriever()
hybrid_retriever = HybridRetriever(
    faiss_store=rag_store,
    bm25_retriever=bm25_retriever,
    embedder=rag_embedder
)
reranker = Reranker()
grounding_service = GroundingService()
rag_retriever = RAGRetriever(
    hybrid_retriever=hybrid_retriever,
    reranker=reranker,
    grounding_service=grounding_service
)
news_indexer = NewsIndexer(faiss_store=rag_store, embedder=rag_embedder)

agent = StockAgent(
    data_service=data_service, 
    reasoning_engine=reasoning_engine,
    rag_retriever=rag_retriever,
    news_indexer=news_indexer

)


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_stocks(request: SuggestRequest) -> Any:
    """
    Analyzes multiple stocks to determine the optimal financial action.
    """
    if not request.symbols:
        raise HTTPException(status_code=400, detail="The 'symbols' list cannot be empty.")

    logger.info("API | Received /suggest request for targets: %s", request.symbols)

    try:
        # Run orchestrated pipeline
        results = await agent.analyze_stocks(request.symbols, lookback_days=request.lookback_days)
        
        # Format response correctly into Pydantic models structure
        output = SuggestResponse(
            suggestions=[
                SuggestionItem(
                    symbol=item["symbol"],
                    score=item["score"],
                    decision=item["decision"],
                    reason=item["reason"],
                    signal_breakdown=item.get("signal_breakdown"),
                    rag=item.get("rag"),
                    prediction=item.get("prediction")
                ) for item in results["suggestions"]
            ]
        )
        return output

    except Exception as e:
        logger.error("API | Fatal internal server error during /suggest: %s", e)
        raise HTTPException(status_code=500, detail="An internal server error occurred while processing the request.")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_query(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Runs user query driven stock analysis pipeline.
    """
    import json
    logger.info("API | Received /analyze request for symbol: %s, query: '%s'", request.symbol, request.query)
    
    metrics = MetricsCollector()
    metrics.start_stage("total")
    
    try:
        # Retrieve context from RAG layer using the user's custom query and top_k
        citation_context = await rag_retriever.retrieve(
            symbol=request.symbol.upper(),
            db_session=db,
            query=request.query,
            top_k=request.top_k,
            metrics=metrics
        )
        
        grounding_decision = citation_context.grounding
        is_grounded = grounding_decision.is_grounded if grounding_decision else False
        confidence_score = grounding_decision.confidence_score if grounding_decision else 0.0
        
        # Ensure grounded status is set on the metrics object
        metrics.set_grounded(is_grounded)
        
        # Build diagnostics dictionary
        diagnostics = {
            "query": request.query,
            "symbol": request.symbol,
            "top_k": request.top_k,
            "grounding_reason": grounding_decision.reason if grounding_decision else "No grounding decision"
        }
        
        if not is_grounded:
            refusal_reason = grounding_decision.reason if grounding_decision else "Grounding failed."
            metrics.end_stage("total")
            symbol_metrics = metrics.get_metrics()
            
            # structured logging
            logger.info(
                "[METRICS] Symbol=%s Total=%.1fms Retrieval=%.1fms Reranker=%.1fms Grounding=%.1fms LLM=0.0ms Grounded=False",
                request.symbol.upper(),
                symbol_metrics.total_duration_ms,
                symbol_metrics.retrieval_duration_ms,
                symbol_metrics.reranker_duration_ms,
                symbol_metrics.grounding_duration_ms
            )
            
            # For ungrounded requests, return a JSON refusal formatted output
            refusal_json = json.dumps({
                "recommendation": "HOLD",
                "confidence": 0.0,
                "reasoning": f"Insufficient evidence available to answer this question reliably. Details: {refusal_reason}",
                "citations": []
            })
            
            return AnalyzeResponse(
                answer=refusal_json,
                grounded=False,
                confidence_score=confidence_score,
                citations=[],
                diagnostics=diagnostics,
                metrics=symbol_metrics
            )
            
        # If grounded, build prompt and call LLM
        metrics.start_stage("prompt_build")
        payload = PromptBuilder.build_recommendation_prompt(
            query=request.query,
            symbol=request.symbol,
            context_text=citation_context.formatted_text
        )
        metrics.end_stage("prompt_build")
        
        metrics.start_stage("llm")
        metrics.set_model_name(llm_client.model_name)
        answer = llm_client.generate_response(
            prompt=payload.user_prompt,
            system=payload.system_prompt,
            format="json"
        )
        metrics.end_stage("llm")
        
        metrics.end_stage("total")
        symbol_metrics = metrics.get_metrics()
        
        # Parse JSON output from the model
        final_citations = citation_context.citations
        try:
            recommendation_data = json.loads(answer)
            confidence_score = float(recommendation_data.get("confidence", confidence_score))
            cited_indices = recommendation_data.get("citations", [])
            filtered_citations = [
                c for c in citation_context.citations
                if c.citation_id in cited_indices
            ]
            if filtered_citations:
                final_citations = filtered_citations
        except Exception as parse_err:
            logger.warning("API | Failed to parse LLM structured response as JSON: %s", parse_err)
            
        # structured logging
        logger.info(
            "[METRICS] Symbol=%s Total=%.1fms Retrieval=%.1fms Reranker=%.1fms Grounding=%.1fms LLM=%.1fms Grounded=True",
            request.symbol.upper(),
            symbol_metrics.total_duration_ms,
            symbol_metrics.retrieval_duration_ms,
            symbol_metrics.reranker_duration_ms,
            symbol_metrics.grounding_duration_ms,
            symbol_metrics.llm_duration_ms
        )
        
        return AnalyzeResponse(
            answer=answer,
            grounded=True,
            confidence_score=confidence_score,
            citations=final_citations,
            diagnostics=diagnostics,
            metrics=symbol_metrics
        )
    except Exception as e:
        logger.error("API | Fatal error in /analyze: %s", e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")



@router.get("/health", response_model=HealthResponse)
async def health_check() -> Any:
    """
    Returns subsystem readiness status based on actual runtime probes.
    """
    overall_level = "healthy"
    
    # 1. Evaluate Database (Async)
    db_status = "healthy"
    try:
        from sqlalchemy import text
        from src.config.database import engine
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("HealthProbe | DB unreachable: %s", e)
        db_status = "unhealthy"
        overall_level = "degraded"

    # 2. Evaluate FAISS Vector Store Status
    try:
        if hasattr(rag_store, 'index') and rag_store.index is not None and rag_store.index.ntotal >= 0:
            index_status = "healthy"
        else:
            index_status = "unhealthy"
            overall_level = "degraded"
    except Exception:
        index_status = "unhealthy"
        overall_level = "degraded"

    # 3. Evaluate LLM / Reasoning Reachability
    llm_status = "healthy"
    try:
        import urllib.request
        # Check if Ollama is responsive
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status != 200:
                llm_status = "unhealthy"
                overall_level = "degraded"
    except Exception:
        llm_status = "unhealthy"
        overall_level = "degraded"

    # If DB is down, consider it unavailable rather than just degraded since we can't persist memory mapping
    if db_status == "unhealthy":
        overall_level = "unavailable"

    return HealthResponse(
        level=overall_level,
        summary="System readiness evaluated dynamically.",
        details="All critical services are operational." if overall_level == "healthy" else "System is experiencing degradation or outages.",
        probe_target="/health",
        checks={
            "api": HealthCheckItem(status="healthy", summary="API responding."),
            "database": HealthCheckItem(status=db_status, summary="DB reachable." if db_status == "healthy" else "DB unreachable."),
            "embedding_layer": HealthCheckItem(
                status="healthy" if rag_embedder else "unhealthy", 
                summary="Embedding model loaded." if rag_embedder else "Model missing.", 
                embedding_model="all-MiniLM-L6-v2", 
                vector_dimension=384
            ),
            "vector_index": HealthCheckItem(
                status=index_status, 
                summary="FAISS index ready." if index_status == "healthy" else "FAISS index unavailable.", 
                index_type="flat_l2", 
                top_k=5
            ),
            "retrieval_pipeline": HealthCheckItem(
                status="healthy" if rag_retriever else "unhealthy", 
                summary="Retriever operational." if rag_retriever else "Retriever offline.", 
                retrieval_strategy="similarity_search"
            ),
            "reasoning": HealthCheckItem(
                status=llm_status, 
                summary="LLM reasoning operational." if llm_status == "healthy" else "LLM offline / unreachable.", 
                prompt_mode="signals+context"
            )
        }
    )


@router.get("/debug/symbol/{symbol}", response_model=SuggestResponse)
async def debug_symbol(symbol: str, lookback_days: int = 90) -> Any:
    """
    QA endpoint for a single symbol providing full Phase 7 output.
    """
    logger.info("API | Received /debug request for target: %s", symbol)
    try:
        results = await agent.analyze_stocks([symbol.upper()], lookback_days=lookback_days)
        
        output = SuggestResponse(
            suggestions=[
                SuggestionItem(
                    symbol=item["symbol"],
                    score=item["score"],
                    decision=item["decision"],
                    reason=item["reason"],
                    signal_breakdown=item.get("signal_breakdown"),
                    rag=item.get("rag"),
                    prediction=item.get("prediction")
                ) for item in results["suggestions"]
            ]
        )
        return output

    except Exception as e:
        logger.error("API | Fatal internal server error during /debug: %s", e)
        raise HTTPException(status_code=500, detail="An internal server error occurred while processing the debug request.")


from src.api.routes.debug import router as debug_router
router.include_router(debug_router)
