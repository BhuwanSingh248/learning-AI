"""
Signal Data Models

Provides the unified structure for engineered features (signals) 
that the Agent / LLM layer will consume in Phase 4.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceSignals:
    """
    Quantifiable signals derived from historical price action.
    """
    trend: str          # "bullish", "bearish", "neutral"
    momentum: float     # Rate of change or momentum score
    volatility: float   # Measure of price stability (e.g. std dev of returns)


@dataclass(frozen=True)
class NewsSignals:
    """
    Sentiment signals derived from news analysis.
    """
    sentiment_score: float  # -1.0 to 1.0


@dataclass(frozen=True)
class EventSignals:
    """
    Impact signals derived from corporate actions.
    """
    event_score: float      # Score summarizing recent corporate events


@dataclass(frozen=True)
class CombinedMarketSignal:
    """
    The unified signal structure combining all modular analysis.
    This acts as the final 'clean' state of the market for a given ticker 
    before LLM reasoning is applied.
    """
    symbol: str
    price_signals: PriceSignals
    news_signals: NewsSignals
    event_signals: EventSignals

    @property
    def summary(self) -> dict:
        """Convenience method to export as a flat dict."""
        return {
            "symbol": self.symbol,
            "trend": self.price_signals.trend,
            "momentum": self.price_signals.momentum,
            "volatility": self.price_signals.volatility,
            "sentiment": self.news_signals.sentiment_score,
            "event_score": self.event_signals.event_score
        }
