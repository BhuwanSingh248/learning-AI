import asyncio
import os
import sys
from sqlalchemy import text
from src.config.database import engine, AsyncSessionLocal
from src.config.logger import setup_logger
from src.rag.faiss_store import FAISSStore
from src.rag.embedder import EmbeddingModel
from src.rag.indexer import NewsIndexer
from src.data.providers.openbb_provider import OpenBBProvider
from src.data.providers.marketaux_provider import MarketauxProvider
from src.data.providers.gnews_provider import GNewsProvider
from src.data.providers.composite_provider import CompositeDataProvider
from src.data.services.data_service import DataService

logger = setup_logger(__name__)

# List of default stock symbols to re-index after cleanup
DEFAULT_SYMBOLS = ["AAPL", "MSFT", "INFY", "GOOG"]

async def rebuild_rag_index():
    logger.info("RebuildIndex | Starting RAG index cleanup and rebuild process...")
    
    # 1. Truncate PostgreSQL metadata table
    async with engine.begin() as conn:
        logger.info("RebuildIndex | Truncating database table 'rag_news_metadata'...")
        await conn.execute(text("TRUNCATE TABLE rag_news_metadata RESTART IDENTITY CASCADE;"))
        logger.info("RebuildIndex | Database table truncated successfully.")
        
    # 2. Reset and clear the FAISS index file on disk
    index_file = "rag_faiss.index"
    if os.path.exists(index_file):
        try:
            os.remove(index_file)
            logger.info("RebuildIndex | Removed existing FAISS index file '%s'", index_file)
        except Exception as e:
            logger.error("RebuildIndex | Failed to remove index file: %s", e)
            
    # 3. Instantiate clean components
    faiss_store = FAISSStore()
    embedder = EmbeddingModel()
    indexer = NewsIndexer(faiss_store, embedder)
    
    # Setup data providers to fetch fresh news
    openbb = OpenBBProvider()
    marketaux = MarketauxProvider()
    gnews = GNewsProvider()
    composite = CompositeDataProvider(primary=openbb, news_main=marketaux, news_fallback=gnews)
    data_service = DataService(composite)
    
    # 4. Fetch and re-index news for default symbols
    async with AsyncSessionLocal() as session:
        for symbol in DEFAULT_SYMBOLS:
            logger.info("RebuildIndex | Fetching news for %s...", symbol)
            raw_news = data_service.get_news(symbol)
            if not raw_news:
                logger.info("RebuildIndex | No news fetched for %s. Skipping.", symbol)
                continue
                
            logger.info("RebuildIndex | Indexing %d articles for %s...", len(raw_news), symbol)
            indexed_chunks = await indexer.index_news(symbol, raw_news, session)
            logger.info("RebuildIndex | Successfully indexed %d chunks for %s.", indexed_chunks, symbol)
            
    logger.info("RebuildIndex | RAG index rebuild process finished successfully.")

if __name__ == "__main__":
    asyncio.run(rebuild_rag_index())
