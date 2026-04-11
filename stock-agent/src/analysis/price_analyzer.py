"""
Price Feature Engineering Layer

Applies standard mathematical logic to clean price data (Pandas DataFrame)
to extract measurable signals like Trend, Momentum, and Volatility.
"""

import pandas as pd
import numpy as np

from src.analysis.signals import PriceSignals
from src.config.logger import setup_logger

logger = setup_logger(__name__)


class PriceAnalyzer:
    """
    Analyzes standardized price data to produce technical indicators 
    and feature scores.
    """

    @staticmethod
    def analyze(df: pd.DataFrame) -> PriceSignals:
        """
        Derives trend, momentum, and volatility from the price dataframe.
        
        Args:
            df: Cleaned dataframe with 'close' price column sorted chronologically.
                Expects DatetimeIndex.
                
        Returns:
            A populated PriceSignals dataclass.
        """
        if df is None or df.empty or "close" not in df.columns:
            logger.warning("PriceAnalyzer | Empty or invalid DataFrame provided.")
            return PriceSignals(trend="neutral", momentum=0.0, volatility=0.0)

        close_prices = df["close"]
        n_days = len(close_prices)

        if n_days < 2:
            return PriceSignals(trend="neutral", momentum=0.0, volatility=0.0)

        # 1. Momentum (Return over recent period)
        # Compare current close to the close 5 days ago (or whatever is available)
        lookback = min(5, n_days - 1)
        current_price = close_prices.iloc[-1]
        past_price = close_prices.iloc[-(lookback + 1)]
        
        # simple percentage return
        momentum = ((current_price - past_price) / past_price) if past_price > 0 else 0.0

        # 2. Volatility (Standard Deviation of Daily Returns)
        # Calculate daily pct change
        daily_returns = close_prices.pct_change().dropna()
        if not daily_returns.empty:
            # Annualized volatility roughly based on trading days (252)
            volatility = float(daily_returns.std() * np.sqrt(252))
        else:
            volatility = 0.0

        # 3. Trend (Moving Averages)
        # Using 5-day (fast) vs 20-day (slow) SMA if sufficient data exists
        if n_days >= 20:
            sma_fast = close_prices.rolling(window=5).mean().iloc[-1]
            sma_slow = close_prices.rolling(window=20).mean().iloc[-1]
            
            if sma_fast > sma_slow:
                 # Check if the fast average is diverging upwards strongly
                trend = "bullish"
            elif sma_fast < sma_slow:
                trend = "bearish"
            else:
                trend = "neutral"
        else:
            # Fallback if we don't have enough data for a 20-day MA
            # Simple check against the mean of available data
            mean_price = close_prices.mean()
            if current_price > (mean_price * 1.01):
                trend = "bullish"
            elif current_price < (mean_price * 0.99):
                trend = "bearish"
            else:
                trend = "neutral"

        logger.debug(
            "PriceAnalyzer | Calculated signals: trend=%s, momentum=%.3f, vol=%.3f",
            trend, momentum, volatility
        )

        return PriceSignals(
            trend=trend,
            momentum=round(float(momentum), 4),
            volatility=round(float(volatility), 4)
        )
