import pytest
from unittest.mock import MagicMock

from src.reasoning.reasoning_engine import ReasoningEngine
from src.reasoning.models import RecommendationResponse, RecommendationType
from src.signals.models import SignalType
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
    """Verify system computes BUY when signals sum to >= 2.0."""
    mock_llm_client.generate_response.return_value = (
        '{"signals": ['
        '  {"signal_type": "POSITIVE", "title": "Growth", "description": "Rev up 15%", "citation_ids": [1]},'
        '  {"signal_type": "POSITIVE", "title": "New Contract", "description": "Government deal", "citation_ids": [2]}'
        '], "reasoning": "Strong indicators."}'
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
    assert response.confidence == 0.7  # base 0.7 since 2 signals
    assert response.reasoning == "Strong indicators."
    assert response.citations == [1, 2]
    assert len(response.signals) == 2

def test_make_decision_valid_hold(reasoning_engine, mock_llm_client):
    """Verify system computes HOLD when signals sum to between -1.0 and 2.0."""
    mock_llm_client.generate_response.return_value = (
        '{"signals": ['
        '  {"signal_type": "POSITIVE", "title": "Growth", "description": "Rev up 15%", "citation_ids": [1]},'
        '  {"signal_type": "RISK", "title": "Tariff", "description": "Macro risk", "citation_ids": []}'
        '], "reasoning": "Mixed signals."}'
    )
    
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News context.",
        is_grounded=True,
        available_citation_ids=[1],
    )
    
    assert response.recommendation == RecommendationType.HOLD
    assert response.confidence == 0.7  # base 0.7 (no conflict between POSITIVE and RISK)
    assert response.reasoning == "Mixed signals."
    assert response.signals[0].score == 1.0
    assert response.signals[1].score == -0.5

def test_make_decision_invalid_signal_type_fallback(reasoning_engine, mock_llm_client):
    """Verify invalid signal type falls back to MARKET."""
    mock_llm_client.generate_response.return_value = (
        '{"signals": ['
        '  {"signal_type": "STRONG_BUY", "title": "Growth", "description": "Rev up 15%", "citation_ids": [1]}'
        '], "reasoning": "Fallback reasoning."}'
    )
    
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News context.",
        is_grounded=True,
        available_citation_ids=[1],
    )
    
    assert response.recommendation == RecommendationType.HOLD  # score = 0.0 (MARKET)
    assert response.signals[0].signal_type == SignalType.MARKET

def test_make_decision_invalid_json(reasoning_engine, mock_llm_client):
    """Verify invalid JSON returns fallback reasoning and empty signals."""
    mock_llm_client.generate_response.return_value = "Unstructured text response"
    
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News context.",
        is_grounded=True,
        available_citation_ids=[],
    )
    
    assert response.recommendation == RecommendationType.HOLD
    assert response.confidence == 0.0
    assert "Parsing signals failed" in response.reasoning
    assert len(response.signals) == 0

def test_make_decision_grounding_failure(reasoning_engine, mock_llm_client):
    """Verify grounding refusal path bypasses LLM call and returns early refusal."""
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
    assert len(response.signals) == 0
    
    mock_llm_client.generate_response.assert_not_called()

def test_make_decision_citation_sanitation(reasoning_engine, mock_llm_client):
    """Verify hallucinated citations are stripped out of signals."""
    mock_llm_client.generate_response.return_value = (
        '{"signals": ['
        '  {"signal_type": "NEGATIVE", "title": "Debt", "description": "High debt", "citation_ids": [1, 99]}'
        '], "reasoning": "Sanitation check."}'
    )
    
    response = reasoning_engine.make_decision(
        symbol="AAPL",
        query="Should I buy?",
        context_text="News context.",
        is_grounded=True,
        available_citation_ids=[1, 2],
    )
    
    assert response.citations == [1]
    assert response.signals[0].citation_ids == [1]
