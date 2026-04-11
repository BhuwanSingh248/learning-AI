"""
Data Layer — public API

External modules should import from here, never from sub-packages directly.

Example:
    from src.data import DataService, OpenBBProvider

    service = DataService(provider=OpenBBProvider())
"""

from src.data.services.data_service import DataService
from src.data.base.interfaces import IDataProvider
from src.data.providers.openbb_provider import OpenBBProvider
from src.data.models import PriceBar, NewsItem, CorporateAction

__all__ = [
    # Service (entry point for callers)
    "DataService",
    # Abstraction (for type hints / testing)
    "IDataProvider",
    # Concrete provider
    "OpenBBProvider",
    # Output contracts
    "PriceBar",
    "NewsItem",
    "CorporateAction",
]
