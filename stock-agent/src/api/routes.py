"""
API Routing Module

Defines the FastAPI routes exposing the underlying orchestrated StockAgent 
to HTTP requests securely.
"""

from fastapi import APIRouter, HTTPException
from typing import Any

from src.config.logger import setup_logger
from src.api.schemas import SuggestRequest, SuggestResponse, SuggestionItem, HealthResponse, HealthCheckItem

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

