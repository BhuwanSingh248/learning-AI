from typing import List

from src.data.base.interfaces import IDataProvider
from src.data.models.price import PriceBar
from src.data.models.news import NewsItem
from src.data.models.corporate_actions import CorporateAction
from src.config.logger import setup_logger

logger = setup_logger(__name__)

class CompositeDataProvider(IDataProvider):
    """
    A smart router that delegates requests to underlying providers.
    - Prices and actions always go to the primary provider (OpenBB).
    - News for US stocks goes to the primary provider.
    - News for Indian stocks (.NS / .BO) goes to Marketaux, falling back to GNews.
    """

    def __init__(self, primary: IDataProvider, news_main: IDataProvider, news_fallback: IDataProvider):
        self.primary = primary
        self.news_main = news_main
        self.news_fallback = news_fallback

    def get_price_data(self, symbol: str, lookback: int) -> List[PriceBar]:
        return self.primary.get_price_data(symbol, lookback)

    def get_corporate_actions(self, symbol: str) -> List[CorporateAction]:
        return self.primary.get_corporate_actions(symbol)

    def get_news(self, symbol: str) -> List[NewsItem]:
        # Check if this is an Indian stock based on Yahoo Finance suffixes
        is_indian = symbol.upper().endswith(".NS") or symbol.upper().endswith(".BO")
        
        if not is_indian:
            logger.debug("CompositeProvider | Routing %s news to Primary Provider", symbol)
            return self.primary.get_news(symbol)
            
        logger.debug("CompositeProvider | Routing %s news to Main News Provider (Marketaux)", symbol)
        news_items = self.news_main.get_news(symbol)
        
        if not news_items:
            logger.warning("CompositeProvider | Main News Provider returned 0 items. Triggering Fallback (GNews) for %s", symbol)
            news_items = self.news_fallback.get_news(symbol)
            
        return news_items
