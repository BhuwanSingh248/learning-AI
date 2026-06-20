import pytest
from unittest.mock import MagicMock

from src.history.models import HistoricalEvent, HistoricalMatch
from src.history.event_store import EventStore
from src.history.event_retriever import EventRetriever
from src.history.outcome_analyzer import OutcomeAnalyzer
from src.rag.embedder import EmbeddingModel
from src.reasoning.reasoning_engine import ReasoningEngine
from src.reasoning.models import RecommendationType
from src.signals.models import SignalType

@pytest.fixture
def embedder():
    return EmbeddingModel()

@pytest.fixture
def event_store(embedder):
    return EventStore(embedder)

@pytest.fixture
def event_retriever(event_store):
    return EventRetriever(event_store)

@pytest.fixture
def outcome_analyzer():
    return OutcomeAnalyzer()

def test_event_store_loading(event_store):
    """Verify historical events JSON is parsed and loaded into store."""
    assert len(event_store.events) >= 5
    titles = [e.title for e in event_store.events]
    assert "US-China Trade War" in titles
    assert "COVID-19 Pandemic Crash" in titles

def test_event_store_semantic_search(event_store):
    """Verify semantic search retrieves Trade War event on tariff query."""
    # Query with "tariff hikes"
    results = event_store.search_similar_events("tariff hikes and trade duties", top_k=1)
    assert len(results) == 1
    matched_event, similarity = results[0]
    assert matched_event.title == "US-China Trade War"
    assert similarity > 0.4

def test_outcome_analyzer_matching_stock(outcome_analyzer, event_store):
    """Verify OutcomeAnalyzer retrieves stock-specific outcome when available."""
    trade_war_event = [e for e in event_store.events if e.event_id == "us_china_trade_war_2018"][0]
    # INFY is explicitly in Trade War stock_outcomes with return_30d = -0.05
    outcome_str = outcome_analyzer.analyze_outcome(trade_war_event, "INFY")
    assert outcome_str == "INFY stock fell 5%"

def test_outcome_analyzer_sector_fallback(outcome_analyzer, event_store):
    """Verify OutcomeAnalyzer falls back to sector outcomes when symbol has no match."""
    trade_war_event = [e for e in event_store.events if e.event_id == "us_china_trade_war_2018"][0]
    # "TESTTICKER" should map to Manufacturing (default) and find -0.08 return
    outcome_str = outcome_analyzer.analyze_outcome(trade_war_event, "TESTTICKER")
    assert outcome_str == "Manufacturing stocks fell 8%"

def test_reasoning_engine_historical_signals(embedder, event_retriever, outcome_analyzer):
    """Verify ReasoningEngine integrates historical signals and maps matches in final response."""
    mock_llm_client = MagicMock()
    mock_llm_client.model_name = "test-model"
    # Mock LLM to return empty signals, reasoning
    mock_llm_client.generate_response.return_value = '{"signals": [], "reasoning": "Standard LLM reasoning."}'
    
    engine = ReasoningEngine(mock_llm_client, event_retriever, outcome_analyzer)
    
    # Run decision with tariff query -> US-China Trade War similarity match
    response = engine.make_decision(
        symbol="INFY",
        query="US tariff announcements and trade import taxes",
        context_text="Tariff news context.",
        is_grounded=True,
        available_citation_ids=[1]
    )
    
    # Assert historical match exists
    assert len(response.historical_matches) == 1
    match = response.historical_matches[0]
    assert match.event == "US-China Trade War"
    assert match.similarity > 0.4
    assert match.observed_outcome == "INFY stock fell 5%"
    
    # Assert a historical signal was generated and merged
    assert len(response.signals) == 1
    sig = response.signals[0]
    assert "Historical Match" in sig.title
    assert sig.signal_type == SignalType.NEGATIVE
    # score = -0.8 * similarity (will be negative, around -0.4 to -0.8)
    assert sig.score < 0.0
