"""
Output contract: Price Data

Defines the canonical shape of OHLCV data returned by any provider.
All providers MUST map their raw output to this dataclass so the rest
of the system has a single, stable interface to work with.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PriceBar:
    """
    A single OHLCV price bar for one trading day.

    Attributes:
        date:   Trading date
        open:   Opening price
        high:   Intraday high price
        low:    Intraday low price
        close:  Closing price
        volume: Number of shares traded
    """

    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
