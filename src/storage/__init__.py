"""Storage layer — CRUD repositories for all domain entities.

Usage::

    from src.storage import NewsRepository, MarketSnapshotRepository
    repo = NewsRepository()
    items = repo.get_latest(limit=10)
"""

from src.storage.article_repository import ArticleRepository
from src.storage.base import BaseRepository
from src.storage.fact_repository import NewsFactRepository
from src.storage.community_sentiment_repository import CommunitySentimentRepository
from src.storage.market_snapshot_repository import MarketSnapshotRepository
from src.storage.news_repository import NewsRepository
from src.storage.ohlcv_repository import OHLCVRepository
from src.storage.research_report_repository import ResearchReportRepository
from src.storage.sentiment_repository import SentimentRepository
from src.storage.sns_post_repository import SNSPostRepository
from src.storage.stock_analysis_repository import StockAnalysisRepository
from src.storage.ontology_repository import (
    MarketReactionRepository,
    OntologyEntityRepository,
    OntologyEventRepository,
    OntologyLinkRepository,
    ThesisRepository,
)
from src.storage.geo_issue_repository import GeoIssueRepository
from src.storage.story_repository import NewsStoryLinkRepository, StoryThreadRepository
from src.storage.trends_repository import TrendsRepository

__all__ = [
    "BaseRepository",
    "NewsRepository",
    "MarketSnapshotRepository",
    "StockAnalysisRepository",
    "ArticleRepository",
    "SNSPostRepository",
    "ResearchReportRepository",
    "SentimentRepository",
    "CommunitySentimentRepository",
    "TrendsRepository",
    "OHLCVRepository",
    "StoryThreadRepository",
    "NewsStoryLinkRepository",
    "OntologyEntityRepository",
    "OntologyEventRepository",
    "OntologyLinkRepository",
    "MarketReactionRepository",
    "ThesisRepository",
    "NewsFactRepository",
    "GeoIssueRepository",
]
