import httpx
from typing import List
from datetime import datetime

from src.data.base.interfaces import IDataProvider
from src.data.models.price import PriceBar
from src.data.models.news import NewsItem
from src.data.models.corporate_actions import CorporateAction
from src.config.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)

class MarketauxProvider(IDataProvider):
    """
    Data provider for Marketaux API.
    Specifically used to fetch robust financial news for global/Indian stocks.
    """
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.MARKETAUX_API_KEY
        self.base_url = "https://api.marketaux.com/v1/news/all"
        
        if not self.api_key:
            logger.warning("MarketauxProvider | MARKETAUX_API_KEY is not set.")

    def get_price_data(self, symbol: str, lookback: int) -> List[PriceBar]:
        """Not implemented for this news-only provider."""
        return []

    def get_news(self, symbol: str) -> List[NewsItem]:
        """
        Fetch recent news articles for a given symbol from Marketaux.
        """
        if not self.api_key:
            logger.error("MarketauxProvider | Cannot fetch news without API key.")
            return []
            
        logger.debug("MarketauxProvider | Fetching news for %s", symbol)
        
        params = {
            "symbols": symbol,
            "filter_entities": "true",
            "language": "en",
            "api_token": self.api_key,
            "limit": 5 # Limit to top 5 to save bandwidth/tokens
        }
        
        try:
            # We use a synchronous request here because the IDataProvider interface is sync.
            # (In a fully async system, this should be httpx.AsyncClient)
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                news_items = []
                for article in data.get("data", []):
                    title = article.get("title", "")
                    description = article.get("description", "")
                    url = article.get("url", "")
                    source = article.get("source", "Marketaux")
                    published_at = article.get("published_at", "")
                    
                    # Construct NewsItem
                    # Assuming NewsItem takes: title, summary, url, source, timestamp
                    # Let's map it cleanly
                    try:
                        # Attempt to parse ISO format if possible, otherwise keep string
                        # Marketaux returns ISO 8601 strings
                        dt_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    except Exception:
                        dt_obj = datetime.utcnow()
                        
                    news_items.append(
                        NewsItem(
                            title=title,
                            summary=description if description else title,
                            source=source,
                            timestamp=dt_obj
                        )
                    )
                
                logger.info("MarketauxProvider | Retrieved %d articles for %s", len(news_items), symbol)
                return news_items
                
        except Exception as e:
            logger.error("MarketauxProvider | Failed to fetch news for %s: %s", symbol, e)
            return []

    def get_corporate_actions(self, symbol: str) -> List[CorporateAction]:
        """Not implemented for this news-only provider."""
        return []
