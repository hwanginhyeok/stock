"""Storage layer — CRUD repositories for all domain entities.

Usage::

    from src.storage import NewsRepository, MarketSnapshotRepository
    repo = NewsRepository()
    items = repo.get_latest(limit=10)
"""

from src.storage.article_repository import ArticleRepository
from src.storage.base import BaseRepository
from src.storage.market_snapshot_repository import MarketSnapshotRepository
from src.storage.news_repository import NewsRepository
from src.storage.research_report_repository import ResearchReportRepository
from src.storage.sns_post_repository import SNSPostRepository
from src.storage.stock_analysis_repository import StockAnalysisRepository

__all__ = [
    "BaseRepository",
    "NewsRepository",
    "MarketSnapshotRepository",
    "StockAnalysisRepository",
    "ArticleRepository",
    "SNSPostRepository",
    "ResearchReportRepository",
]
