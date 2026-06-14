import pytest
import numpy as np
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

from fastapi.testclient import TestClient
from main import app

from src.rag.retriever import RAGRetriever
from src.rag.hybrid_retriever import HybridRetriever
from src.rag.bm25_retriever import BM25Retriever
from src.rag.reranker import Reranker
from src.rag.grounding import GroundingService
from src.rag.models import RagNewsMetadata
from src.data.models import Citation, CitationContext, GroundingDecision

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

@pytest.mark.asyncio
async def test_hybrid_retrieval():
    """
    Verify that HybridRetriever merges results from both FAISS (semantic) and BM25 (keyword).
    """
    mock_store = MagicMock()
    mock_embedder = MagicMock()
    mock_embedder.embed_text.return_value = np.zeros(384, dtype=np.float32)
    
    bm25_retriever = BM25Retriever()
    hybrid_retriever = HybridRetriever(
        faiss_store=mock_store,
        bm25_retriever=bm25_retriever,
        embedder=mock_embedder
    )
    
    # 3 mock chunks in DB
    chunk_1 = make_mock_chunk("c1", "TEST", "Apple shares rose on earnings reports", source="Reuters")
    chunk_2 = make_mock_chunk("c2", "TEST", "Apple news updates", source="Bloomberg")
    chunk_3 = make_mock_chunk("c3", "TEST", "Other random info", source="Reuters")
    
    # Mock DB session execution returning these chunks
    mock_db = AsyncMock()
    mock_execute_res = MagicMock()
    mock_execute_res.scalars.return_value.all.return_value = [chunk_1, chunk_2, chunk_3]
    mock_db.execute.return_value = mock_execute_res
    
    # Mock FAISS store search returning c1 and c2
    mock_store.search = AsyncMock(return_value=[chunk_1, chunk_2])
    
    # Search for "Apple"
    merged = await hybrid_retriever.search("Apple", "TEST", mock_db, top_k=3)
    
    assert len(merged) >= 2
    chunk_ids = {c.chunk_id for c in merged}
    assert "c1" in chunk_ids
    assert "c2" in chunk_ids

@patch("src.rag.reranker.CrossEncoder")
def test_reranker(mock_cross_encoder_cls):
    """
    Verify that Reranker correctly calls Cross-Encoder to rank candidates.
    """
    mock_model = MagicMock()
    mock_model.predict.return_value = [-1.0, 2.5, 0.5]
    mock_cross_encoder_cls.return_value = mock_model
    
    reranker = Reranker()
    chunks = [
        make_mock_chunk("chunk_1", "TEST", "text 1"),
        make_mock_chunk("chunk_2", "TEST", "text 2"),
        make_mock_chunk("chunk_3", "TEST", "text 3"),
    ]
    
    ranked = reranker.rerank("query", chunks, top_k=3)
    
    assert len(ranked) == 3
    # Check that highest score chunk_2 is ranked first, then chunk_3, then chunk_1
    assert ranked[0][0].chunk_id == "chunk_2"
    assert ranked[0][1] == 2.5
    assert ranked[1][0].chunk_id == "chunk_3"
    assert ranked[1][1] == 0.5
    assert ranked[2][0].chunk_id == "chunk_1"
    assert ranked[2][1] == -1.0

def test_grounding_allow():
    """
    Verify that GroundingService passes the query if evidence scores are above thresholds.
    """
    service = GroundingService(
        min_score_threshold=-5.0,
        min_average_threshold=-9.0,
        min_chunks=1
    )
    ranked_chunks = [
        (make_mock_chunk("c1", "TEST", "text1"), -2.0),
        (make_mock_chunk("c2", "TEST", "text2"), -8.0),
        (make_mock_chunk("c3", "TEST", "text3"), -8.0),
    ]
    decision = service.evaluate("query", ranked_chunks)
    assert decision.is_grounded is True
    assert "passed all grounding checks" in decision.reason

def test_grounding_refuse():
    """
    Verify that GroundingService refuses the query if best score is below min_score_threshold.
    """
    service = GroundingService(
        min_score_threshold=-5.0,
        min_average_threshold=-9.0,
        min_chunks=1
    )
    ranked_chunks = [
        (make_mock_chunk("c1", "TEST", "text1"), -6.0),
        (make_mock_chunk("c2", "TEST", "text2"), -8.0),
        (make_mock_chunk("c3", "TEST", "text3"), -8.0),
    ]
    decision = service.evaluate("query", ranked_chunks)
    assert decision.is_grounded is False
    assert "Top reranker score below threshold" in decision.reason

def test_analyze_endpoint():
    """
    Verify successful path of /analyze endpoint (grounding passes and LLM is queried).
    """
    client = TestClient(app)
    
    with patch("src.api.routes.rag_retriever.retrieve") as mock_retrieve, \
         patch("src.api.routes.llm_client.generate_response") as mock_generate:
        
        mock_decision = GroundingDecision(is_grounded=True, reason="Evidence passed", confidence_score=-2.5)
        mock_retrieve.return_value = CitationContext(
            formatted_text="[1] Source: Reuters | Context: Info",
            citations=[
                Citation(citation_id=1, chunk_id="c1", source_id="Reuters", timestamp="2026-06-14", text_preview="Info")
            ],
            grounding=mock_decision
        )
        mock_generate.return_value = "Yes, Infosys is a buy."
        
        response = client.post(
            "/analyze",
            json={"symbol": "INFY", "query": "Should I buy Infosys after recent earnings?", "top_k": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Yes, Infosys is a buy."
        assert data["grounded"] is True
        assert data["confidence_score"] == -2.5
        assert len(data["citations"]) == 1
        assert data["citations"][0]["chunk_id"] == "c1"

def test_refusal_path():
    """
    Verify refusal path of /analyze endpoint (grounding fails, returning refusal without LLM call).
    """
    client = TestClient(app)
    
    with patch("src.api.routes.rag_retriever.retrieve") as mock_retrieve:
        mock_decision = GroundingDecision(is_grounded=False, reason="Top reranker score below threshold", confidence_score=-8.5)
        mock_retrieve.return_value = CitationContext(
            formatted_text="Insufficient evidence available to answer this question reliably.",
            citations=[],
            grounding=mock_decision
        )
        
        response = client.post(
            "/analyze",
            json={"symbol": "INFY", "query": "Will Infosys build a city on Mars?", "top_k": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Insufficient evidence" in data["answer"]
        assert "Top reranker score below threshold" in data["answer"]
        assert data["grounded"] is False
        assert data["confidence_score"] == -8.5
        assert len(data["citations"]) == 0


from src.metrics import MetricsCollector

def test_metrics_collection():
    """
    Verify stateful metrics collection via MetricsCollector.
    """
    metrics = MetricsCollector()
    metrics.start_stage("retrieval")
    import time
    time.sleep(0.005)  # sleep 5ms
    metrics.end_stage("retrieval")
    metrics.set_count("chunks_retrieved", 4)
    metrics.set_grounded(True)
    metrics.set_model_name("phi3:mini")
    
    payload = metrics.get_metrics()
    assert payload.retrieval_duration_ms > 0.0
    assert payload.chunks_retrieved == 4
    assert payload.grounded is True
    assert payload.model_name == "phi3:mini"

def test_api_metrics_returned():
    """
    Verify that /analyze and /debug/analyze endpoints return metrics correctly.
    """
    client = TestClient(app)
    
    with patch("src.api.routes.rag_retriever.retrieve") as mock_retrieve, \
         patch("src.api.routes.llm_client.generate_response") as mock_generate:
        
        mock_decision = GroundingDecision(is_grounded=True, reason="Passed", confidence_score=-1.0)
        mock_retrieve.return_value = CitationContext(
            formatted_text="[1] Context",
            citations=[
                Citation(citation_id=1, chunk_id="c1", source_id="S1", timestamp="2026-06-14", text_preview="Ctx")
            ],
            grounding=mock_decision
        )
        mock_generate.return_value = "Answer"
        
        # Test /analyze public endpoint
        response = client.post(
            "/analyze",
            json={"symbol": "INFY", "query": "Should I buy?", "top_k": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert data["metrics"]["retrieval_duration_ms"] is not None
        assert data["metrics"]["grounded"] is True
        
        # Test /debug/analyze endpoint
        debug_response = client.post(
            "/debug/analyze",
            json={"symbol": "INFY", "query": "Should I buy?", "top_k": 5}
        )
        assert debug_response.status_code == 200
        debug_data = debug_response.json()
        assert "metrics" in debug_data
        assert debug_data["metrics"]["retrieval_duration_ms"] is not None

