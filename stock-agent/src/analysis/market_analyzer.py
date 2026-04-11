"""
Feature Engineering Layer — Orchestrator

Consolidates all modular analyzers (Price, News, Events) into a single 
facade representing the overall market signals.
"""

import pandas as pd
from typing import List

from src.data.models.news import NewsItem
from src.data.models.corporate_actions import CorporateAction
from src.analysis.signals import CombinedMarketSignal
from src.analysis.price_analyzer import PriceAnalyzer
from src.analysis.news_analyzer import NewsAnalyzer
from src.analysis.event_analyzer import EventAnalyzer


class MarketAnalyzer:
    """
    Facade class that orchestrates all analyzers to produce a unified signal.
    """

    @staticmethod
    def generate_signals(
        symbol: str, 
        clean_prices: pd.DataFrame, 
        clean_news: List[NewsItem], 
        clean_actions: List[CorporateAction]
    ) -> CombinedMarketSignal:
        """
        Runs all sub-analyzers and merges their outputs into the CombinedMarketSignal interface.
        
        Args:
            symbol: Ticker symbol.
            clean_prices: Standardized price DataFrame.
            clean_news: Standardized list of NewsItems.
            clean_actions: Standardized list of CorporateActions.
            
        Returns:
            A CombinedMarketSignal instance.
        """
        price_signals = PriceAnalyzer.analyze(clean_prices)
        news_signals = NewsAnalyzer.analyze(clean_news)
        event_signals = EventAnalyzer.analyze(clean_actions)

        return CombinedMarketSignal(
            symbol=symbol,
            price_signals=price_signals,
            news_signals=news_signals,
            event_signals=event_signals
        )
