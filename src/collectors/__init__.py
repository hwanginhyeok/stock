"""Data collectors package — news and market data.

Usage::

    from src.collectors.news import RSSNewsCollector
    from src.collectors.market import KoreaMarketCollector, USMarketCollector
"""

from src.collectors.base import BaseCollector
from src.collectors.market import (
    BaseMarketCollector,
    KoreaMarketCollector,
    USMarketCollector,
)
from src.collectors.news import BaseNewsCollector, RSSNewsCollector, TitleDeduplicator

__all__ = [
    "BaseCollector",
    "BaseNewsCollector",
    "RSSNewsCollector",
    "TitleDeduplicator",
    "BaseMarketCollector",
    "KoreaMarketCollector",
    "USMarketCollector",
]
