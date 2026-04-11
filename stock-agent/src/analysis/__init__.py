"""
Analysis Layer — public API

Provides access to the modular feature engineering structure.
The core element to export is the MarketAnalyzer and base models.
"""

from src.analysis.market_analyzer import MarketAnalyzer
from src.analysis.signals import CombinedMarketSignal, PriceSignals, NewsSignals, EventSignals

__all__ = [
    "MarketAnalyzer",
    "CombinedMarketSignal",
    "PriceSignals",
    "NewsSignals",
    "EventSignals"
]
