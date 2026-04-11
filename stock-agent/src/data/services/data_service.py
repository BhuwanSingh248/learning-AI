"""
DataService — orchestrates the data layer.

This is the ONLY module that the rest of the application (analysis,
agent, API layers) should import from when they need market data.

Design decisions:
  - Depends on IDataProvider abstraction, NOT on OpenBB directly.
    (Dependency Inversion Principle)
  - Accepts the provider via constructor injection so it is trivially
    testable with a mock provider and swappable at runtime.
  - Owns no fetching logic of its own; it delegates entirely to the
    injected provider.

Responsibilities:
  ✅ Be the single entry-point for data access
  ✅ Delegate to the injected provider
  ✅ Log requests for observability

NOT responsible for:
  ❌ Calling OpenBB (that is the provider's job)
  ❌ Cleaning or transforming data
  ❌ Caching (future concern — can be added here without touching callers)
"""

from typing import List

from src.config.logger import setup_logger
from src.data.base.interfaces import IDataProvider
from src.data.models.price import PriceBar
from src.data.models.news import NewsItem
from src.data.models.corporate_actions import CorporateAction

logger = setup_logger(__name__)


class DataService:
    """
    High-level data access façade.

    Usage example (once providers are implemented):

        provider = OpenBBProvider()
        service  = DataService(provider=provider)

        price_bars = service.get_price_data("AAPL", lookback=30)
        news       = service.get_news("AAPL")
        actions    = service.get_corporate_actions("AAPL")
    """

    def __init__(self, provider: IDataProvider) -> None:
        """
        Args:
            provider: Any concrete implementation of IDataProvider.
                      Injected so callers (or tests) control which
                      provider is used.
        """
        self._provider = provider

    # ------------------------------------------------------------------ #
    # Price Data                                                           #
    # ------------------------------------------------------------------ #

    def get_price_data(self, symbol: str, lookback: int = 90) -> List[PriceBar]:
        """
        Retrieve historical OHLCV bars for `symbol`.

        Args:
            symbol:   Ticker symbol (e.g. "AAPL")
            lookback: Calendar days to look back (default: 90)

        Returns:
            List[PriceBar] in ascending date order.
        """
        logger.debug("DataService.get_price_data | symbol=%s lookback=%d", symbol, lookback)
        try:
            return self._provider.get_price_data(symbol=symbol, lookback=lookback)
        except Exception as e:
            logger.error("DataService failed to get price data for %s: %s", symbol, e)
            return []

    # ------------------------------------------------------------------ #
    # News                                                                 #
    # ------------------------------------------------------------------ #

    def get_news(self, symbol: str) -> List[NewsItem]:
        """
        Retrieve recent news articles for `symbol`.

        Args:
            symbol: Ticker symbol (e.g. "AAPL")

        Returns:
            List[NewsItem], most recent first.
        """
        logger.debug("DataService.get_news | symbol=%s", symbol)
        try:
            return self._provider.get_news(symbol=symbol)
        except Exception as e:
            logger.error("DataService failed to get news for %s: %s", symbol, e)
            return []

    # ------------------------------------------------------------------ #
    # Corporate Actions                                                    #
    # ------------------------------------------------------------------ #

    def get_corporate_actions(self, symbol: str) -> List[CorporateAction]:
        """
        Retrieve upcoming / recent corporate actions for `symbol`.

        Args:
            symbol: Ticker symbol (e.g. "AAPL")

        Returns:
            List[CorporateAction] in ascending date order.
        """
        logger.debug("DataService.get_corporate_actions | symbol=%s", symbol)
        try:
            return self._provider.get_corporate_actions(symbol=symbol)
        except Exception as e:
            logger.error("DataService failed to get corporate actions for %s: %s", symbol, e)
            return []
