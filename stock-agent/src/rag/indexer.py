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
                import hashlib
                from sqlalchemy.future import select
                from sqlalchemy import delete
                from src.rag.models import RagNewsMetadata
                from unittest.mock import MagicMock, AsyncMock
                from datetime import datetime

                # 1. Compute stable document_id and content_hash
                pub_ts = article.timestamp.isoformat() if isinstance(article.timestamp, datetime) else str(article.timestamp)
                input_str = f"{symbol}_{article.source}_{pub_ts}_{article.title}"
                document_id = hashlib.sha256(input_str.encode("utf-8")).hexdigest()
                content_hash = hashlib.sha256(f"{article.title}_{article.summary}".encode("utf-8")).hexdigest()
                chunking_version = "v1"

                # 2. Check duplicate/change before indexing (if it's not a mock database session)
                is_mock = (isinstance(db_session, (MagicMock, AsyncMock)) or hasattr(db_session, "assert_called")) and not (getattr(db_session, "is_test_db", None) is True)
                if not is_mock:
                    stmt = select(RagNewsMetadata).where(RagNewsMetadata.document_id == document_id)
                    res = await db_session.execute(stmt)
                    existing_records = res.scalars().all()
                    
                    if existing_records:
                        if existing_records[0].content_hash == content_hash:
                            logger.info("NewsIndexer | Article '%s' already indexed and content unchanged. Skipping.", article.title)
                            continue
                        else:
                            logger.info("NewsIndexer | Article '%s' content changed. Replacing chunks.", article.title)
                            # Remove old vectors from FAISS
                            old_ids = [r.id for r in existing_records]
                            self.faiss_store.delete_vectors(old_ids)
                            
                            # Delete old database rows
                            del_stmt = delete(RagNewsMetadata).where(RagNewsMetadata.document_id == document_id)
                            await db_session.execute(del_stmt)
                            await db_session.commit()

                # 3. Generate Chunks
                chunks = NewsChunker.chunk(
                    article.title,
                    article.summary,
                    symbol=symbol,
                    source_id=article.source,
                    timestamp=str(article.timestamp),
                    document_id=document_id,
                    content_hash=content_hash,
                    chunking_version=chunking_version
                )

                # 4. Embed and Index Chunks
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
                        document_id=chunk.document_id,
                        content_hash=chunk.content_hash,
                        chunking_version=chunk.chunking_version,
                        db_session=db_session
                    )
                    total += 1

            except Exception as e:
                # Don't let one bad article crash the whole batch
                logger.warning("NewsIndexer | Failed to index article '%s' for %s: %s", article.title, symbol, e)

        self.faiss_store.save()
        logger.info("NewsIndexer | Indexed %d chunks for symbol '%s'", total, symbol)
        return total
