"""
Output contract: News Data

Defines the canonical shape of a news article returned by any provider.
Providers must normalise their API responses to this format.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NewsItem:
    """
    A single news article associated with a stock symbol.

    Attributes:
        title:     Headline / title of the article
        summary:   Short summary or excerpt
        timestamp: Publication time (UTC)
        source:    Name of the news outlet (e.g. "Reuters", "Bloomberg")
    """

    title: str
    summary: str
    timestamp: datetime
    source: str
