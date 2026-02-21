"""News collection sub-package.

Usage::

    from src.collectors.news import RSSNewsCollector
    collector = RSSNewsCollector()
    items = collector.collect()
"""

from src.collectors.news.base import BaseNewsCollector
from src.collectors.news.dedup import TitleDeduplicator
from src.collectors.news.rss_collector import RSSNewsCollector

__all__ = [
    "BaseNewsCollector",
    "TitleDeduplicator",
    "RSSNewsCollector",
]
