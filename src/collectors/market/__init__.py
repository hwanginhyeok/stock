"""Market data collection sub-package.

Usage::

    from src.collectors.market import KoreaMarketCollector, USMarketCollector
    kr = KoreaMarketCollector()
    snapshots = kr.collect_indices()
"""

from src.collectors.market.base import BaseMarketCollector
from src.collectors.market.korea_collector import KoreaMarketCollector
from src.collectors.market.us_collector import USMarketCollector

__all__ = [
    "BaseMarketCollector",
    "KoreaMarketCollector",
    "USMarketCollector",
]
