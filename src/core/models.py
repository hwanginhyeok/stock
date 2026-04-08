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


class StoryStatus(StrEnum):
    """Story thread lifecycle status."""

    ACTIVE = "active"
    STALE = "stale"
    CLOSED = "closed"


class FactType(StrEnum):
    """News fact claim type."""

    NUMERICAL = "numerical"
    EVENT = "event"
    POLICY = "policy"
    EARNINGS = "earnings"
    FORECAST = "forecast"
    DEAL = "deal"


class EntityType(StrEnum):
    """Ontology entity type."""

    COMPANY = "company"
    PERSON = "person"
    ASSET = "asset"
    INSTITUTION = "institution"
    SECTOR = "sector"
    COUNTRY = "country"
    PROXY = "proxy"
    COMMODITY = "commodity"


class EventType(StrEnum):
    """Ontology event type.

    Geo: diplomatic, military, sanctions, energy, trade, territorial, war, policy
    Stock: earnings, analyst, product, regulatory, macro, deal, sector
    """

    # 공통
    MACRO = "macro"
    DEAL = "deal"
    POLICY = "policy"
    # Geo 전용
    WAR = "war"
    MILITARY = "military"
    DIPLOMATIC = "diplomatic"
    SANCTIONS = "sanctions"
    ENERGY = "energy"
    TRADE = "trade"
    TERRITORIAL = "territorial"
    # Stock 전용
    EARNINGS = "earnings"
    ANALYST = "analyst"
    PRODUCT = "product"
    REGULATORY = "regulatory"
    SECTOR = "sector"
    REGULATION = "regulation"  # 하위호환


class Severity(StrEnum):
    """Event severity level."""

    CRITICAL = "critical"
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"


class EventStatus(StrEnum):
    """Ontology event lifecycle status."""

    DEVELOPING = "developing"
    RESOLVED = "resolved"
    STALE = "stale"
    ESCALATING = "escalating"


class LinkType(StrEnum):
    """Ontology link type between objects."""

    MENTIONS = "mentions"
    TRIGGERS = "triggers"
    INVOLVES = "involves"
    IMPACTS = "impacts"
    REACTS_TO = "reacts_to"
    SUPPORTS = "supports"
    ALLY = "ally"
    HOSTILE = "hostile"
    PROXY = "proxy"
    TRADE = "trade"
    SUPPLY = "supply"
    SANCTIONS = "sanctions"
    BLOCKADE = "blockade"
    ATTACK = "attack"
    BASE = "base"


class GeoIssueStatus(StrEnum):
    """Geopolitical issue lifecycle status."""

    ACTIVE = "active"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


class ThesisStatus(StrEnum):
    """Investment thesis lifecycle status."""

    ACTIVE = "active"
    INVALIDATED = "invalidated"
    ARCHIVED = "archived"


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


class SentimentSource(StrEnum):
    """Sentiment data source identifier."""

    CNN_FEAR_GREED = "cnn_fear_greed"
    CBOE_PUTCALL_TOTAL = "cboe_putcall_total"
    CBOE_PUTCALL_EQUITY = "cboe_putcall_equity"
    CBOE_PUTCALL_INDEX = "cboe_putcall_index"
    AAII_SURVEY = "aaii_survey"
    CUSTOM_FEAR_GREED = "custom_fear_greed"


class SentimentRecord(BaseEntity, TimestampMixin):
    """Historical sentiment indicator record (market-level, daily)."""

    date: str
    source: SentimentSource
    score: float = 0.0
    level: str = ""
    components: dict[str, Any] = Field(default_factory=dict)


class CommunitySentiment(BaseEntity, TimestampMixin):
    """Per-ticker community sentiment snapshot."""

    date: str
    ticker: str
    name: str = ""
    market: Market = Market.US
    source: str = ""
    posts_count: int = 0
    bullish_ratio: float = 0.5
    sentiment_score: float = 0.5
    sentiment: str = "Neutral"
    details: dict[str, Any] = Field(default_factory=dict)


class TrendsRecord(BaseEntity, TimestampMixin):
    """Google Trends interest record for a keyword."""

    date: str
    keyword: str
    geo: str = ""
    current_interest: int = 0
    average_interest: float = 0.0
    spike_ratio: float = 0.0
    trend_direction: str = "Stable"
    attention_level: str = "Normal"


class OHLCVRecord(BaseEntity, TimestampMixin):
    """Historical OHLCV price record for a single ticker/date."""

    date: str
    ticker: str
    market: Market = Market.US
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: int = 0
    adjusted_close: float = 0.0


class StoryThread(BaseEntity, TimestampMixin):
    """A developing news story that accumulates related articles over time."""

    title: str
    summary: str = ""
    market: Market = Market.KOREA
    status: StoryStatus = StoryStatus.ACTIVE
    related_tickers: list[str] = Field(default_factory=list)
    article_count: int = 0
    first_seen_at: datetime = Field(default_factory=_utcnow)
    last_updated_at: datetime = Field(default_factory=_utcnow)


class NewsStoryLink(BaseEntity, TimestampMixin):
    """Link between a news item and a story thread."""

    news_id: str
    story_id: str
    relevance_score: float = 1.0


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


# ============================================================
# Ontology models
# ============================================================


class OntologyEntity(BaseEntity, TimestampMixin):
    """A real-world entity: company, person, asset, institution, etc."""

    name: str
    entity_type: EntityType = EntityType.COMPANY
    ticker: str = ""
    market: Market = Market.KOREA
    properties: dict[str, Any] = Field(default_factory=dict)
    aliases: list[str] = Field(default_factory=list)
    status: str = "active"


class OntologyEvent(BaseEntity, TimestampMixin):
    """A discrete event with a time axis (absorbs/extends StoryThread)."""

    title: str
    summary: str = ""
    event_type: EventType = EventType.MACRO
    severity: Severity = Severity.MODERATE
    market: Market = Market.KOREA
    started_at: datetime = Field(default_factory=_utcnow)
    last_article_at: datetime = Field(default_factory=_utcnow)
    status: EventStatus = EventStatus.DEVELOPING
    article_count: int = 0
    story_thread: str = ""  # 같은 스토리라인 묶기 (예: "이란_호르무즈_봉쇄")


class OntologyLink(BaseEntity, TimestampMixin):
    """A typed, directional link between two ontology objects."""

    link_type: LinkType
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    confidence: float = 1.0
    evidence: str = ""
    source_urls: list[str] = Field(default_factory=list)
    geo_issue_id: str = ""


class GeoIssue(BaseEntity, TimestampMixin):
    """A geopolitical/stock issue that groups related events and entities."""

    title: str
    description: str = ""
    severity: Severity = Severity.MODERATE
    status: GeoIssueStatus = GeoIssueStatus.ACTIVE
    category: str = "geo"  # geo, stock_us, stock_kr
    analysis_type: str = ""  # fundamental, technical, market (주식 전용)
    event_ids: list[str] = Field(default_factory=list)
    entity_ids: list[str] = Field(default_factory=list)


class MarketReaction(BaseEntity, TimestampMixin):
    """Market reaction to an event (price/sentiment change)."""

    event_id: str
    entity_id: str
    reaction_type: str = "price"
    magnitude: float = 0.0
    direction: str = "neutral"
    details: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime = Field(default_factory=_utcnow)


class Thesis(BaseEntity, TimestampMixin):
    """An investment thesis built from accumulated events and reactions."""

    title: str
    summary: str = ""
    market: Market = Market.KOREA
    status: ThesisStatus = ThesisStatus.ACTIVE
    related_tickers: list[str] = Field(default_factory=list)
    strength: float = 0.0
    evidence_count: int = 0


class NewsFact(BaseEntity, TimestampMixin):
    """A structured fact extracted from a news article.

    Captures numerical data, events, policy decisions, and other
    verifiable claims along with their source evidence.
    """

    news_id: str
    fact_type: FactType = FactType.NUMERICAL
    claim: str
    entities: list[str] = Field(default_factory=list)
    tickers: list[str] = Field(default_factory=list)
    numbers: dict[str, Any] = Field(default_factory=dict)
    source_quote: str = ""
    market: Market = Market.KOREA
    confidence: float = 1.0
    published_at: datetime | None = None
    extracted_at: datetime = Field(default_factory=_utcnow)


class FirstPrincipleAnalysis(BaseEntity, TimestampMixin):
    """First-principles analysis of an ontology event.

    Follows the pattern: conventional wisdom → decompose →
    identify gap → derive opportunity.
    """

    event_id: str
    event_title: str = ""
    conventional_wisdom: str = ""
    fundamental_truths: list[str] = Field(default_factory=list)
    gap: str = ""
    opportunity: str = ""
    related_fact_ids: list[str] = Field(default_factory=list)
    market: Market = Market.KOREA
    status: str = "draft"
