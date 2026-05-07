"""
News Indexer
============

Ingestion pipeline: News → Chunk → Embed → FAISS + PostgreSQL

Flow:
    1. Pass each NewsItem through NewsChunker → list of chunks
    2. For each chunk → embed chunk.text → get vector
    3. Call faiss_store.add_vector(chunk fields + vector + db_session)
    4. After all articles → persist FAISS index to disk
"""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.rag.faiss_store import FAISSStore
from src.rag.embedder import EmbeddingModel
from src.rag.chunker import NewsChunker
from src.data.models.news import NewsItem
from src.config.logger import setup_logger

logger = setup_logger(__name__)


class NewsIndexer:
    """
    Orchestrates the full ingestion pipeline for a batch of news articles.
    Depends on FAISSStore and EmbeddingModel via constructor injection (DIP).
    """

    def __init__(self, faiss_store: FAISSStore, embedder: EmbeddingModel) -> None:
        self.faiss_store = faiss_store
        self.embedder = embedder

    async def index_news(
        self,
        symbol: str,
        news_articles: List[NewsItem],
        db_session: AsyncSession
    ) -> int:
        """
        Chunk, embed, and index all provided news articles for a given symbol.

        Args:
            symbol:        Stock ticker (e.g. "AARTIIND.NS").
            news_articles: List of NewsItem objects fetched from a provider.
            db_session:    Active async DB session for metadata persistence.

        Returns:
            Total number of chunks successfully indexed.
        """
        total = 0

        for article in news_articles:
            try:
                # article.source is the news outlet name (e.g. "Reuters")
                # Used as source_id since NewsItem has no dedicated id field
                chunks = NewsChunker.chunk(
                    article.title,
                    article.summary,
                    symbol=symbol,
                    source_id=article.source,      # ← correct field: .source not .source_id
                    timestamp=str(article.timestamp)
                )

                for chunk in chunks:
                    vector = self.embedder.embed_text(chunk.text)
                    await self.faiss_store.add_vector(
                        chunk_id=chunk.chunk_id,
                        source_id=chunk.source_id,
                        symbol=chunk.symbol,
                        chunk_index=chunk.chunk_index,
                        chunk_text=chunk.text,
                        timestamp=article.timestamp,   # pass datetime object, not str
                        vector=vector,
                        db_session=db_session
                    )
                    total += 1

            except Exception as e:
                # Don't let one bad article crash the whole batch
                logger.warning("NewsIndexer | Failed to index article '%s' for %s: %s", article.title, symbol, e)

        self.faiss_store.save()
        logger.info("NewsIndexer | Indexed %d chunks for symbol '%s'", total, symbol)
        return total
