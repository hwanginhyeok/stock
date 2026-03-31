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


class SentimentRecordDB(Base):
    """ORM model for historical sentiment indicators."""

    __tablename__ = "sentiment_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10))
    source: Mapped[str] = mapped_column(String(30))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    level: Mapped[str] = mapped_column(String(30), default="")
    components: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_sentiment_date", "date"),
        Index("ix_sentiment_source", "source"),
        Index("ix_sentiment_date_source", "date", "source", unique=True),
    )


class CommunitySentimentDB(Base):
    """ORM model for per-ticker community sentiment."""

    __tablename__ = "community_sentiment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10))
    ticker: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(100), default="")
    market: Mapped[str] = mapped_column(String(10), default="us")
    source: Mapped[str] = mapped_column(String(30), default="")
    posts_count: Mapped[int] = mapped_column(Integer, default=0)
    bullish_ratio: Mapped[float] = mapped_column(Float, default=0.5)
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.5)
    sentiment: Mapped[str] = mapped_column(String(20), default="Neutral")
    details: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_community_date", "date"),
        Index("ix_community_ticker", "ticker"),
        Index("ix_community_source", "source"),
    )


class OHLCVDB(Base):
    """ORM model for historical OHLCV price data."""

    __tablename__ = "ohlcv_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10))
    ticker: Mapped[str] = mapped_column(String(20))
    market: Mapped[str] = mapped_column(String(10), default="us")
    open: Mapped[float] = mapped_column(Float, default=0.0)
    high: Mapped[float] = mapped_column(Float, default=0.0)
    low: Mapped[float] = mapped_column(Float, default=0.0)
    close: Mapped[float] = mapped_column(Float, default=0.0)
    volume: Mapped[int] = mapped_column(Integer, default=0)
    adjusted_close: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_ohlcv_date", "date"),
        Index("ix_ohlcv_ticker", "ticker"),
        Index("ix_ohlcv_ticker_date", "ticker", "date", unique=True),
    )


class StoryThreadDB(Base):
    """ORM model for news story threads."""

    __tablename__ = "story_threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text, default="")
    market: Mapped[str] = mapped_column(String(10), default="korea")
    status: Mapped[str] = mapped_column(String(20), default="active")
    related_tickers: Mapped[str] = mapped_column(Text, default="[]")
    article_count: Mapped[int] = mapped_column(Integer, default=0)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_story_status", "status"),
        Index("ix_story_market", "market"),
        Index("ix_story_last_updated", "last_updated_at"),
    )


class NewsStoryLinkDB(Base):
    """ORM model linking news items to story threads."""

    __tablename__ = "news_story_links"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    news_id: Mapped[str] = mapped_column(String(36))
    story_id: Mapped[str] = mapped_column(String(36))
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_link_news_id", "news_id"),
        Index("ix_link_story_id", "story_id"),
        Index("ix_link_news_story", "news_id", "story_id", unique=True),
    )


class OntologyEntityDB(Base):
    """ORM model for ontology entities."""

    __tablename__ = "ontology_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    entity_type: Mapped[str] = mapped_column(String(30), default="company")
    ticker: Mapped[str] = mapped_column(String(20), default="")
    market: Mapped[str] = mapped_column(String(10), default="korea")
    properties: Mapped[str] = mapped_column(Text, default="{}")
    aliases: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_ont_entity_name", "name"),
        Index("ix_ont_entity_type", "entity_type"),
        Index("ix_ont_entity_ticker", "ticker"),
        Index("ix_ont_entity_market", "market"),
    )


class OntologyEventDB(Base):
    """ORM model for ontology events."""

    __tablename__ = "ontology_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text, default="")
    event_type: Mapped[str] = mapped_column(String(30), default="macro")
    severity: Mapped[str] = mapped_column(String(20), default="moderate")
    market: Mapped[str] = mapped_column(String(10), default="korea")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    last_article_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    status: Mapped[str] = mapped_column(String(20), default="developing")
    article_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_ont_event_type", "event_type"),
        Index("ix_ont_event_severity", "severity"),
        Index("ix_ont_event_market", "market"),
        Index("ix_ont_event_status", "status"),
        Index("ix_ont_event_started", "started_at"),
        Index("ix_ont_event_last_article", "last_article_at"),
    )


class OntologyLinkDB(Base):
    """ORM model for ontology links (relationships between objects)."""

    __tablename__ = "ontology_links"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    link_type: Mapped[str] = mapped_column(String(20))
    source_type: Mapped[str] = mapped_column(String(20))
    source_id: Mapped[str] = mapped_column(String(36))
    target_type: Mapped[str] = mapped_column(String(20))
    target_id: Mapped[str] = mapped_column(String(36))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    evidence: Mapped[str] = mapped_column(Text, default="")
    source_urls: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_ont_link_type", "link_type"),
        Index("ix_ont_link_source", "source_type", "source_id"),
        Index("ix_ont_link_target", "target_type", "target_id"),
        Index(
            "ix_ont_link_unique",
            "link_type", "source_type", "source_id", "target_type", "target_id",
            unique=True,
        ),
    )


class GeoIssueDB(Base):
    """ORM model for geopolitical issues."""

    __tablename__ = "geo_issues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(String(20), default="moderate")
    status: Mapped[str] = mapped_column(String(20), default="active")
    event_ids: Mapped[str] = mapped_column(Text, default="[]")
    entity_ids: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_geo_issue_status", "status"),
        Index("ix_geo_issue_severity", "severity"),
    )


class MarketReactionDB(Base):
    """ORM model for market reactions."""

    __tablename__ = "ontology_reactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36))
    entity_id: Mapped[str] = mapped_column(String(36))
    reaction_type: Mapped[str] = mapped_column(String(20), default="price")
    magnitude: Mapped[float] = mapped_column(Float, default=0.0)
    direction: Mapped[str] = mapped_column(String(20), default="neutral")
    details: Mapped[str] = mapped_column(Text, default="{}")
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_ont_reaction_event", "event_id"),
        Index("ix_ont_reaction_entity", "entity_id"),
        Index("ix_ont_reaction_observed", "observed_at"),
    )


class ThesisDB(Base):
    """ORM model for investment theses."""

    __tablename__ = "ontology_theses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text, default="")
    market: Mapped[str] = mapped_column(String(10), default="korea")
    status: Mapped[str] = mapped_column(String(20), default="active")
    related_tickers: Mapped[str] = mapped_column(Text, default="[]")
    strength: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_ont_thesis_status", "status"),
        Index("ix_ont_thesis_market", "market"),
        Index("ix_ont_thesis_strength", "strength"),
    )


class NewsFactDB(Base):
    """ORM model for extracted news facts."""

    __tablename__ = "news_facts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    news_id: Mapped[str] = mapped_column(String(36))
    fact_type: Mapped[str] = mapped_column(String(20), default="numerical")
    claim: Mapped[str] = mapped_column(Text)
    entities: Mapped[str] = mapped_column(Text, default="[]")
    tickers: Mapped[str] = mapped_column(Text, default="[]")
    numbers: Mapped[str] = mapped_column(Text, default="{}")
    source_quote: Mapped[str] = mapped_column(Text, default="")
    market: Mapped[str] = mapped_column(String(10), default="korea")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
    )
    extracted_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_fact_news_id", "news_id"),
        Index("ix_fact_type", "fact_type"),
        Index("ix_fact_market", "market"),
        Index("ix_fact_confidence", "confidence"),
        Index("ix_fact_published_at", "published_at"),
        Index("ix_fact_extracted_at", "extracted_at"),
    )


class FirstPrincipleAnalysisDB(Base):
    """ORM model for first-principles analyses."""

    __tablename__ = "first_principle_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36))
    event_title: Mapped[str] = mapped_column(String(500), default="")
    conventional_wisdom: Mapped[str] = mapped_column(Text, default="")
    fundamental_truths: Mapped[str] = mapped_column(Text, default="[]")
    gap: Mapped[str] = mapped_column(Text, default="")
    opportunity: Mapped[str] = mapped_column(Text, default="")
    related_fact_ids: Mapped[str] = mapped_column(Text, default="[]")
    market: Mapped[str] = mapped_column(String(10), default="korea")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_fpa_event_id", "event_id"),
        Index("ix_fpa_market", "market"),
        Index("ix_fpa_status", "status"),
    )


class TrendsRecordDB(Base):
    """ORM model for Google Trends interest data."""

    __tablename__ = "trends_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    date: Mapped[str] = mapped_column(String(10))
    keyword: Mapped[str] = mapped_column(String(100))
    geo: Mapped[str] = mapped_column(String(10), default="")
    current_interest: Mapped[int] = mapped_column(Integer, default=0)
    average_interest: Mapped[float] = mapped_column(Float, default=0.0)
    spike_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    trend_direction: Mapped[str] = mapped_column(String(20), default="Stable")
    attention_level: Mapped[str] = mapped_column(String(20), default="Normal")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_trends_date", "date"),
        Index("ix_trends_keyword", "keyword"),
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
    "data_sources", "components", "details",
    # StoryThread uses related_tickers (already listed above)
    "properties", "aliases",  # OntologyEntity
    "source_urls",  # OntologyLink
    "event_ids", "entity_ids",  # GeoIssue
    "entities", "tickers", "numbers",  # NewsFact
    "fundamental_truths", "related_fact_ids",  # FirstPrincipleAnalysis
})

# Lazy-initialized Pydantic -> ORM type mapping
_ORM_MAP: dict[type, type[Base]] = {}


def _get_orm_map() -> dict[type, type[Base]]:
    """Lazy-initialize the Pydantic-to-ORM type mapping."""
    if not _ORM_MAP:
        from src.core.models import (
            Article,
            CommunitySentiment,
            GeoIssue,
            MarketReaction,
            MarketSnapshot,
            FirstPrincipleAnalysis,
            NewsFact,
            NewsItem,
            NewsStoryLink,
            OHLCVRecord,
            OntologyEntity,
            OntologyEvent,
            OntologyLink,
            ResearchReport,
            SNSPost,
            SentimentRecord,
            StockAnalysis,
            StoryThread,
            Thesis,
            TrendsRecord,
        )

        _ORM_MAP.update({
            NewsItem: NewsItemDB,
            MarketSnapshot: MarketSnapshotDB,
            StockAnalysis: StockAnalysisDB,
            Article: ArticleDB,
            SNSPost: SNSPostDB,
            ResearchReport: ResearchReportDB,
            SentimentRecord: SentimentRecordDB,
            CommunitySentiment: CommunitySentimentDB,
            TrendsRecord: TrendsRecordDB,
            OHLCVRecord: OHLCVDB,
            StoryThread: StoryThreadDB,
            NewsStoryLink: NewsStoryLinkDB,
            OntologyEntity: OntologyEntityDB,
            OntologyEvent: OntologyEventDB,
            OntologyLink: OntologyLinkDB,
            GeoIssue: GeoIssueDB,
            MarketReaction: MarketReactionDB,
            Thesis: ThesisDB,
            NewsFact: NewsFactDB,
            FirstPrincipleAnalysis: FirstPrincipleAnalysisDB,
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
