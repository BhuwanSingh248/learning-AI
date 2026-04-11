"""
Corporate Actions Feature Engineering Layer

Derives an aggregate event impact score based on corporate events
such as dividends, earnings reports, and stock splits.
"""

from typing import List

from src.analysis.signals import EventSignals
from src.data.models.corporate_actions import CorporateAction, ActionType
from src.config.logger import setup_logger

logger = setup_logger(__name__)


class EventAnalyzer:
    """
    Analyzes corporate actions to compute a quantifiable impact score.
    """

    @staticmethod
    def analyze(actions: List[CorporateAction]) -> EventSignals:
        """
        Derives an aggregated event score from corporate actions.
        
        Simple rules:
        - Dividends are generally seen as positive (+0.5 base).
        - Stock Splits are often seen as positive retail indicators (+0.5 base).
        - Earnings beats (positive values) add slight positives (+1.0), misses negative.
        
        Args:
            actions: Cleaned list of CorporateAction objects.
            
        Returns:
            An EventSignals dataclass with an event_score bounded arbitrarily (e.g. -1 to 1).
        """
        if not actions:
            logger.debug("EventAnalyzer | No actions provided. Returning neutral score.")
            return EventSignals(event_score=0.0)

        total_score = 0.0

        for action in actions:
            action_val = action.value or 0.0
            
            if action.type == ActionType.DIVIDEND:
                # Assuming presence of a dividend is inherently slightly positive
                # Size of dividend ideally requires history to check for "increases",
                # but for MVP we apply a base positive.
                total_score += 0.5 

            elif action.type == ActionType.SPLIT:
                # Stock splits signal management confidence
                # Ratios > 1 (e.g. 4 for 1) are standard splits.
                if action_val > 1.0:
                    total_score += 0.5

            elif action.type == ActionType.EARNINGS:
                # If EPS estimate/actual is positive, slightly positive impact
                if action_val > 0:
                    total_score += 0.8
                elif action_val < 0:
                    total_score -= 0.8

        # Normalize score loosely to the [-1.0, 1.0] range using a simple tanh function 
        # or bounding. We'll simply use max/min capping for MVP clarity.
        final_score = max(min(total_score, 1.0), -1.0)

        logger.debug(
            "EventAnalyzer | Derived event score: %.3f from %d actions",
            final_score, len(actions)
        )

        return EventSignals(event_score=round(final_score, 4))
