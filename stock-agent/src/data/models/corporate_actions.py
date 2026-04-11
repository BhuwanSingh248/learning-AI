"""
Output contract: Corporate Actions

Defines the canonical shape of a corporate action event returned by
any provider (dividends, earnings, stock splits, etc.).
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class ActionType(str, Enum):
    """Supported types of corporate actions."""

    DIVIDEND = "dividend"
    EARNINGS = "earnings"
    SPLIT = "split"


@dataclass(frozen=True)
class CorporateAction:
    """
    A single corporate action event for a stock symbol.

    Attributes:
        type:  Category of the action (dividend / earnings / split)
        date:  Event date (ex-dividend date, earnings date, etc.)
        value: Numeric value associated with the event, e.g.:
                 - dividend amount per share
                 - EPS estimate for earnings
                 - split ratio (e.g. 4.0 for a 4-for-1 split)
               May be None when no numeric value is applicable.
    """

    type: ActionType
    date: date
    value: Optional[float] = None
