"""Domain models and enums for the Stock Rich Project."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================


class Market(StrEnum):
    """Stock market identifier."""

    KOREA = "korea"
    US = "us"


class Importance(StrEnum):
    """News importance level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MarketSentiment(StrEnum):
    """Market sentiment indicator."""

    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"


class ArticleType(StrEnum):
    """Article content type."""

    MORNING_BRIEFING = "morning_briefing"
    CLOSING_REVIEW = "closing_review"
    STOCK_ANALYSIS = "stock_analysis"
    WEEKLY_REVIEW = "weekly_review"


class SNSPlatform(StrEnum):
    """Social media platform."""

    INSTAGRAM = "instagram"
    X = "x"


class PostType(StrEnum):
    """SNS post type."""

    IMAGE = "image"
    CAROUSEL = "carousel"
    STORY = "story"
    TWEET = "tweet"
    THREAD = "thread"


class PostStatus(StrEnum):
    """SNS post lifecycle status."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class ResearchType(StrEnum):
    """Research report type."""

    STOCK = "stock"
    SECTOR = "sector"
    THEME = "theme"
    CROSS_MARKET = "cross_market"


class ClaudeTask(StrEnum):
    """Claude API task type for model/parameter selection."""

    GENERAL = "general"
    DEEP_ANALYSIS = "deep_analysis"
    SUMMARY = "summary"


# ============================================================
# Base models
# ============================================================


def _utcnow() -> datetime:
    """Return current UTC time with timezone info."""
    return datetime.now(timezone.utc)


class BaseEntity(BaseModel):
    """Base model with UUID id and ORM compatibility."""

    model_config = {"from_attributes": True}

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    def to_log_dict(self) -> dict[str, Any]:
        """Convert to a dict suitable for structured logging."""
        return self.model_dump(exclude_none=True)


class TimestampMixin(BaseModel):
    """Mixin that adds a created_at timestamp."""

    created_at: datetime = Field(default_factory=_utcnow)


# ============================================================
# Domain models
# ============================================================


class NewsItem(BaseEntity, TimestampMixin):
    """A collected news item."""

    title: str
    content: str = ""
    summary: str = ""
    source: str = ""
    url: str = ""
    category: str = ""
    importance: Importance = Importance.MEDIUM
    sentiment_score: float = 0.0
    related_tickers: list[str] = Field(default_factory=list)
    related_sectors: list[str] = Field(default_factory=list)
    market: Market = Market.KOREA
    published_at: datetime | None = None


class MarketSnapshot(BaseEntity, TimestampMixin):
    """Market state at a point in time."""

    date: str = ""
    market: Market = Market.KOREA
    index_name: str = ""
    index_value: float = 0.0
    change_percent: float = 0.0
    volume: int = 0
    sentiment: MarketSentiment = MarketSentiment.NEUTRAL
    top_gainers: list[dict[str, Any]] = Field(default_factory=list)
    top_losers: list[dict[str, Any]] = Field(default_factory=list)
    extra_data: dict[str, Any] = Field(default_factory=dict)


class StockAnalysis(BaseEntity, TimestampMixin):
    """Analysis result for a single stock."""

    ticker: str
    name: str = ""
    market: Market = Market.KOREA
    date: str = ""
    technical_score: float = 0.0
    fundamental_score: float = 0.0
    composite_score: float = 0.0
    signals: list[str] = Field(default_factory=list)
    technical_indicators: dict[str, Any] = Field(default_factory=dict)
    fundamental_data: dict[str, Any] = Field(default_factory=dict)
    recommendation: str = ""


class Article(BaseEntity, TimestampMixin):
    """Generated article content."""

    article_type: ArticleType
    title: str
    content: str
    summary: str = ""
    related_tickers: list[str] = Field(default_factory=list)
    model_used: str = ""
    char_count: int = 0
    disclaimer_included: bool = False
    quality_score: float = 0.0


class SNSPost(BaseEntity, TimestampMixin):
    """An SNS post (draft or published)."""

    platform: SNSPlatform
    post_type: PostType
    content: str
    hashtags: list[str] = Field(default_factory=list)
    media_paths: list[str] = Field(default_factory=list)
    status: PostStatus = PostStatus.DRAFT
    article_id: str = ""
    retry_count: int = 0
    published_at: datetime | None = None
    platform_post_id: str = ""
    error_message: str = ""


class ReportSection(BaseModel):
    """A section within a research report."""

    title: str
    content: str
    order: int = 0


class ResearchReport(BaseEntity, TimestampMixin):
    """In-depth research report."""

    research_type: ResearchType
    subject: str
    title: str
    executive_summary: str = ""
    sections: list[ReportSection] = Field(default_factory=list)
    related_tickers: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    swot: dict[str, list[str]] = Field(default_factory=dict)
    data_sources: list[str] = Field(default_factory=list)
    model_used: str = ""
