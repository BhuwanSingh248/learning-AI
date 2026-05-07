"""
Tests for src/rag/indexer.py

Mirrors folder structure: tests/rag/test_indexer.py

All external dependencies (FAISSStore, EmbeddingModel, AsyncSession) are
mocked so no real DB or FAISS connection is needed.
"""

import pytest
import numpy as np
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

from src.rag.indexer import NewsIndexer
from src.data.models.news import NewsItem


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_news_item(title="Market rises sharply.", summary="Stocks climbed today.", source="Reuters") -> NewsItem:
    return NewsItem(
        title=title,
        summary=summary,
        timestamp=datetime(2026, 5, 7, 12, 0, 0, tzinfo=timezone.utc),
        source=source,
    )


def make_long_news_item() -> NewsItem:
    """Returns a NewsItem whose combined text will produce multiple chunks."""
    long_summary = (
        "Aarti Industries posted strong quarterly results. "
        "Revenue increased by 18% year-on-year driven by specialty chemicals demand. "
        "EBITDA margins improved to 22%, up from 18% in the previous quarter. "
        "Export volumes to Europe and North America grew significantly this period. "
        "The board also declared an interim dividend of Rs 2 per share to shareholders. "
        "Capital expenditure for the next fiscal is planned at Rs 800 crore by management. "
        "New plant commissioning in Gujarat is on track for Q3 of the current fiscal year. "
        "Research and development spend increased to 3% of revenue this quarter significantly. "
        "Management remains confident about sustaining growth momentum into next year strongly. "
        "Domestic volumes were flat but international volumes showed robust growth consistently. "
    ) * 4  # repeat to guarantee multi-chunk (>600 tokens)
    return NewsItem(title="Aarti Industries Q2 Earnings", summary=long_summary,
                    timestamp=datetime(2026, 5, 7, tzinfo=timezone.utc), source="Bloomberg")


def make_indexer(add_vector_return: int = 1):
    """Returns a NewsIndexer with fully mocked FAISSStore and EmbeddingModel."""
    mock_store = MagicMock()
    mock_store.add_vector = AsyncMock(return_value=add_vector_return)
    mock_store.save = MagicMock()

    mock_embedder = MagicMock()
    mock_embedder.embed_text = MagicMock(return_value=np.zeros(384, dtype=np.float32))

    indexer = NewsIndexer(faiss_store=mock_store, embedder=mock_embedder)
    return indexer, mock_store, mock_embedder


def make_db_session():
    return AsyncMock()


# ---------------------------------------------------------------------------
# Test 1 — Basic indexing: single short article
# ---------------------------------------------------------------------------

class TestSingleArticleIndexing:

    @pytest.mark.asyncio
    async def test_returns_correct_chunk_count_for_short_article(self):
        indexer, store, embedder = make_indexer()
        article = make_news_item()
        result = await indexer.index_news("AAPL", [article], make_db_session())
        assert result == 1  # short article → 1 chunk

    @pytest.mark.asyncio
    async def test_embed_text_called_once_for_short_article(self):
        indexer, store, embedder = make_indexer()
        article = make_news_item()
        await indexer.index_news("AAPL", [article], make_db_session())
        assert embedder.embed_text.call_count == 1

    @pytest.mark.asyncio
    async def test_add_vector_called_once_for_short_article(self):
        indexer, store, embedder = make_indexer()
        article = make_news_item()
        await indexer.index_news("AAPL", [article], make_db_session())
        assert store.add_vector.call_count == 1

    @pytest.mark.asyncio
    async def test_save_called_once_after_indexing(self):
        indexer, store, embedder = make_indexer()
        article = make_news_item()
        await indexer.index_news("AAPL", [article], make_db_session())
        store.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_vector_receives_correct_symbol(self):
        indexer, store, embedder = make_indexer()
        article = make_news_item()
        await indexer.index_news("AARTIIND.NS", [article], make_db_session())
        call_kwargs = store.add_vector.call_args.kwargs
        assert call_kwargs["symbol"] == "AARTIIND.NS"

    @pytest.mark.asyncio
    async def test_add_vector_receives_correct_source_id(self):
        indexer, store, embedder = make_indexer()
        article = make_news_item(source="Bloomberg")
        await indexer.index_news("AAPL", [article], make_db_session())
        call_kwargs = store.add_vector.call_args.kwargs
        assert call_kwargs["source_id"] == "Bloomberg"

    @pytest.mark.asyncio
    async def test_add_vector_receives_float32_vector(self):
        indexer, store, embedder = make_indexer()
        article = make_news_item()
        await indexer.index_news("AAPL", [article], make_db_session())
        vector = store.add_vector.call_args.kwargs["vector"]
        assert vector.dtype == np.float32


# ---------------------------------------------------------------------------
# Test 2 — Multiple articles and long articles
# ---------------------------------------------------------------------------

class TestMultipleArticles:

    @pytest.mark.asyncio
    async def test_two_short_articles_returns_two(self):
        indexer, store, embedder = make_indexer()
        articles = [make_news_item(), make_news_item(title="Another headline.", summary="More news here.")]
        result = await indexer.index_news("MSFT", articles, make_db_session())
        assert result == 2

    @pytest.mark.asyncio
    async def test_long_article_produces_multiple_chunks(self):
        indexer, store, embedder = make_indexer()
        article = make_long_news_item()
        result = await indexer.index_news("AARTIIND.NS", [article], make_db_session())
        assert result > 1

    @pytest.mark.asyncio
    async def test_save_called_once_even_for_multiple_articles(self):
        indexer, store, embedder = make_indexer()
        articles = [make_news_item(), make_long_news_item()]
        await indexer.index_news("MSFT", articles, make_db_session())
        store.save.assert_called_once()


# ---------------------------------------------------------------------------
# Test 3 — Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    @pytest.mark.asyncio
    async def test_empty_articles_list_returns_zero(self):
        indexer, store, embedder = make_indexer()
        result = await indexer.index_news("AAPL", [], make_db_session())
        assert result == 0

    @pytest.mark.asyncio
    async def test_empty_articles_list_does_not_call_embed(self):
        indexer, store, embedder = make_indexer()
        await indexer.index_news("AAPL", [], make_db_session())
        embedder.embed_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_articles_list_still_calls_save(self):
        indexer, store, embedder = make_indexer()
        await indexer.index_news("AAPL", [], make_db_session())
        store.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_faulty_add_vector_does_not_crash_whole_batch(self):
        """One article failing should not stop remaining articles from being indexed."""
        indexer, store, embedder = make_indexer()

        # First call raises, second succeeds
        store.add_vector.side_effect = [Exception("DB error"), None]

        articles = [make_news_item(), make_news_item(title="Safe article.", summary="This one is fine.")]
        result = await indexer.index_news("AAPL", articles, make_db_session())
        # First article fails (0 chunks indexed), second article succeeds (1 chunk)
        assert result == 1

    @pytest.mark.asyncio
    async def test_article_with_empty_title_and_summary_skipped(self):
        """An article with no title and no summary produces 0 chunks — should be skipped cleanly."""
        indexer, store, embedder = make_indexer()
        empty_article = NewsItem(title="", summary="", timestamp=datetime.now(timezone.utc), source="Reuters")
        result = await indexer.index_news("AAPL", [empty_article], make_db_session())
        assert result == 0
        embedder.embed_text.assert_not_called()
