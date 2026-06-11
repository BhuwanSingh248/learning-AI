import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.rag.grounding import GroundingService
from src.rag.retriever import RAGRetriever
from src.rag.models import RagNewsMetadata
from src.data.models import GroundingDecision

def make_mock_chunk(chunk_id: str, text: str) -> RagNewsMetadata:
    chunk = RagNewsMetadata()
    chunk.chunk_id = chunk_id
    chunk.symbol = "TEST"
    chunk.chunk_text = text
    chunk.source_id = "test_source"
    return chunk

class TestGroundingRegression:

    def test_grounding_allows_relevant_queries(self):
        """
        6.4.6 & 6.4.8: Verify that strong, relevant queries with scores matching
        the calibrated range (-5.0 best, -9.0 average) are ALLOWED.
        """
        # Calibrated thresholds
        service = GroundingService(
            min_score_threshold=-5.0,
            min_average_threshold=-9.0,
            min_chunks=1
        )
        
        # Simulating a strong query (e.g. RELIANCE.NS recent context: best -2.0, avg -8.5)
        ranked_chunks_with_scores = [
            (make_mock_chunk("c1", "Reliance reports profit growth"), -2.0),
            (make_mock_chunk("c2", "Reliance expands retail presence"), -8.5),
            (make_mock_chunk("c3", "Reliance stock performance"), -8.8),
        ]
        
        decision = service.evaluate("Recent context and news updates for RELIANCE.NS.", ranked_chunks_with_scores)
        
        assert decision.is_grounded is True
        assert "passed all grounding checks" in decision.reason
        assert decision.confidence_score == -6.433333333333334 # Average of -2.0, -8.5, -8.8

    def test_grounding_refuses_irrelevant_queries(self):
        """
        6.4.7 & 6.4.8: Verify that weak, irrelevant queries with low scores
        (e.g., best below -5.0 or average below -9.0) are REFUSED.
        """
        # Calibrated thresholds
        service = GroundingService(
            min_score_threshold=-5.0,
            min_average_threshold=-9.0,
            min_chunks=1
        )
        
        # Simulating a weak query (e.g., "Will RELIANCE build space elevator?": best -8.5, avg -10.8)
        ranked_chunks_with_scores = [
            (make_mock_chunk("c1", "Reliance reports profit growth"), -8.5),
            (make_mock_chunk("c2", "Reliance expands retail presence"), -10.8),
            (make_mock_chunk("c3", "Reliance stock performance"), -11.2),
        ]
        
        decision = service.evaluate("Will RELIANCE build a space elevator to Mars?", ranked_chunks_with_scores)
        
        assert decision.is_grounded is False
        assert "Top reranker score below threshold" in decision.reason

    def test_grounding_averages_top_3_only(self):
        """
        6.4.3 & 6.4.8: Verify that the grounding quality average is calculated
        strictly over the top 3 chunks, ignoring tail noise.
        """
        # Set min_average to -7.0 (so an overall average of -8.0 would fail, but top-3 avg of -6.0 passes)
        service = GroundingService(
            min_score_threshold=-5.0,
            min_average_threshold=-7.0,
            min_chunks=1
        )
        
        ranked_chunks_with_scores = [
            (make_mock_chunk("c1", "Reliance reports profit growth"), -2.0),
            (make_mock_chunk("c2", "Reliance expands retail presence"), -8.0),
            (make_mock_chunk("c3", "Reliance stock performance"), -8.0),
            (make_mock_chunk("c4", "Some generic stock market text"), -11.0),
            (make_mock_chunk("c5", "Another noisy text"), -11.0),
        ]
        
        decision = service.evaluate("Recent context and news updates for RELIANCE.NS.", ranked_chunks_with_scores)
        
        # Top 3 scores: -2.0, -8.0, -8.0 -> Average: -6.0 >= -7.0 -> ALLOW!
        assert decision.is_grounded is True
        assert decision.confidence_score == -6.0

    @pytest.mark.asyncio
    async def test_rag_retriever_refusal_bypasses_citations(self):
        """
        Verify that when grounding fails, the retrieval pipeline skips citation building.
        """
        mock_hybrid = MagicMock()
        mock_hybrid.search = AsyncMock(return_value=[make_mock_chunk("c1", "text")])
        
        mock_reranker = MagicMock()
        mock_reranker.rerank.return_value = [(make_mock_chunk("c1", "text"), -10.0)]
        
        # Grounding service with standard settings
        grounding_service = GroundingService(
            min_score_threshold=-5.0,
            min_average_threshold=-9.0,
            min_chunks=1
        )
        
        retriever = RAGRetriever(
            hybrid_retriever=mock_hybrid,
            reranker=mock_reranker,
            grounding_service=grounding_service
        )
        
        mock_session = AsyncMock()
        with patch("src.rag.retriever.CitationContextBuilder") as mock_builder:
            res = await retriever.retrieve("Will RELIANCE build space elevator?", mock_session, top_k=5)
            
            # Grounding should fail (-10.0 < -5.0)
            assert res.grounding.is_grounded is False
            # Citation builder should NOT have been called
            mock_builder.build_context.assert_not_called()
            # Formatted context should be empty
            assert res.formatted_context == "Insufficient evidence available to answer this question reliably."
