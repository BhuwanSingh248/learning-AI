import pytest
import numpy as np
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

from src.rag.retriever import RAGRetriever
from src.rag.hybrid_retriever import HybridRetriever
from src.rag.bm25_retriever import BM25Retriever
from src.rag.reranker import Reranker
from src.rag.grounding import GroundingService
from src.rag.models import RagNewsMetadata
from src.data.services.data_service import DataService
from src.llm.reasoning import ReasoningEngine, LLMDecision
from src.agent.stock_agent import StockAgent
from src.data.models.price import PriceBar
from src.data.models.news import NewsItem
from src.data.models.corporate_actions import CorporateAction


# Helper to construct database metadata records
def make_mock_chunk(chunk_id: str, symbol: str, text: str, source: str = "Reuters") -> RagNewsMetadata:
    chunk = RagNewsMetadata()
    chunk.id = hash(chunk_id) % 100000
    chunk.chunk_id = chunk_id
    chunk.symbol = symbol
    chunk.chunk_text = text
    chunk.source_id = source
    chunk.chunk_index = 0
    chunk.timestamp = datetime.now(timezone.utc)
    return chunk


class TestRAGEndToEnd:

    @pytest.fixture
    def mock_db_session(self):
        return AsyncMock()

    @pytest.fixture
    def setup_rag_pipeline(self):
        """Sets up real RAG components with mock embedding and FAISS store backends."""
        mock_store = MagicMock()
        # Mock vector search to return matching list of records
        mock_store.search = AsyncMock()

        mock_embedder = MagicMock()
        mock_embedder.embed_text = MagicMock(return_value=np.zeros(384, dtype=np.float32))

        bm25_retriever = BM25Retriever()
        hybrid_retriever = HybridRetriever(
            faiss_store=mock_store,
            bm25_retriever=bm25_retriever,
            embedder=mock_embedder
        )
        # Reranker uses the local lightweight cross-encoder model
        reranker = Reranker()
        
        # Grounding checks: require >= 1 chunks, and best score >= -10.0, average score >= -10.0
        grounding_service = GroundingService(
            min_score_threshold=-10.0,
            min_chunks=1,
            min_average_threshold=-10.0
        )

        retriever = RAGRetriever(
            hybrid_retriever=hybrid_retriever,
            reranker=reranker,
            grounding_service=grounding_service
        )

        return retriever, mock_store

    @pytest.fixture
    def setup_stock_agent(self, setup_rag_pipeline):
        """Prepares a StockAgent with mock data service and reasoning engines."""
        retriever, mock_store = setup_rag_pipeline

        mock_data_service = MagicMock()
        mock_data_service.get_price_data.return_value = [
            PriceBar(open=150.0, high=155.0, low=149.0, close=153.0, volume=1000000, date=datetime.now(timezone.utc).date())
        ]
        mock_data_service.get_news.return_value = []
        mock_data_service.get_corporate_actions.return_value = []

        mock_reasoning_engine = MagicMock()
        mock_reasoning_engine.make_decision.return_value = LLMDecision(
            symbol="AAPL",
            decision="Bullish",
            reason="Market indicators are positive and news matches momentum."
        )

        agent = StockAgent(
            data_service=mock_data_service,
            reasoning_engine=mock_reasoning_engine,
            rag_retriever=retriever
        )

        return agent, mock_store, mock_reasoning_engine

    @pytest.mark.asyncio
    @patch("src.agent.stock_agent.AsyncSessionLocal")
    async def test_case_1_grounding_refusal_path(self, mock_session_cls, setup_stock_agent):
        """Test Case 1: Insufficient chunks in the database triggers early refusal."""
        agent, mock_store, mock_reasoning_engine = setup_stock_agent

        # 1. Setup DB session mocks
        mock_session = AsyncMock()
        mock_session_cls.return_value = mock_session
        mock_session.__aenter__.return_value = mock_session
        
        # Database query returns 0 candidates for the EMPTYTICKER symbol
        mock_execute_result = MagicMock()
        mock_execute_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_execute_result

        # 2. Run analysis
        result = await agent.analyze_stocks(["EMPTYTICKER"], lookback_days=90)
        
        # 3. Verifications
        assert len(result["suggestions"]) == 1
        suggestion = result["suggestions"][0]
        
        assert suggestion["symbol"] == "EMPTYTICKER"
        assert suggestion["decision"] == "Neutral"
        # Verify that the reason text explains the grounding failure
        assert "Insufficient evidence available to answer this question reliably." in suggestion["reason"]
        assert "required >= 1" in suggestion["reason"]
        
        # Verify LLM was bypassed (make_decision should not be called)
        mock_reasoning_engine.make_decision.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.agent.stock_agent.AsyncSessionLocal")
    async def test_case_2_grounding_allow_path(self, mock_session_cls, setup_stock_agent):
        """Test Case 2: High quality matches pass checks and call the LLM."""
        agent, mock_store, mock_reasoning_engine = setup_stock_agent

        # 1. Setup DB session mocks
        mock_session = AsyncMock()
        mock_session_cls.return_value = mock_session
        mock_session.__aenter__.return_value = mock_session
        
        # Prepare two candidate records for AAPL stock
        chunk_1 = make_mock_chunk("AAPL_chunk_1", "AAPL", "Apple reports records sales numbers and launches AI tools.")
        chunk_2 = make_mock_chunk("AAPL_chunk_2", "AAPL", "AAPL stock hits all time high on solid earnings growth.")
        
        mock_execute_result = MagicMock()
        mock_execute_result.scalars.return_value.all.return_value = [chunk_1, chunk_2]
        mock_session.execute.return_value = mock_execute_result

        # Mock FAISS store search returns chunks
        mock_store.search.return_value = [chunk_1, chunk_2]

        # 2. Run analysis
        result = await agent.analyze_stocks(["AAPL"], lookback_days=90)

        # 3. Verifications
        assert len(result["suggestions"]) == 1
        suggestion = result["suggestions"][0]

        assert suggestion["symbol"] == "AAPL"
        assert suggestion["decision"] == "Bullish"
        assert suggestion["reason"] == "Market indicators are positive and news matches momentum."
        
        # Verify LLM was invoked
        mock_reasoning_engine.make_decision.assert_called_once()
