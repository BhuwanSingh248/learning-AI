"""
API Routing Module

Defines the FastAPI routes exposing the underlying orchestrated StockAgent 
to HTTP requests securely.
"""

from fastapi import APIRouter, HTTPException
from typing import Any

from src.config.logger import setup_logger
from src.api.schemas import SuggestRequest, SuggestResponse, SuggestionItem

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

# Instantiate core business logic dependencies once per application startup
# For complete scalability this could be handled by a formal Dependency Injection container.
provider = OpenBBProvider()
data_service = DataService(provider)
llm_client = LLMClient()
reasoning_engine = ReasoningEngine(llm_client)

rag_embedder = EmbeddingModel()
rag_store = FAISSStore()
rag_retriever = RAGRetriever(store=rag_store, embedder=rag_embedder)

agent = StockAgent(
    data_service=data_service, 
    reasoning_engine=reasoning_engine,
    rag_retriever=rag_retriever
)


@router.post("/suggest", response_model=SuggestResponse)
def suggest_stocks(request: SuggestRequest) -> Any:
    """
    Analyzes multiple stocks to determine the optimal financial action.
    """
    if not request.symbols:
        raise HTTPException(status_code=400, detail="The 'symbols' list cannot be empty.")

    logger.info("API | Received /suggest request for targets: %s", request.symbols)

    try:
        # Run orchestrated pipeline
        results = agent.analyze_stocks(request.symbols, lookback_days=request.lookback_days)
        
        # Format response correctly into Pydantic models structure
        output = SuggestResponse(
            suggestions=[
                SuggestionItem(
                    symbol=item["symbol"],
                    score=item["score"],
                    decision=item["decision"],
                    reason=item["reason"]
                ) for item in results["suggestions"]
            ]
        )
        return output

    except Exception as e:
        logger.error("API | Fatal internal server error during /suggest: %s", e)
        raise HTTPException(status_code=500, detail="An internal server error occurred while processing the request.")
