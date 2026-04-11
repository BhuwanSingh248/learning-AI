"""
Abstract interfaces for the Data Layer.

Follows the Dependency Inversion Principle (DIP):
  - High-level modules (DataService) depend on these abstractions.
  - Low-level modules (OpenBBProvider, etc.) implement them.
  - This means providers can be swapped without touching business logic.
"""

from abc import ABC, abstractmethod
from typing import List

from src.data.models.price import PriceBar
from src.data.models.news import NewsItem
from src.data.models.corporate_actions import CorporateAction


class IDataProvider(ABC):
    """
    Abstract base class that every data provider must implement.

    Single Responsibility: defines WHAT data can be fetched,
    not HOW it is fetched. Concrete providers (e.g. OpenBBProvider)
    are responsible for the "how".

    Adding a new provider (e.g. Finnhub) = implement this interface.
    No existing code changes required. (Open/Closed Principle)
    """

    @abstractmethod
    def get_price_data(self, symbol: str, lookback: int) -> List[PriceBar]:
        """
        Fetch historical OHLCV price bars for a given symbol.

        Args:
            symbol:   Ticker symbol (e.g. "AAPL")
            lookback: Number of calendar days to look back from today

        Returns:
            List of PriceBar objects in ascending date order.
        """
        ...

    @abstractmethod
    def get_news(self, symbol: str) -> List[NewsItem]:
        """
        Fetch recent news articles related to a given symbol.

        Args:
            symbol: Ticker symbol (e.g. "AAPL")

        Returns:
            List of NewsItem objects, most recent first.
        """
        ...

    @abstractmethod
    def get_corporate_actions(self, symbol: str) -> List[CorporateAction]:
        """
        Fetch upcoming / recent corporate actions for a given symbol.

        Args:
            symbol: Ticker symbol (e.g. "AAPL")

        Returns:
            List of CorporateAction objects in ascending date order.
        """
        ...
