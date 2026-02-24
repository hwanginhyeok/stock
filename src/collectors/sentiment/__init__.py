"""Sentiment data collectors — external sentiment indices and community data."""

from src.collectors.sentiment.aaii_collector import AAIISentimentCollector
from src.collectors.sentiment.cnn_fear_greed_collector import CNNFearGreedCollector
from src.collectors.sentiment.google_trends_collector import GoogleTrendsCollector
from src.collectors.sentiment.naver_community_collector import NaverCommunityCollector
from src.collectors.sentiment.putcall_collector import PutCallRatioCollector
from src.collectors.sentiment.reddit_collector import RedditSentimentCollector
from src.collectors.sentiment.stocktwits_collector import StockTwitsCollector

__all__ = [
    "CNNFearGreedCollector",
    "PutCallRatioCollector",
    "NaverCommunityCollector",
    "StockTwitsCollector",
    "AAIISentimentCollector",
    "RedditSentimentCollector",
    "GoogleTrendsCollector",
]
