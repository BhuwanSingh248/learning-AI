import pytest
from unittest.mock import MagicMock, patch

from src.reasoning.reasoning_engine import ReasoningEngine
from src.reasoning.models import RecommendationResponse, RecommendationType
from src.metrics.service import MetricsCollector

@pytest.fixture
def mock_llm_client():
    client = MagicMock()
    client.model_name = "test-model"
    return client

@pytest.fixture
def reasoning_engine(mock_llm_client):
    return ReasoningEngine(mock_llm_client)

def test_make_decision_valid_buy(reasoning_engine, mock_llm_client):
    """Verify standard valid BUY JSON response from LLM."""
    mock_llm_client.generate_response.return_value = (
        '{"recommendation": "BUY", "confidence": 0.85, "reasoning": "Strong indicators.", "citations": [1, 2]}'
    )
    
    metrics = MetricsCollector()
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="[1] News context. [2] News context.",
        is_grounded=True,
        available_citation_ids=[1, 2, 3],
        metrics=metrics
    )
    
    assert response.recommendation == RecommendationType.BUY
    assert response.confidence == 0.85
    assert response.reasoning == "Strong indicators."
    assert response.citations == [1, 2]

def test_make_decision_valid_hold(reasoning_engine, mock_llm_client):
    """Verify standard valid HOLD JSON response from LLM."""
    mock_llm_client.generate_response.return_value = (
        '{"recommendation": "HOLD", "confidence": 0.5, "reasoning": "Mixed signals.", "citations": []}'
    )
    
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News context.",
        is_grounded=True,
        available_citation_ids=[],
    )
    
    assert response.recommendation == RecommendationType.HOLD
    assert response.confidence == 0.5
    assert response.reasoning == "Mixed signals."
    assert response.citations == []

def test_make_decision_invalid_recommendation_fallback(reasoning_engine, mock_llm_client):
    """Verify invalid recommendation defaults to INSUFFICIENT_DATA."""
    mock_llm_client.generate_response.return_value = (
        '{"recommendation": "STRONG_BUY", "confidence": 0.9, "reasoning": "Invalid type.", "citations": []}'
    )
    
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News context.",
        is_grounded=True,
        available_citation_ids=[],
    )
    
    assert response.recommendation == RecommendationType.INSUFFICIENT_DATA
    assert response.confidence == 0.9
    assert response.reasoning == "Invalid type."

def test_make_decision_invalid_json(reasoning_engine, mock_llm_client):
    """Verify invalid JSON returns the parsing fallback response."""
    mock_llm_client.generate_response.return_value = "Unstructured text response"
    
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News context.",
        is_grounded=True,
        available_citation_ids=[],
    )
    
    assert response.recommendation == RecommendationType.INSUFFICIENT_DATA
    assert response.confidence == 0.0
    assert "Unable to parse model response" in response.reasoning

def test_make_decision_grounding_failure(reasoning_engine, mock_llm_client):
    """Verify grounding refusal path bypasses LLM call and returns fallback."""
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="No news.",
        is_grounded=False,
        available_citation_ids=[],
        refusal_reason="Reranker score below threshold"
    )
    
    assert response.recommendation == RecommendationType.INSUFFICIENT_DATA
    assert response.confidence == 0.0
    assert "Grounding failed" in response.reasoning
    assert "Reranker score below threshold" in response.reasoning
    assert response.citations == []
    
    mock_llm_client.generate_response.assert_not_called()

def test_make_decision_citation_sanitation(reasoning_engine, mock_llm_client):
    """Verify hallucinated citations are stripped out."""
    mock_llm_client.generate_response.return_value = (
        '{"recommendation": "SELL", "confidence": 0.99, "reasoning": "High risk.", "citations": [1, 99]}'
    )
    
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News context.",
        is_grounded=True,
        available_citation_ids=[1, 2],
    )
    
    assert response.recommendation == RecommendationType.SELL
    assert response.confidence == 0.99
    assert response.citations == [1]  # 99 is filtered out since it's not in available_citation_ids

def test_make_decision_confidence_clamping(reasoning_engine, mock_llm_client):
    """Verify confidence score is clamped within [0.0, 1.0]."""
    # Test confidence > 1.0
    mock_llm_client.generate_response.return_value = (
        '{"recommendation": "BUY", "confidence": 1.5, "reasoning": "Overconfident.", "citations": []}'
    )
    response_high = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News.",
        is_grounded=True,
    )
    assert response_high.confidence == 1.0
    
    # Test confidence < 0.0
    mock_llm_client.generate_response.return_value = (
        '{"recommendation": "BUY", "confidence": -0.5, "reasoning": "Underconfident.", "citations": []}'
    )
    response_low = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News.",
        is_grounded=True,
    )
    assert response_low.confidence == 0.0
