"""
Data Validation and Standardization Layer.

Responsibilities:
  - Take raw structured data from DataLayer (PriceBar, NewsItem, CorporateAction).
  - Apply validation rules (e.g. drop 0.0 prices, missing dates).
  - Standardize formats (e.g. convert PriceBars to Pandas DataFrame for downstream feature engineering).
  - Ensure data is clean and consistent.
  - No business logic, no indicator computation.
"""

from typing import List, Optional
import pandas as pd
from datetime import datetime, timezone

from src.config.logger import setup_logger
from src.data.models.price import PriceBar
from src.data.models.news import NewsItem
from src.data.models.corporate_actions import CorporateAction

logger = setup_logger(__name__)


class DataValidator:
    """
    Validates and standardizes data coming from the DataService.
    """

    @staticmethod
    def clean_price_data(bars: List[PriceBar]) -> pd.DataFrame:
        """
        Validates and standardizes historical price data.
        
        Rules:
        - Converts list of PriceBar objects to a Pandas DataFrame.
        - Ensures dates are datetime objects and sets date as index.
        - Removes rows with 0.0 or missing crucial numeric fields (open, high, low, close).
        - Ensures data types: prices -> float, volume -> int.
        
        Args:
            bars: List of PriceBar objects.
            
        Returns:
            A clean Pandas DataFrame containing the price data, sorted by date.
        """
        if not bars:
            logger.warning("DataValidator.clean_price_data | Empty price data received.")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "date": pd.to_datetime(b.date),
                "open": float(b.open),
                "high": float(b.high),
                "low": float(b.low),
                "close": float(b.close),
                "volume": int(b.volume)
            }
            for b in bars
        ])

        # Drop rows where close price is 0 (invalid data)
        invalid_mask = (df["close"] <= 0) | (df["open"] <= 0) | (df["high"] <= 0) | (df["low"] <= 0)
        invalid_count = invalid_mask.sum()
        if invalid_count > 0:
            logger.info("DataValidator.clean_price_data | Dropping %d rows with invalid / zero prices.", invalid_count)
            df = df[~invalid_mask]

        if df.empty:
            return df

        # Handle missing (NaN) values simply by dropping them
        df = df.dropna()

        # Standardize: Set date as index and sort
        df.set_index("date", inplace=True)
        df.sort_index(ascending=True, inplace=True)

        logger.debug("DataValidator.clean_price_data | Standardized %d rows successfully.", len(df))
        return df

    @staticmethod
    def clean_news_data(news: List[NewsItem]) -> List[NewsItem]:
        """
        Validates and standardizes news articles.
        
        Rules:
        - Removes items with empty or purely whitespace titles.
        - Removes duplicate articles (by comparing title strings).
        - Ensures all timestamps are UTC-aware.
        
        Args:
            news: List of raw NewsItem objects.
            
        Returns:
            A cleaned list of NewsItem objects sorted by timestamp descending.
        """
        if not news:
            return []

        cleaned: List[NewsItem] = []
        seen_titles = set()

        for item in news:
            title = (item.title or "").strip()
            # Rule: remove empty titles
            if not title:
                continue

            # Rule: remove duplicates based on title
            lower_title = title.lower()
            if lower_title in seen_titles:
                continue
            seen_titles.add(lower_title)

            # Rule: Ensure timezone is UTC-aware
            ts = item.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            cleaned.append(
                NewsItem(
                    title=title,
                    summary=(item.summary or "").strip(),
                    timestamp=ts,
                    source=(item.source or "unknown").strip()
                )
            )

        # Ensure correct sorting: most recent first
        cleaned.sort(key=lambda x: x.timestamp, reverse=True)
        
        logger.debug("DataValidator.clean_news_data | Retained %d unique valid articles out of %d.", len(cleaned), len(news))
        return cleaned

    @staticmethod
    def clean_corporate_actions(actions: List[CorporateAction]) -> List[CorporateAction]:
        """
        Validates and standardizes corporate actions.
        
        Rules:
        - Ignore events where date is missing (already typed as date, but checking safety).
        - Ensure numeric values are reasonable floats (or gracefully handles None).
        - Sort chronologically.
        
        Args:
            actions: List of CorporateAction objects.
            
        Returns:
            A cleaned list of CorporateAction objects.
        """
        if not actions:
            return []

        cleaned: List[CorporateAction] = []
        
        for item in actions:
            if not item.date:
                continue

            # Skip events where value is supposed to be numeric but is invalid
            val = item.value
            if val is not None:
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    logger.warning("DataValidator.clean_corporate_actions | Invalid value for event: %1", item)
                    continue

            cleaned.append(
                CorporateAction(
                    type=item.type,
                    date=item.date,
                    value=val
                )
            )

        # Sort chronologically ascending
        cleaned.sort(key=lambda x: x.date)
        
        logger.debug("DataValidator.clean_corporate_actions | Validated %d corporate actions.", len(cleaned))
        return cleaned
