"""
News Feature Engineering Layer

Extracts keyword-based sentiment from news headlines and summaries
to produce an aggregated, normalized sentiment score.
"""

from typing import List
import re

from src.analysis.signals import NewsSignals
from src.data.models.news import NewsItem
from src.config.logger import setup_logger

logger = setup_logger(__name__)


# Simple deterministic keyword dictionaries for MVP phase
POSITIVE_WORDS = {
    "surge", "jump", "grow", "growth", "gain", "profit", "beat",
    "exceed", "higher", "positive", "upgrade", "outperform",
    "strong", "bull", "bullish", "soar", "dividend", "revenue",
    "partnership", "breakthrough", "launch"
}

NEGATIVE_WORDS = {
    "plunge", "drop", "fall", "decline", "loss", "miss", "lower",
    "negative", "downgrade", "underperform", "weak", "bear", "bearish",
    "crash", "lawsuit", "investigation", "layoff", "debt", "risk",
    "warning", "bankruptcy"
}


class NewsAnalyzer:
    """
    Analyzes standard news items to compute an aggregated sentiment score.
    """

    @staticmethod
    def analyze(news_items: List[NewsItem]) -> NewsSignals:
        """
        Derives an aggregated sentiment score from news articles.
        
        Args:
            news_items: Cleaned list of NewsItem objects.
            
        Returns:
            A NewsSignals dataclass with a sentiment bounded between -1.0 and 1.0.
        """
        if not news_items:
            logger.debug("NewsAnalyzer | No news items provided. Returning neutral sentiment.")
            return NewsSignals(sentiment_score=0.0)

        total_sentiment = 0.0

        for item in news_items:
            # Combine title and summary for keyword scanning
            text = f"{item.title} {item.summary}".lower()
            
            # Simple tokenization by non-alphanumeric chars
            words = set(re.findall(r'\b[a-z]+\b', text))
            
            # Score individual article
            pos_matches = len(words.intersection(POSITIVE_WORDS))
            neg_matches = len(words.intersection(NEGATIVE_WORDS))
            
            # Sub-score for this article bounded by -1 to 1 based on dominant words
            if (pos_matches + neg_matches) > 0:
                article_score = (pos_matches - neg_matches) / (pos_matches + neg_matches)
            else:
                article_score = 0.0
                
            total_sentiment += article_score

        # Average the sentiment across all provided articles
        avg_sentiment = total_sentiment / len(news_items)

        logger.debug(
            "NewsAnalyzer | Derived sentiment score: %.3f from %d items",
            avg_sentiment, len(news_items)
        )

        return NewsSignals(sentiment_score=round(avg_sentiment, 4))
