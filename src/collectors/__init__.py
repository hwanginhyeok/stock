"""Data collectors package — news, market data, and sentiment indicators.

Usage::

    from src.collectors.news import RSSNewsCollector
    from src.collectors.market import KoreaMarketCollector, USMarketCollector
    from src.collectors.sentiment import (
        CNNFearGreedCollector, PutCallRatioCollector,
        NaverCommunityCollector, StockTwitsCollector, AAIISentimentCollector,
    )
"""

from src.collectors.base import BaseCollector
from src.collectors.market import (
    BaseMarketCollector,
    KoreaMarketCollector,
    USMarketCollector,
)
from src.collectors.news import BaseNewsCollector, RSSNewsCollector, TitleDeduplicator
from src.collectors.sentiment import (
    AAIISentimentCollector,
    CNNFearGreedCollector,
    NaverCommunityCollector,
    PutCallRatioCollector,
    StockTwitsCollector,
)

__all__ = [
    "BaseCollector",
    "BaseNewsCollector",
    "RSSNewsCollector",
    "TitleDeduplicator",
    "BaseMarketCollector",
    "KoreaMarketCollector",
    "USMarketCollector",
    "CNNFearGreedCollector",
    "PutCallRatioCollector",
    "NaverCommunityCollector",
    "StockTwitsCollector",
    "AAIISentimentCollector",
]
