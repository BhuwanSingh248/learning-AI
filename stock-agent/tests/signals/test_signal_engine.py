import pytest

from src.signals.models import Signal, SignalType
from src.signals.signal_engine import SignalEngine
from src.signals.scoring import SignalScorer, RecommendationCalculator, ConfidenceCalculator
from src.reasoning.models import RecommendationType

def test_signal_extraction_parsing():
    """Verify SignalEngine extracts signals correctly and filters citations."""
    raw_response = """
    {
      "signals": [
        {
          "signal_type": "POSITIVE",
          "title": "Strong Earnings",
          "description": "Earnings beat by 15%",
          "citation_ids": [1, 99]
        },
        {
          "signal_type": "RISK",
          "title": "Supply Chain Issues",
          "description": "Logistics delays reported",
          "citation_ids": [2]
        },
        {
          "signal_type": "INVALID_TYPE",
          "title": "Invalid Signal",
          "description": "Should fallback to MARKET",
          "citation_ids": [3]
        }
      ],
      "reasoning": "Context reveals growth with macro risk."
    }
    """
    
    # 99 is not in available_citation_ids, so it should be filtered out
    result = SignalEngine.extract_signals(raw_response, available_citation_ids=[1, 2, 3])
    
    assert len(result.signals) == 3
    assert result.reasoning == "Context reveals growth with macro risk."
    
    # Verify strong earnings
    assert result.signals[0].signal_type == SignalType.POSITIVE
    assert result.signals[0].title == "Strong Earnings"
    assert result.signals[0].citation_ids == [1]  # 99 filtered out
    
    # Verify supply chain
    assert result.signals[1].signal_type == SignalType.RISK
    assert result.signals[1].citation_ids == [2]
    
    # Verify fallback to MARKET
    assert result.signals[2].signal_type == SignalType.MARKET
    assert result.signals[2].citation_ids == [3]

def test_signal_extraction_decode_error():
    """Verify JSON decode error fallback logic."""
    raw_response = "Not JSON output"
    result = SignalEngine.extract_signals(raw_response, available_citation_ids=[1])
    
    assert len(result.signals) == 0
    assert "Parsing signals failed" in result.reasoning

def test_signal_scoring():
    """Verify SignalScorer assigns correct system weights."""
    signals = [
        Signal(signal_type=SignalType.POSITIVE, title="P", description="d", citation_ids=[]),
        Signal(signal_type=SignalType.NEGATIVE, title="N", description="d", citation_ids=[]),
        Signal(signal_type=SignalType.RISK, title="R", description="d", citation_ids=[]),
        Signal(signal_type=SignalType.MARKET, title="M", description="d", citation_ids=[])
    ]
    
    scored = SignalScorer.score_signals(signals)
    
    assert scored[0].score == 1.0
    assert scored[1].score == -1.0
    assert scored[2].score == -0.5
    assert scored[3].score == 0.0

def test_recommendation_thresholds():
    """Verify recommendation thresholds mapping (>= 2.0 -> BUY, <= -1.0 -> SELL, else -> HOLD)."""
    # 1. Test BUY path (score = 2.0)
    signals_buy = [
        Signal(signal_type=SignalType.POSITIVE, title="P1", description="d", score=1.0, citation_ids=[]),
        Signal(signal_type=SignalType.POSITIVE, title="P2", description="d", score=1.0, citation_ids=[])
    ]
    assert RecommendationCalculator.calculate_recommendation(signals_buy) == RecommendationType.BUY
    
    # 2. Test SELL path (score = -1.0)
    signals_sell = [
        Signal(signal_type=SignalType.NEGATIVE, title="N1", description="d", score=-1.0, citation_ids=[])
    ]
    assert RecommendationCalculator.calculate_recommendation(signals_sell) == RecommendationType.SELL
    
    # 3. Test HOLD path (score = 0.5)
    signals_hold = [
        Signal(signal_type=SignalType.POSITIVE, title="P1", description="d", score=1.0, citation_ids=[]),
        Signal(signal_type=SignalType.RISK, title="R1", description="d", score=-0.5, citation_ids=[])
    ]
    assert RecommendationCalculator.calculate_recommendation(signals_hold) == RecommendationType.HOLD

def test_confidence_calculations():
    """Verify confidence formula bounds, consistency penalty, and grounding blending."""
    # 1. Base confidence (2 signals -> 0.7 base conf, no conflict)
    signals_base = [
        Signal(signal_type=SignalType.POSITIVE, title="P1", description="d", citation_ids=[]),
        Signal(signal_type=SignalType.POSITIVE, title="P2", description="d", citation_ids=[])
    ]
    conf = ConfidenceCalculator.calculate_confidence(signals_base)
    # base_conf = min(0.5 + 0.2, 0.7) = 0.7
    assert pytest.approx(conf, 0.01) == 0.7
    
    # 2. Conflict penalty (1 positive, 1 negative -> penalty of 0.2)
    signals_conflict = [
        Signal(signal_type=SignalType.POSITIVE, title="P1", description="d", citation_ids=[]),
        Signal(signal_type=SignalType.NEGATIVE, title="N1", description="d", citation_ids=[])
    ]
    conf_conflict = ConfidenceCalculator.calculate_confidence(signals_conflict)
    # base_conf = min(0.5 + 0.2, 0.7) = 0.7
    # conflict_ratio = 1 / 1 = 1.0 -> penalty = 0.2
    # final_conf = 0.7 - 0.2 = 0.5
    assert pytest.approx(conf_conflict, 0.01) == 0.5
    
    # 3. Grounding confidence blending (80% signal conf, 20% grounding conf)
    # grounding_score = -5.0 -> normalized = (-5 + 10) / 20 = 0.25
    # blended_conf = 0.8 * 0.7 + 0.2 * 0.25 = 0.56 + 0.05 = 0.61
    conf_grounded = ConfidenceCalculator.calculate_confidence(signals_base, grounding_confidence_score=-5.0)
    assert pytest.approx(conf_grounded, 0.01) == 0.61
