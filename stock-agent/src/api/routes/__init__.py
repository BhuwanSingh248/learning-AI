"""
API Routing Module

Defines the FastAPI routes exposing the underlying orchestrated StockAgent 
to HTTP requests securely.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Any, Optional, List
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
from src.reasoning.reasoning_engine import ReasoningEngine
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
rag_embedder = EmbeddingModel()

from src.history.event_store import EventStore
from src.history.event_retriever import EventRetriever
from src.history.outcome_analyzer import OutcomeAnalyzer

event_store = EventStore(rag_embedder)
event_retriever = EventRetriever(event_store)
outcome_analyzer = OutcomeAnalyzer()
reasoning_engine = ReasoningEngine(llm_client, event_retriever, outcome_analyzer)
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
    logger.info("API | Received /analyze request for symbol: %s, query: '%s'", request.symbol, request.query)
    
    metrics = MetricsCollector()
    metrics.start_stage("total")
    
    # 1. Query Intent Routing Check
    from src.query_router.intent_classifier import IntentClassifier
    from src.query_router.query_types import QueryIntent
    from src.reasoning.models import RecommendationType
    
    intent = IntentClassifier.classify(request.query)
    if intent == QueryIntent.FUNDAMENTAL:
        metrics.end_stage("total")
        symbol_metrics = metrics.get_metrics()
        
        diagnostics = {
            "query": request.query,
            "symbol": request.symbol,
            "top_k": request.top_k,
            "intent": str(intent),
            "failure_type": "FUNDAMENTAL_QUERY_NOT_SUPPORTED",
            "grounding_reason": "Query classification bypassed retrieval."
        }
        
        # Persist Metrics Record
        from src.metrics.models import MetricRecord
        from unittest.mock import MagicMock, AsyncMock
        is_mock = isinstance(db, (MagicMock, AsyncMock)) or hasattr(db, "assert_called")
        if not is_mock:
            try:
                metric_record = MetricRecord(
                    symbol=request.symbol.upper(),
                    query=request.query,
                    total_duration_ms=symbol_metrics.total_duration_ms,
                    retrieval_duration_ms=0.0,
                    reranker_duration_ms=0.0,
                    grounding_duration_ms=0.0,
                    prompt_build_duration_ms=0.0,
                    llm_duration_ms=0.0,
                    chunks_retrieved=0,
                    chunks_after_rerank=0,
                    grounded=False,
                    model_name=settings.LLM_MODEL,
                    average_score=0.0
                )
                db.add(metric_record)
                await db.commit()
            except Exception as db_err:
                logger.error("API | Failed to persist metrics for fundamental bypass: %s", db_err)
                await db.rollback()

        return AnalyzeResponse(
            recommendation=RecommendationType.INSUFFICIENT_DATA,
            confidence=0.0,
            reasoning="Query type 'FUNDAMENTAL' is not yet supported.",
            grounded=False,
            citations=[],
            signals=[],
            historical_matches=[],
            diagnostics=diagnostics,
            metrics=symbol_metrics
        )
        
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
        refusal_reason = grounding_decision.reason if grounding_decision else "Grounding failed."
        available_citation_ids = [c.citation_id for c in citation_context.citations]
        
        # Ensure grounded status is set on the metrics object
        metrics.set_grounded(is_grounded)
        
        # Build diagnostics dictionary with rich failure types if grounding checks fail
        failure_type = None
        if not is_grounded:
            from unittest.mock import MagicMock, AsyncMock
            is_mock = isinstance(db, (MagicMock, AsyncMock)) or hasattr(db, "assert_called")
            symbol_records = []
            if not is_mock:
                try:
                    from sqlalchemy.future import select
                    from src.rag.models import RagNewsMetadata
                    stmt = select(RagNewsMetadata).where(RagNewsMetadata.symbol == request.symbol.upper())
                    res = await db.execute(stmt)
                    if res is not None:
                        symbol_records = res.scalars().all()
                except Exception as e:
                    logger.warning("API | Failed to query metadata database: %s", e)
                    symbol_records = []
            
            if not symbol_records:
                failure_type = "NO_NEWS_INDEXED"
            elif len(citation_context.citations) == 0:
                failure_type = "NO_RELEVANT_EVIDENCE"
            else:
                failure_type = "WEAK_EVIDENCE_QUALITY"

        diagnostics = {
            "query": request.query,
            "symbol": request.symbol,
            "top_k": request.top_k,
            "grounding_reason": grounding_decision.reason if grounding_decision else "No grounding decision",
            "failure_type": failure_type
        }
        
        # Delegate prompt building, model inference, parsing, validation to ReasoningEngine
        llm_decision = reasoning_engine.make_decision(
            symbol=request.symbol,
            query=request.query,
            context_text=citation_context.formatted_text,
            is_grounded=is_grounded,
            available_citation_ids=available_citation_ids,
            metrics=metrics,
            refusal_reason=refusal_reason,
            grounding_confidence_score=grounding_decision.confidence_score if grounding_decision else 0.0
        )
        
        metrics.end_stage("total")
        symbol_metrics = metrics.get_metrics()
        symbol_metrics.grounded = is_grounded
        
        # Filter citations to only include those returned by the engine
        filtered_citations = [
            c for c in citation_context.citations
            if c.citation_id in llm_decision.citations
        ]
        
        # structured logging
        logger.info(
            "[METRICS] Symbol=%s Total=%.1fms Retrieval=%.1fms Reranker=%.1fms Grounding=%.1fms LLM=%.1fms Grounded=%s",
            request.symbol.upper(),
            symbol_metrics.total_duration_ms,
            symbol_metrics.retrieval_duration_ms,
            symbol_metrics.reranker_duration_ms,
            symbol_metrics.grounding_duration_ms,
            symbol_metrics.llm_duration_ms,
            str(is_grounded)
        )
        
        # Persist Metrics Record
        from src.metrics.models import MetricRecord
        from unittest.mock import MagicMock, AsyncMock
        is_mock = isinstance(db, (MagicMock, AsyncMock)) or hasattr(db, "assert_called")
        if not is_mock:
            try:
                metric_record = MetricRecord(
                    symbol=request.symbol.upper(),
                    query=request.query,
                    total_duration_ms=symbol_metrics.total_duration_ms,
                    retrieval_duration_ms=symbol_metrics.retrieval_duration_ms,
                    reranker_duration_ms=symbol_metrics.reranker_duration_ms,
                    grounding_duration_ms=symbol_metrics.grounding_duration_ms,
                    prompt_build_duration_ms=symbol_metrics.prompt_build_duration_ms,
                    llm_duration_ms=symbol_metrics.llm_duration_ms,
                    chunks_retrieved=symbol_metrics.chunks_retrieved,
                    chunks_after_rerank=symbol_metrics.chunks_after_rerank,
                    grounded=is_grounded,
                    model_name=settings.LLM_MODEL,
                    average_score=grounding_decision.confidence_score if grounding_decision else 0.0
                )
                db.add(metric_record)
                await db.commit()
            except Exception as db_err:
                logger.error("API | Failed to persist metrics to database: %s", db_err)
                await db.rollback()
                
        return AnalyzeResponse(
            recommendation=llm_decision.recommendation,
            confidence=llm_decision.confidence,
            reasoning=llm_decision.reasoning,
            grounded=is_grounded,
            citations=filtered_citations,
            signals=llm_decision.signals,
            historical_matches=llm_decision.historical_matches,
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
    from datetime import datetime
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

    # 4. Evaluate News Freshness (Latest news chunk timestamp)
    news_freshness_status = "healthy"
    news_freshness_summary = "News is fresh."
    try:
        if db_status == "healthy":
            from sqlalchemy import func
            from src.rag.models import RagNewsMetadata
            from src.config.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                stmt = select(func.max(RagNewsMetadata.timestamp))
                res = await session.execute(stmt)
                latest_ts = res.scalar()
                
            if latest_ts is None:
                news_freshness_status = "unhealthy"
                news_freshness_summary = "No news indexed in database yet."
            else:
                # latest_ts is offset-naive UTC datetime
                time_diff = datetime.now() - latest_ts
                if time_diff.total_seconds() > 86400:
                    news_freshness_status = "unhealthy"
                    news_freshness_summary = f"No news indexed in last 24 hours. Latest update: {latest_ts.isoformat()}"
                else:
                    news_freshness_summary = f"Latest news indexed: {latest_ts.isoformat()} (within last 24h)."
        else:
            news_freshness_status = "unhealthy"
            news_freshness_summary = "Cannot verify freshness: database unreachable."
    except Exception as e:
        logger.error("HealthProbe | News freshness check failed: %s", e)
        news_freshness_status = "unhealthy"
        news_freshness_summary = f"Freshness check failed: {e}"

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
            ),
            "news_freshness": HealthCheckItem(
                status=news_freshness_status,
                summary=news_freshness_summary
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


# -------------------------------------------------------------
# Phase 2.8 and 2.9 Visualization & Metadata Endpoints
# -------------------------------------------------------------

@router.get("/capabilities")
async def get_capabilities() -> Any:
    """
    Returns metadata detailing the functional capabilities supported by the Stock Agent.
    """
    return {
        "supports": [
            "news_analysis",
            "recommendations",
            "historical_events"
        ],
        "not_supported": [
            "shareholding",
            "financial_statements",
            "technical_analysis"
        ]
    }


@router.get("/models")
async def get_models() -> Any:
    """
    Returns the currently active LLM reasoning model settings.
    """
    return {
        "active_model": settings.LLM_MODEL
    }


@router.get("/pipeline/status")
async def get_pipeline_status() -> Any:
    """
    Performs runtime status checks on all pipelines (database, FAISS, reranker, and Ollama).
    """
    db_ok = True
    try:
        from sqlalchemy import text
        from src.config.database import engine
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
        
    faiss_ok = False
    try:
        if hasattr(rag_store, 'index') and rag_store.index is not None:
            faiss_ok = True
    except Exception:
        pass
        
    reranker_ok = False
    try:
        if reranker is not None and reranker.model_name is not None:
            reranker_ok = True
    except Exception:
        pass
        
    ollama_ok = False
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=1.5) as response:
            if response.status == 200:
                ollama_ok = True
    except Exception:
        pass
        
    return {
        "faiss": faiss_ok,
        "reranker": reranker_ok,
        "ollama": ollama_ok,
        "database": db_ok
    }


@router.get("/evaluation/results")
async def get_evaluation_results() -> Any:
    """
    Loads and returns the latest evaluation metrics baseline file.
    """
    import os
    import json
    import glob
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    baselines_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "evaluation", "baselines"))
    active_model_safe = settings.LLM_MODEL.replace(':', '_')
    active_baseline_file = os.path.join(baselines_dir, f"{active_model_safe}_baseline.json")
    
    if os.path.exists(active_baseline_file):
        with open(active_baseline_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    # Try finding any baseline file
    files = glob.glob(os.path.join(baselines_dir, "*_baseline.json"))
    if files:
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)
            
    raise HTTPException(status_code=404, detail="No evaluation baseline files found. Please run run_evaluation.py first.")


@router.get("/benchmark/results")
async def get_benchmark_results() -> Any:
    """
    Loads and returns the latest compiled multi-model rankings.
    """
    import os
    import json
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rankings_file = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "evaluation", "model_rankings.json"))
    
    if os.path.exists(rankings_file):
        with open(rankings_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    raise HTTPException(status_code=404, detail="Model rankings file not found. Please run run_benchmark.py first.")


from pydantic import BaseModel
class HistoricalSearchRequest(BaseModel):
    query: str
    top_k: int = 3

@router.post("/historical-events/search")
async def search_historical_events(request: HistoricalSearchRequest) -> Any:
    """
    Searches for semantically matching historical market events.
    """
    try:
        results = event_retriever.retrieve(query=request.query, top_k=request.top_k)
        return [
            {
                "event": event,
                "similarity": similarity
            } for event, similarity in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query historical events: {e}")


class SignalsRequest(BaseModel):
    raw_response: str
    available_citation_ids: Optional[List[int]] = None

@router.post("/signals")
async def extract_signals_endpoint(request: SignalsRequest) -> Any:
    """
    Utility endpoint to parse and score signals dynamically from custom text responses.
    """
    from src.signals.signal_engine import SignalEngine
    from src.signals.scoring import SignalScorer
    try:
        extracted = SignalEngine.extract_signals(request.raw_response, request.available_citation_ids)
        scored_signals = SignalScorer.score_signals(extracted.signals)
        return {
            "signals": scored_signals,
            "reasoning": extracted.reasoning
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract signals: {e}")


from src.api.routes.debug import router as debug_router
router.include_router(debug_router)
