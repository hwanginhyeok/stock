"""Database engine, ORM models, and session management."""

from __future__ import annotations

import json
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)

from src.core.config import PROJECT_ROOT, get_config
from src.core.exceptions import DatabaseError
from src.core.logger import get_logger

logger = get_logger(__name__)


def _utcnow() -> datetime:
    """Return current UTC time with timezone info."""
    return datetime.now(timezone.utc)


# ============================================================
# Declarative Base
# ============================================================


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""


# ============================================================
# ORM Models
# ============================================================


class NewsItemDB(Base):
    """ORM model for news items."""

    __tablename__ = "news_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(100), default="")
    url: Mapped[str] = mapped_column(String(1000), default="")
    category: Mapped[str] = mapped_column(String(50), default="")
    importance: Mapped[str] = mapped_column(String(20), default="medium")
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    related_tickers: Mapped[str] = mapped_column(Text, default="[]")
    related_sectors: Mapped[str] = mapped_column(Text, default="[]")
    market: Mapped[str] = mapped_column(String(10), default="korea")
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_news_created_at", "created_at"),
        Index("ix_news_market", "market"),
        Index("ix_news_category", "category"),
        Index("ix_news_importance", "importance"),
    )


class MarketSnapshotDB(Base):
    """ORM model for market snapshots."""

    __tablename__ = "market_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), default="")
    market: Mapped[str] = mapped_column(String(10), default="korea")
    index_name: Mapped[str] = mapped_column(String(50), default="")
    index_value: Mapped[float] = mapped_column(Float, default=0.0)
    change_percent: Mapped[float] = mapped_column(Float, default=0.0)
    volume: Mapped[int] = mapped_column(Integer, default=0)
    sentiment: Mapped[str] = mapped_column(String(20), default="neutral")
    top_gainers: Mapped[str] = mapped_column(Text, default="[]")
    top_losers: Mapped[str] = mapped_column(Text, default="[]")
    extra_data: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_snapshot_date", "date"),
        Index("ix_snapshot_market", "market"),
    )


class StockAnalysisDB(Base):
    """ORM model for stock analyses."""

    __tablename__ = "stock_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(100), default="")
    market: Mapped[str] = mapped_column(String(10), default="korea")
    date: Mapped[str] = mapped_column(String(10), default="")
    technical_score: Mapped[float] = mapped_column(Float, default=0.0)
    fundamental_score: Mapped[float] = mapped_column(Float, default=0.0)
    composite_score: Mapped[float] = mapped_column(Float, default=0.0)
    signals: Mapped[str] = mapped_column(Text, default="[]")
    technical_indicators: Mapped[str] = mapped_column(Text, default="{}")
    fundamental_data: Mapped[str] = mapped_column(Text, default="{}")
    recommendation: Mapped[str] = mapped_column(String(50), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_analysis_ticker", "ticker"),
        Index("ix_analysis_date", "date"),
        Index("ix_analysis_market", "market"),
        Index("ix_analysis_composite", "composite_score"),
    )


class ArticleDB(Base):
    """ORM model for generated articles."""

    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    article_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text, default="")
    related_tickers: Mapped[str] = mapped_column(Text, default="[]")
    model_used: Mapped[str] = mapped_column(String(50), default="")
    char_count: Mapped[int] = mapped_column(Integer, default=0)
    disclaimer_included: Mapped[bool] = mapped_column(Boolean, default=False)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_article_type", "article_type"),
        Index("ix_article_created_at", "created_at"),
    )


class SNSPostDB(Base):
    """ORM model for SNS posts."""

    __tablename__ = "sns_posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    platform: Mapped[str] = mapped_column(String(20))
    post_type: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    hashtags: Mapped[str] = mapped_column(Text, default="[]")
    media_paths: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    article_id: Mapped[str] = mapped_column(String(36), default="")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )
    platform_post_id: Mapped[str] = mapped_column(String(100), default="")
    error_message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_post_platform", "platform"),
        Index("ix_post_status", "status"),
        Index("ix_post_created_at", "created_at"),
    )


class ResearchReportDB(Base):
    """ORM model for research reports."""

    __tablename__ = "research_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    research_type: Mapped[str] = mapped_column(String(20))
    subject: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(500))
    executive_summary: Mapped[str] = mapped_column(Text, default="")
    sections: Mapped[str] = mapped_column(Text, default="[]")
    related_tickers: Mapped[str] = mapped_column(Text, default="[]")
    risk_factors: Mapped[str] = mapped_column(Text, default="[]")
    swot: Mapped[str] = mapped_column(Text, default="{}")
    data_sources: Mapped[str] = mapped_column(Text, default="[]")
    model_used: Mapped[str] = mapped_column(String(50), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_report_type", "research_type"),
        Index("ix_report_subject", "subject"),
        Index("ix_report_created_at", "created_at"),
    )


# ============================================================
# Engine & Session Management
# ============================================================


def _resolve_db_url(url: str) -> str:
    """Resolve relative SQLite paths to absolute paths from project root.

    Args:
        url: Database URL string.

    Returns:
        Resolved URL with absolute path for SQLite.
    """
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
        relative_path = url.replace("sqlite:///", "")
        absolute_path = PROJECT_ROOT / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{absolute_path}"
    return url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Get the singleton SQLAlchemy engine.

    Returns:
        SQLAlchemy Engine instance.
    """
    config = get_config()
    raw_url = config.database_url or config.database.url
    db_url = _resolve_db_url(raw_url)
    engine = create_engine(db_url, echo=config.database.echo)
    logger.info("database_engine_created", url=db_url)
    return engine


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Get the singleton session factory.

    Returns:
        SQLAlchemy sessionmaker instance.
    """
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def init_db() -> None:
    """Create all database tables.

    Raises:
        DatabaseError: If table creation fails.
    """
    try:
        Base.metadata.create_all(get_engine())
        logger.info("database_initialized")
    except Exception as e:
        raise DatabaseError(
            "Failed to initialize database",
            {"error": str(e)},
        ) from e


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional database session.

    Automatically commits on success, rolls back on error.

    Yields:
        SQLAlchemy Session instance.

    Raises:
        DatabaseError: If a database operation fails.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise DatabaseError(
            "Session error",
            {"error": str(e)},
        ) from e
    finally:
        session.close()


# ============================================================
# Conversion Helpers
# ============================================================

# Fields that are stored as JSON strings in the database
_JSON_FIELDS = frozenset({
    "related_tickers", "related_sectors", "top_gainers", "top_losers",
    "extra_data", "signals", "technical_indicators", "fundamental_data",
    "hashtags", "media_paths", "sections", "risk_factors", "swot",
    "data_sources",
})

# Lazy-initialized Pydantic -> ORM type mapping
_ORM_MAP: dict[type, type[Base]] = {}


def _get_orm_map() -> dict[type, type[Base]]:
    """Lazy-initialize the Pydantic-to-ORM type mapping."""
    if not _ORM_MAP:
        from src.core.models import (
            Article,
            MarketSnapshot,
            NewsItem,
            ResearchReport,
            SNSPost,
            StockAnalysis,
        )

        _ORM_MAP.update({
            NewsItem: NewsItemDB,
            MarketSnapshot: MarketSnapshotDB,
            StockAnalysis: StockAnalysisDB,
            Article: ArticleDB,
            SNSPost: SNSPostDB,
            ResearchReport: ResearchReportDB,
        })
    return _ORM_MAP


def pydantic_to_orm(model: Any) -> Base:
    """Convert a Pydantic domain model to its corresponding ORM model.

    Args:
        model: A Pydantic BaseEntity instance.

    Returns:
        The corresponding SQLAlchemy ORM instance.

    Raises:
        DatabaseError: If the model type has no ORM mapping.
    """
    orm_map = _get_orm_map()
    orm_class = orm_map.get(type(model))
    if orm_class is None:
        raise DatabaseError(
            f"No ORM mapping for {type(model).__name__}",
            {"model_type": type(model).__name__},
        )

    data = model.model_dump()
    for key, value in data.items():
        if key in _JSON_FIELDS and not isinstance(value, str):
            data[key] = json.dumps(value, ensure_ascii=False, default=str)

    return orm_class(**data)
