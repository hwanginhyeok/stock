"""News collection sub-package.

Usage::

    from src.collectors.news import RSSNewsCollector, NewsPipeline
    collector = RSSNewsCollector()
    items = collector.collect()

    pipeline = NewsPipeline()
    result = pipeline.run()
"""

from src.collectors.news.base import BaseNewsCollector
from src.collectors.news.dedup import TitleDeduplicator
from src.collectors.news.news_pipeline import NewsPipeline
from src.collectors.news.rss_collector import RSSNewsCollector
from src.collectors.news.ticker_extractor import TickerExtractor

__all__ = [
    "BaseNewsCollector",
    "NewsPipeline",
    "RSSNewsCollector",
    "TickerExtractor",
    "TitleDeduplicator",
]
