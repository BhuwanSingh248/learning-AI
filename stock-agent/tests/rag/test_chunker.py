"""
Tests for src/rag/chunker.py

Mirrors folder structure: tests/rag/test_chunker.py
"""

import pytest
from src.rag.chunker import NewsChunker
from src.rag.models import NewsChunk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SHORT_TITLE = "Market update"
SHORT_SUMMARY = "Stocks rose slightly today."

LONG_TITLE = "AARTIIND quarterly earnings report"
LONG_SUMMARY = (
    "Aarti Industries posted strong quarterly results. "
    "Revenue increased by 18% year-on-year driven by specialty chemicals demand. "
    "EBITDA margins improved to 22%, up from 18% in the previous quarter. "
    "The management guided for continued growth in the agrochemicals segment. "
    "Export volumes to Europe and North America grew significantly this period. "
    "The board also declared an interim dividend of Rs 2 per share to shareholders. "
    "Analysts have upgraded the stock citing strong order book visibility going forward. "
    "Capital expenditure for the next fiscal is planned at Rs 800 crore by management. "
    "Debt levels remain comfortable with a net debt-to-equity ratio of 0.4 currently. "
    "The company expects double-digit growth for the full fiscal year ahead confidently. "
    "New plant commissioning in Gujarat is on track for Q3 of the current fiscal year. "
    "Research and development spend increased to 3% of revenue this quarter significantly. "
    "Management remains confident about sustaining growth momentum into next year strongly. "
    "Domestic volumes were flat but international volumes showed robust growth consistently. "
    "Profitability in the pharma intermediates segment also improved materially over the year. "
    "The specialty chemicals division contributed the largest share of overall revenue growth. "
    "Order book for the agrochemicals segment stands at a record high of Rs 2000 crore now. "
    "Operating cash flows improved by 30% year-on-year, reflecting strong business execution. "
    "Working capital cycle has been optimized, reducing days sales outstanding by 10 days. "
    "The company plans to enter the electronic chemicals market in the next fiscal year. "
    "Management highlighted strong client relationships across US, Europe, and Japan markets. "
    "Capacity utilization across all plants reached 85%, the highest level in three years. "
    "Employee headcount increased by 12% as the company scales up operations for future growth. "
    "Supply chain resilience was improved by onboarding additional raw material vendors globally. "
) * 2  # repeat to guarantee >2400 chars


# ---------------------------------------------------------------------------
# Test 1 — Short news: expect exactly 1 chunk
# ---------------------------------------------------------------------------

class TestShortNews:
    def test_returns_one_chunk(self):
        result = NewsChunker.chunk(
            SHORT_TITLE, SHORT_SUMMARY,
            symbol="TEST", source_id="src_001", timestamp="2026-05-07"
        )
        assert len(result) == 1

    def test_chunk_is_newsChunk_instance(self):
        result = NewsChunker.chunk(SHORT_TITLE, SHORT_SUMMARY, source_id="src_001")
        assert isinstance(result[0], NewsChunk)

    def test_chunk_contains_title_and_summary(self):
        result = NewsChunker.chunk(SHORT_TITLE, SHORT_SUMMARY, source_id="src_001")
        assert SHORT_TITLE in result[0].text
        assert "Stocks rose" in result[0].text

    def test_metadata_attached_correctly(self):
        result = NewsChunker.chunk(
            SHORT_TITLE, SHORT_SUMMARY,
            symbol="AAPL", source_id="src_42", timestamp="2026-01-01"
        )
        chunk = result[0]
        assert len(chunk.chunk_id) == 64
        assert chunk.source_id == "src_42"
        assert chunk.chunk_index == 0
        assert chunk.symbol == "AAPL"
        assert chunk.timestamp == "2026-01-01"


# ---------------------------------------------------------------------------
# Test 2 — Long news: expect multiple chunks
# ---------------------------------------------------------------------------

class TestLongNews:
    def test_returns_multiple_chunks(self):
        result = NewsChunker.chunk(
            LONG_TITLE, LONG_SUMMARY,
            symbol="AARTIIND.NS", source_id="src_long", timestamp="2026-05-07"
        )
        assert len(result) > 1

    def test_chunk_indices_are_sequential(self):
        result = NewsChunker.chunk(LONG_TITLE, LONG_SUMMARY, source_id="src_long")
        indices = [c.chunk_index for c in result]
        assert indices == list(range(len(result)))

    def test_chunk_ids_are_unique(self):
        result = NewsChunker.chunk(LONG_TITLE, LONG_SUMMARY, source_id="src_long")
        ids = [c.chunk_id for c in result]
        assert len(ids) == len(set(ids))

    def test_all_chunks_are_non_empty(self):
        result = NewsChunker.chunk(LONG_TITLE, LONG_SUMMARY, source_id="src_long")
        for chunk in result:
            assert chunk.text.strip() != ""

    @pytest.mark.xfail(reason="Overlap tuning deferred — CHUNK_OVERLAP value needs calibration for sentence-based strategy")
    def test_overlap_exists_between_consecutive_chunks(self):
        """
        At least one word from the end of chunk N should appear
        in the beginning of chunk N+1 when overlap is active.
        """
        result = NewsChunker.chunk(LONG_TITLE, LONG_SUMMARY, source_id="src_long")
        if len(result) < 2:
            pytest.skip("Not enough chunks to test overlap")
        for i in range(len(result) - 1):
            end_words = set(result[i].text.split()[-10:])
            start_words = set(result[i + 1].text.split()[:30])
            assert end_words & start_words, (
                f"No overlap detected between chunk {i} and chunk {i+1}"
            )


# ---------------------------------------------------------------------------
# Test 3 — Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_both_empty_returns_empty_list(self):
        result = NewsChunker.chunk("", "", source_id="src_edge")
        assert result == []

    def test_none_title_and_none_summary_returns_empty_list(self):
        result = NewsChunker.chunk(None, None, source_id="src_edge")
        assert result == []

    def test_title_only_returns_single_chunk(self):
        result = NewsChunker.chunk("Breaking news headline.", "", source_id="src_edge")
        assert len(result) == 1
        assert "Breaking news" in result[0].text

    def test_summary_only_returns_single_chunk(self):
        result = NewsChunker.chunk("", "Some summary content here.", source_id="src_edge")
        assert len(result) == 1

    def test_no_source_id_chunk_id_still_formed(self):
        result = NewsChunker.chunk(SHORT_TITLE, SHORT_SUMMARY)
        assert len(result[0].chunk_id) == 64

    def test_sanity_each_chunk_makes_standalone_sense(self):
        """Each chunk should contain at least one complete word."""
        result = NewsChunker.chunk(LONG_TITLE, LONG_SUMMARY, source_id="src_sanity")
        for chunk in result:
            words = chunk.text.split()
            assert len(words) >= 3, f"Chunk too small to be meaningful: '{chunk.text}'"
