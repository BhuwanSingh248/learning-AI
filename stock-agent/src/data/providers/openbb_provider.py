"""
OpenBB Provider — concrete implementation of IDataProvider.

Single Responsibility:
  This is the ONLY place in the entire codebase that imports or calls OpenBB.
  All other modules receive data through the IDataProvider abstraction.

Design principles applied:
  SRP  — This module ONLY fetches and maps data. No cleaning, no scoring.
  DIP  — Callers depend on IDataProvider, not this class directly.
  OCP  — New providers (FinnhubProvider, etc.) just implement IDataProvider;
          this file never needs to change for that.

Endpoints used:
  Price            → obb.equity.price.historical()
  News             → obb.news.company()
  Dividends        → obb.equity.calendar.dividend()
  Earnings         → obb.equity.calendar.earnings()
  Splits           → obb.equity.calendar.splits()
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import List

from openbb import obb

from src.data.base.interfaces import IDataProvider
from src.data.models.corporate_actions import ActionType, CorporateAction
from src.data.models.news import NewsItem
from src.data.models.price import PriceBar

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper: safe attribute extraction from OBB result rows
# ---------------------------------------------------------------------------

def _get(row, *attrs, default=None):
    """
    Walk a chain of attribute names on `row`, returning `default` on any miss.
    Handles both object-style (OBBject rows) and dict-style rows.
    """
    obj = row
    for attr in attrs:
        if obj is None:
            return default
        if isinstance(obj, dict):
            obj = obj.get(attr, default)
        else:
            obj = getattr(obj, attr, default)
    return obj if obj is not None else default


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class OpenBBProvider(IDataProvider):
    """
    Fetches market data from OpenBB and maps it to the standard contracts
    defined in src/data/models/.

    Responsibilities (what this class does):
      ✅ Calls OpenBB endpoints
      ✅ Maps raw response rows → typed model objects
      ✅ Basic error isolation (logs + returns empty list on failure)

    NOT responsible for (what this class never does):
      ❌ Cleaning / normalising values
      ❌ Removing nulls or outliers
      ❌ Computing features or indicators
      ❌ Business logic of any kind
    """

    # ------------------------------------------------------------------ #
    # Price Data                                                           #
    # ------------------------------------------------------------------ #

    def get_price_data(self, symbol: str, lookback: int) -> List[PriceBar]:
        """
        Fetch historical OHLCV bars for `symbol` over the last `lookback` days.

        Maps:  obb.equity.price.historical() → List[PriceBar]

        Args:
            symbol:   Ticker symbol (e.g. "AAPL")
            lookback: Number of calendar days to look back from today

        Returns:
            List[PriceBar] in ascending date order.
            Returns an empty list if OpenBB raises any error.
        """
        start_date = (date.today() - timedelta(days=lookback)).isoformat()
        end_date   = date.today().isoformat()

        logger.debug(
            "OpenBBProvider.get_price_data | symbol=%s start=%s end=%s",
            symbol, start_date, end_date,
        )

        try:
            result = obb.equity.price.historical(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                provider="yfinance",
            )
            rows = result.results or []
        except Exception as exc:
            logger.error(
                "OpenBBProvider.get_price_data failed for %s: %s", symbol, exc
            )
            return []

        bars: List[PriceBar] = []
        for row in rows:
            try:
                bars.append(
                    PriceBar(
                        date=_get(row, "date").date()
                              if hasattr(_get(row, "date"), "date")
                              else _get(row, "date"),
                        open=float(_get(row, "open", default=0.0)),
                        high=float(_get(row, "high", default=0.0)),
                        low=float(_get(row, "low",  default=0.0)),
                        close=float(_get(row, "close", default=0.0)),
                        volume=int(_get(row, "volume", default=0)),
                    )
                )
            except Exception as exc:
                logger.warning("Skipping malformed price row for %s: %s", symbol, exc)
                continue

        logger.info(
            "OpenBBProvider.get_price_data | symbol=%s → %d bars", symbol, len(bars)
        )
        return sorted(bars, key=lambda b: b.date)

    # ------------------------------------------------------------------ #
    # News                                                                 #
    # ------------------------------------------------------------------ #

    def get_news(self, symbol: str) -> List[NewsItem]:
        """
        Fetch recent news articles related to `symbol`.

        Maps:  obb.news.company() → List[NewsItem]

        Args:
            symbol: Ticker symbol (e.g. "AAPL")

        Returns:
            List[NewsItem], most recent first.
            Returns an empty list if OpenBB raises any error.
        """
        logger.debug("OpenBBProvider.get_news | symbol=%s", symbol)

        try:
            result = obb.news.company(
                symbol=symbol,
                limit=20,
                provider="yfinance",
            )
            rows = result.results or []
        except Exception as exc:
            logger.error(
                "OpenBBProvider.get_news failed for %s: %s", symbol, exc
            )
            return []

        items: List[NewsItem] = []
        for row in rows:
            try:
                raw_ts = _get(row, "date") or _get(row, "published_at") or _get(row, "publishedAt")

                # Normalise timestamp → UTC-aware datetime
                if isinstance(raw_ts, datetime):
                    ts = raw_ts if raw_ts.tzinfo else raw_ts.replace(tzinfo=timezone.utc)
                elif isinstance(raw_ts, date):
                    ts = datetime(raw_ts.year, raw_ts.month, raw_ts.day, tzinfo=timezone.utc)
                else:
                    ts = datetime.now(tz=timezone.utc)

                items.append(
                    NewsItem(
                        title=str(_get(row, "title", default="")),
                        summary=str(_get(row, "text") or _get(row, "summary") or ""),
                        timestamp=ts,
                        source=str(_get(row, "source", default="unknown")),
                    )
                )
            except Exception as exc:
                logger.warning("Skipping malformed news row for %s: %s", symbol, exc)
                continue

        logger.info(
            "OpenBBProvider.get_news | symbol=%s → %d articles", symbol, len(items)
        )
        # Most recent first
        return sorted(items, key=lambda n: n.timestamp, reverse=True)

    # ------------------------------------------------------------------ #
    # Corporate Actions                                                    #
    # ------------------------------------------------------------------ #

    def get_corporate_actions(self, symbol: str) -> List[CorporateAction]:
        """
        Fetch recent corporate actions: dividends, earnings, and splits.

        Endpoint mapping (chosen for max free-tier coverage):
          Dividends → obb.equity.fundamental.dividends(provider="yfinance")
                       ✅ No API key required
          Earnings  → obb.equity.calendar.earnings(provider="fmp")
                       ⚠️  Requires FMP_API_KEY in environment
          Splits    → obb.equity.fundamental.historical_splits(provider="fmp")
                       ⚠️  Requires FMP_API_KEY in environment

        Each sub-fetch is isolated: if one fails (e.g. missing API key),
        the others still return results.

        Args:
            symbol: Ticker symbol (e.g. "AAPL")

        Returns:
            List[CorporateAction] in ascending date order.
            Returns an empty list if all fetches fail.
        """
        logger.debug("OpenBBProvider.get_corporate_actions | symbol=%s", symbol)
        actions: List[CorporateAction] = []

        # ---- Dividends (yfinance — no key needed) ---- #
        try:
            result = obb.equity.fundamental.dividends(
                symbol=symbol,
                provider="yfinance",
            )
            for row in (result.results or []):
                try:
                    actions.append(
                        CorporateAction(
                            type=ActionType.DIVIDEND,
                            date=self._to_date(
                                _get(row, "ex_dividend_date") or _get(row, "date")
                            ),
                            value=float(_get(row, "amount", default=0.0)),
                        )
                    )
                except Exception as exc:
                    logger.warning("Skipping malformed dividend row for %s: %s", symbol, exc)
        except Exception as exc:
            logger.error("OpenBBProvider: dividend fetch failed for %s: %s", symbol, exc)

        # ---- Earnings (fmp — requires FMP_API_KEY) ---- #
        try:
            result = obb.equity.calendar.earnings(symbol=symbol, provider="fmp")
            for row in (result.results or []):
                try:
                    actions.append(
                        CorporateAction(
                            type=ActionType.EARNINGS,
                            date=self._to_date(
                                _get(row, "date") or _get(row, "report_date")
                            ),
                            value=float(_get(row, "eps_estimate") or 0.0),
                        )
                    )
                except Exception as exc:
                    logger.warning("Skipping malformed earnings row for %s: %s", symbol, exc)
        except Exception as exc:
            logger.warning(
                "OpenBBProvider: earnings fetch failed for %s (FMP key required?): %s",
                symbol, exc,
            )

        # ---- Splits (fmp — requires FMP_API_KEY) ---- #
        try:
            result = obb.equity.fundamental.historical_splits(
                symbol=symbol, provider="fmp"
            )
            for row in (result.results or []):
                try:
                    # ratio = numerator/denominator  (e.g. 4.0 for a 4-for-1 split)
                    num = float(_get(row, "numerator") or 0.0)
                    den = float(_get(row, "denominator") or 1.0)
                    ratio = round(num / den, 4) if den else 0.0
                    actions.append(
                        CorporateAction(
                            type=ActionType.SPLIT,
                            date=self._to_date(_get(row, "date")),
                            value=ratio,
                        )
                    )
                except Exception as exc:
                    logger.warning("Skipping malformed split row for %s: %s", symbol, exc)
        except Exception as exc:
            logger.warning(
                "OpenBBProvider: splits fetch failed for %s (FMP key required?): %s",
                symbol, exc,
            )

        logger.info(
            "OpenBBProvider.get_corporate_actions | symbol=%s → %d actions",
            symbol, len(actions),
        )
        return sorted(actions, key=lambda a: a.date)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_date(value) -> date:
        """
        Convert an OpenBB date value (date, datetime, or ISO-string) to
        a plain Python date. Raises ValueError if conversion is impossible.
        """
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return date.fromisoformat(value[:10])
        raise ValueError(f"Cannot convert {value!r} to date")
