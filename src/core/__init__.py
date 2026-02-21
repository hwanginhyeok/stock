"""Core infrastructure module - shared across all agents.

Usage::

    from src.core import get_config, setup_logging, get_logger, ClaudeClient
    from src.core import init_db, get_session, pydantic_to_orm
    from src.core.models import NewsItem, Article, Market, ClaudeTask
"""

from src.core.claude_client import ClaudeClient, ClaudeResponse
from src.core.config import (
    AppConfig,
    ArticleTypeConfig,
    ClaudeModelConfig,
    ContentConfig,
    DatabaseConfig,
    LoggingConfig,
    MarketConfig,
    NewsSourcesConfig,
    RetryConfig,
    ScheduleConfig,
    SNSConfig,
    get_config,
)
from src.core.database import (
    Base,
    ArticleDB,
    MarketSnapshotDB,
    NewsItemDB,
    ResearchReportDB,
    SNSPostDB,
    StockAnalysisDB,
    get_engine,
    get_session,
    get_session_factory,
    init_db,
    pydantic_to_orm,
)
from src.core.exceptions import (
    AnalysisError,
    APIError,
    ClaudeAPIError,
    CollectionError,
    ConfigError,
    ContentError,
    DatabaseError,
    PublishError,
    RateLimitError,
    StockRichError,
)
from src.core.logger import get_logger, setup_logging
from src.core.models import (
    Article,
    ArticleType,
    BaseEntity,
    ClaudeTask,
    Importance,
    Market,
    MarketSentiment,
    MarketSnapshot,
    NewsItem,
    PostStatus,
    PostType,
    ReportSection,
    ResearchReport,
    ResearchType,
    SNSPlatform,
    SNSPost,
    StockAnalysis,
    TimestampMixin,
)

__all__ = [
    # config
    "AppConfig",
    "ArticleTypeConfig",
    "ClaudeModelConfig",
    "ContentConfig",
    "DatabaseConfig",
    "LoggingConfig",
    "MarketConfig",
    "NewsSourcesConfig",
    "RetryConfig",
    "ScheduleConfig",
    "SNSConfig",
    "get_config",
    # logger
    "setup_logging",
    "get_logger",
    # exceptions
    "StockRichError",
    "ConfigError",
    "APIError",
    "ClaudeAPIError",
    "RateLimitError",
    "CollectionError",
    "AnalysisError",
    "ContentError",
    "PublishError",
    "DatabaseError",
    # models - enums
    "Market",
    "Importance",
    "MarketSentiment",
    "ArticleType",
    "SNSPlatform",
    "PostType",
    "PostStatus",
    "ResearchType",
    "ClaudeTask",
    # models - base
    "BaseEntity",
    "TimestampMixin",
    # models - domain
    "NewsItem",
    "MarketSnapshot",
    "StockAnalysis",
    "Article",
    "SNSPost",
    "ReportSection",
    "ResearchReport",
    # database
    "Base",
    "NewsItemDB",
    "MarketSnapshotDB",
    "StockAnalysisDB",
    "ArticleDB",
    "SNSPostDB",
    "ResearchReportDB",
    "get_engine",
    "get_session_factory",
    "init_db",
    "get_session",
    "pydantic_to_orm",
    # claude client
    "ClaudeClient",
    "ClaudeResponse",
]
