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

class GNewsProvider(IDataProvider):
    """
    Data provider for GNews API.
    Used as a fallback mechanism to fetch business headlines using keyword search.
    """
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GNEWS_API_KEY
        self.base_url = "https://gnews.io/api/v4/search"
        
        if not self.api_key:
            logger.warning("GNewsProvider | GNEWS_API_KEY is not set.")

    def get_price_data(self, symbol: str, lookback: int) -> List[PriceBar]:
        """Not implemented for this news-only provider."""
        return []

    def get_news(self, symbol: str) -> List[NewsItem]:
        """
        Fetch recent news articles for a given symbol from GNews.
        """
        if not self.api_key:
            logger.error("GNewsProvider | Cannot fetch news without API key.")
            return []
            
        logger.debug("GNewsProvider | Fetching news for %s", symbol)
        
        # Strip suffix like .NS or .BO for a broader keyword search in Google News
        keyword = symbol.split('.')[0]
        
        params = {
            "q": keyword,
            "lang": "en",
            "country": "in",
            "max": 5,
            "apikey": self.api_key
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                news_items = []
                for article in data.get("articles", []):
                    title = article.get("title", "")
                    description = article.get("description", "")
                    url = article.get("url", "")
                    source_dict = article.get("source", {})
                    source_name = source_dict.get("name", "GNews") if isinstance(source_dict, dict) else "GNews"
                    published_at = article.get("publishedAt", "")
                    
                    try:
                        dt_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    except Exception:
                        dt_obj = datetime.utcnow()
                        
                    news_items.append(
                        NewsItem(
                            title=title,
                            summary=description if description else title,
                            source=source_name,
                            timestamp=dt_obj
                        )
                    )
                
                logger.info("GNewsProvider | Retrieved %d articles for %s", len(news_items), symbol)
                return news_items
                
        except Exception as e:
            logger.error("GNewsProvider | Failed to fetch news for %s: %s", symbol, e)
            return []

    def get_corporate_actions(self, symbol: str) -> List[CorporateAction]:
        """Not implemented for this news-only provider."""
        return []
