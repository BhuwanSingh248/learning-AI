import os
import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from datetime import datetime, timezone

from main import app
from src.signals.models import SignalType
from src.reasoning.models import RecommendationType
from src.config.database import get_db
from src.rag.models import RagNewsMetadata

def load_test_queries():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, "test_queries.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

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

# Parameterize over the 20 test query scenarios
@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", load_test_queries())
async def test_analyze_pipeline_e2e(scenario):
    """
    Executes end-to-end integration tests over various query categories (strong, weak, neutral, failure).
    Ensures correct grounding REFUSE/ALLOW paths, structured formatting, and metrics population.
    """
    symbol = scenario["symbol"]
    query = scenario["query"]
    category = scenario["category"]
    expected_grounded = scenario["expected_grounded"]
    
    # 1. Setup mock database return chunks based on symbol and query
    mock_chunks = []
    if symbol and symbol.upper() in ["INFY", "AAPL"] and expected_grounded:
        # We construct mock chunks containing query text to pass grounding evaluation
        mock_chunks = [
            make_mock_chunk(f"{symbol}_chunk_1", symbol, f"Recent developments for {symbol}: {query}"),
            make_mock_chunk(f"{symbol}_chunk_2", symbol, f"Key business info of {symbol} related to {query}")
        ]
        
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_chunks
    mock_db.execute.return_value = mock_result
    
    async def override_get_db():
        yield mock_db
        
    app.dependency_overrides[get_db] = override_get_db
    
    # 2. Mock LLM to return standard structured signal response for allowed path.
    # We return 3 positive signals so that total score >= 2.0 (yielding BUY recommendation),
    # even if any historical risk signals are blended in.
    mock_llm_json = (
        '{"signals": ['
        '  {"signal_type": "POSITIVE", "title": "Strong Earnings", "description": "Earnings expansion", "citation_ids": [1]},'
        '  {"signal_type": "POSITIVE", "title": "New Government Contract", "description": "Contracts growth", "citation_ids": [1]},'
        '  {"signal_type": "POSITIVE", "title": "Product Launch", "description": "Successful rollout", "citation_ids": [1]}'
        '], "reasoning": "A similar event occurred previously and negatively impacted export-focused companies."}'
    )
    
    with patch("src.api.routes.llm_client.generate_response", return_value=mock_llm_json) as mock_gen, \
         patch("src.rag.faiss_store.FAISSStore.search", new_callable=AsyncMock) as mock_faiss_search:
         
        mock_faiss_search.return_value = mock_chunks
        
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/analyze",
                    json={"symbol": symbol, "query": query, "top_k": 5}
                )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify schema keys
            assert "recommendation" in data
            assert "confidence" in data
            assert "reasoning" in data
            assert "grounded" in data
            assert "citations" in data
            assert "signals" in data
            assert "metrics" in data
            
            # Check answer field does not exist (cleaned up)
            assert "answer" not in data
            
            if expected_grounded and category != "failure":
                # Grounded ALLOW path validation
                assert data["grounded"] is True
                assert data["recommendation"] == RecommendationType.BUY
                assert 0.0 <= data["confidence"] <= 1.0
                assert len(data["signals"]) >= 2
                
                # Verify citations mapping
                for cit in data["citations"]:
                    assert "chunk_id" in cit
                    assert "source_id" in cit
                    
                # Verify metrics are fully populated
                metrics = data["metrics"]
                assert metrics["total_duration_ms"] > 0
                assert metrics["retrieval_duration_ms"] > 0
                assert metrics["reranker_duration_ms"] > 0
                assert metrics["grounding_duration_ms"] > 0
                assert metrics["llm_duration_ms"] > 0
                assert metrics["grounded"] is True
                
            else:
                # Grounded REFUSE or failure path validation (Graceful degradation)
                assert data["grounded"] is False
                assert data["recommendation"] == RecommendationType.INSUFFICIENT_DATA
                assert data["confidence"] == 0.0
                assert len(data["signals"]) == 0
                assert len(data["citations"]) == 0
                
                # Verify LLM was bypassed (generate_response not called)
                mock_gen.assert_not_called()
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_debug_analyze_pipeline_e2e():
    """
    Verifies that the /debug/analyze endpoint returns proper prompt logs, recommendation data, and metrics.
    """
    mock_chunks = [
        make_mock_chunk("INFY_chunk_1", "INFY", "Recent developments for INFY: Should I buy Infosys after recent earnings?"),
        make_mock_chunk("INFY_chunk_2", "INFY", "Key business info of INFY related to earnings")
    ]
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_chunks
    mock_db.execute.return_value = mock_result
    
    async def override_get_db():
        yield mock_db
        
    app.dependency_overrides[get_db] = override_get_db
    
    mock_llm_json = (
        '{"signals": ['
        '  {"signal_type": "POSITIVE", "title": "Strong Earnings", "description": "Earnings growth", "citation_ids": [1]}'
        '], "reasoning": "Debug reasoning."}'
    )
    
    with patch("src.api.routes.llm_client.generate_response", return_value=mock_llm_json), \
         patch("src.rag.faiss_store.FAISSStore.search", new_callable=AsyncMock) as mock_faiss_search:
         
        mock_faiss_search.return_value = mock_chunks
        
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/debug/analyze",
                    json={"symbol": "INFY", "query": "Should I buy Infosys after recent earnings?", "top_k": 5}
                )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "prompt" in data
            assert "recommendation" in data
            assert "metrics" in data
            
            rec = data["recommendation"]
            assert rec["recommendation"] == RecommendationType.HOLD  # 1 positive signal (score = 1.0) maps to HOLD
            assert 0.0 <= rec["confidence"] <= 1.0
            assert len(rec["signals"]) >= 1
        finally:
            app.dependency_overrides.clear()
