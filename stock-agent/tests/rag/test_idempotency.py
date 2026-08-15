import pytest
import numpy as np
import hashlib
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch
from src.rag.indexer import NewsIndexer
from src.data.models.news import NewsItem
from src.rag.chunker import NewsChunker
from src.rag.models import RagNewsMetadata

def make_news_item(title="Market update", summary="Stocks closed higher today.", source="Reuters") -> NewsItem:
    return NewsItem(
        title=title,
        summary=summary,
        timestamp=datetime(2026, 6, 14, 10, 0, 0, tzinfo=timezone.utc),
        source=source,
    )

def make_indexer():
    mock_store = MagicMock()
    mock_store.add_vector = AsyncMock(return_value=1)
    mock_store.delete_vectors = MagicMock()
    mock_store.save = MagicMock()

    mock_embedder = MagicMock()
    mock_embedder.embed_text = MagicMock(return_value=np.zeros(384, dtype=np.float32))

    indexer = NewsIndexer(faiss_store=mock_store, embedder=mock_embedder)
    return indexer, mock_store, mock_embedder

@pytest.mark.asyncio
async def test_stable_document_and_chunk_id_generation():
    """
    Verify that document_id and chunk_id generation is stable and consistent.
    """
    article1 = make_news_item("Aarti Industries Q2 Result", "Record profits reported.", "Bloomberg")
    article2 = make_news_item("Aarti Industries Q2 Result", "Record profits reported.", "Bloomberg")
    
    # Generate chunks
    chunks1 = NewsChunker.chunk(article1.title, article1.summary, symbol="AARTIIND.NS", source_id=article1.source, timestamp=str(article1.timestamp))
    chunks2 = NewsChunker.chunk(article2.title, article2.summary, symbol="AARTIIND.NS", source_id=article2.source, timestamp=str(article2.timestamp))
    
    assert len(chunks1) == len(chunks2)
    assert chunks1[0].document_id == chunks2[0].document_id
    assert chunks1[0].chunk_id == chunks2[0].chunk_id
    assert chunks1[0].content_hash == chunks2[0].content_hash

@pytest.mark.asyncio
async def test_collision_prevention():
    """
    Ensure two different articles (different title/source/timestamp) get unique chunk/document IDs.
    """
    article1 = make_news_item("Aarti Industries Q2 Result", "Record profits reported.", "Bloomberg")
    article2 = make_news_item("Aarti Industries Q3 Guidance", "Flat margins expected.", "Bloomberg")
    
    chunks1 = NewsChunker.chunk(article1.title, article1.summary, symbol="AARTIIND.NS", source_id=article1.source, timestamp=str(article1.timestamp))
    chunks2 = NewsChunker.chunk(article2.title, article2.summary, symbol="AARTIIND.NS", source_id=article2.source, timestamp=str(article2.timestamp))
    
    assert chunks1[0].document_id != chunks2[0].document_id
    assert chunks1[0].chunk_id != chunks2[0].chunk_id
    assert chunks1[0].content_hash != chunks2[0].content_hash

@pytest.mark.asyncio
async def test_idempotent_indexing_unchanged_article():
    """
    Verify that indexing an already indexed article with unchanged content
    skips re-indexing and returns 0 chunks indexed.
    """
    indexer, store, embedder = make_indexer()
    article = make_news_item()
    
    mock_db = AsyncMock()
    mock_db.is_test_db = True
    # Mock database query to return a record simulating that the article is already indexed
    mock_record = RagNewsMetadata(
        id=101,
        symbol="AAPL",
        chunk_text="Market update Stocks closed higher today.",
        chunk_id="some_chunk_id",
        source_id="Reuters",
        chunk_index=0,
        document_id="some_doc_id",
        content_hash=hashlib.sha256(f"{article.title}_{article.summary}".encode("utf-8")).hexdigest(),
        embedding_model="all-MiniLM-L6-v2",
        chunking_version="v1"
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_record]
    mock_db.execute.return_value = mock_result
    
    # Run indexer
    indexed_count = await indexer.index_news("AAPL", [article], mock_db)
    
    # Should skip indexing
    assert indexed_count == 0
    store.add_vector.assert_not_called()

@pytest.mark.asyncio
async def test_update_indexing_changed_article():
    """
    Verify that indexing an already indexed article with changed content
    replaces the old chunks and registers the new ones.
    """
    indexer, store, embedder = make_indexer()
    article_original = make_news_item()
    article_updated = make_news_item(summary="Updated summary: Stocks finished flat.")
    
    mock_db = AsyncMock()
    mock_db.is_test_db = True
    # Mock database query to return original article record
    mock_record = RagNewsMetadata(
        id=101,
        symbol="AAPL",
        chunk_text="Market update Stocks closed higher today.",
        chunk_id="some_chunk_id",
        source_id="Reuters",
        chunk_index=0,
        document_id="some_doc_id",
        content_hash=hashlib.sha256(f"{article_original.title}_{article_original.summary}".encode("utf-8")).hexdigest(),
        embedding_model="all-MiniLM-L6-v2",
        chunking_version="v1"
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_record]
    mock_db.execute.return_value = mock_result
    
    # Run indexer on the updated article
    indexed_count = await indexer.index_news("AAPL", [article_updated], mock_db)
    
    # Should delete the old vector ID (101) and add the new chunk
    assert indexed_count > 0
    store.delete_vectors.assert_called_once_with([101])
    store.add_vector.assert_called_once()
