from typing import List, Optional
from src.signals.models import Signal, SignalType
from src.reasoning.models import RecommendationType

class SignalScorer:
    """
    Assigns deterministic system-side scores to signals based on category.
    """
    @staticmethod
    def score_signals(signals: List[Signal]) -> List[Signal]:
        """
        Assigns explicit deterministic score weights to each signal based on type.
        Preserves pre-calculated scores if they are non-zero.
        """
        for sig in signals:
            if sig.score != 0.0:
                continue
            if sig.signal_type == SignalType.POSITIVE:
                sig.score = 1.0
            elif sig.signal_type == SignalType.NEGATIVE:
                sig.score = -1.0
            elif sig.signal_type == SignalType.RISK:
                sig.score = -0.5
            else:
                sig.score = 0.0
        return signals

class RecommendationCalculator:
    """
    Calculates final stock recommendation based on aggregate signal scores.
    """
    @staticmethod
    def calculate_recommendation(signals: List[Signal]) -> RecommendationType:
        """
        Sums up signal scores and maps to BUY, SELL, or HOLD using thresholds:
        - score >= 2.0 -> BUY
        - score <= -1.0 -> SELL
        - Otherwise -> HOLD
        """
        if not signals:
            return RecommendationType.HOLD
            
        total_score = sum(sig.score for sig in signals)
        
        if total_score >= 2.0:
            return RecommendationType.BUY
        elif total_score <= -1.0:
            return RecommendationType.SELL
        else:
            return RecommendationType.HOLD

class ConfidenceCalculator:
    """
    Computes a robust, deterministic confidence metric based on signal evidence and agreement.
    """
    @staticmethod
    def calculate_confidence(signals: List[Signal], grounding_confidence_score: Optional[float] = None) -> float:
        """
        Computes deterministic confidence score from 0.0 to 1.0 based on signal count,
        consistency (penalizing conflicting positive and negative signals), and grounding quality.
        """
        if not signals:
            return 0.0
            
        # 1. Base confidence from signal count (more evidence yields higher base confidence)
        # 1 signal = 0.5, 2 signals = 0.6, 3+ signals = 0.7
        base_conf = min(0.5 + (len(signals) * 0.1), 0.7)
        
        # 2. Consistency penalty: if conflicting signals are present, penalize confidence
        pos_count = sum(1 for s in signals if s.signal_type == SignalType.POSITIVE)
        neg_count = sum(1 for s in signals if s.signal_type == SignalType.NEGATIVE)
        
        conflict_penalty = 0.0
        if pos_count > 0 and neg_count > 0:
            # Maximum penalty of 0.2 when count is equal (e.g. 2 pos, 2 neg)
            conflict_ratio = min(pos_count, neg_count) / max(pos_count, neg_count)
            conflict_penalty = 0.2 * conflict_ratio
            
        confidence = base_conf - conflict_penalty
        
        # 3. Incorporate grounding confidence score if available
        # Reranker score threshold in GroundingService is generally between -10.0 and 10.0.
        # We normalize this range to [0.0, 1.0] and blend it (80% signal-based, 20% grounding-based).
        if grounding_confidence_score is not None:
            normalized_grounding = max(0.0, min(1.0, (grounding_confidence_score + 10.0) / 20.0))
            confidence = 0.8 * confidence + 0.2 * normalized_grounding
            
        return max(0.0, min(1.0, confidence))
