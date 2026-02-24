"""Tests for Pydantic domain models and enums."""

from __future__ import annotations

import json

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


class TestEnums:
    """Test all StrEnum definitions."""

    def test_market_values(self):
        assert Market.KOREA == "korea"
        assert Market.US == "us"

    def test_importance_values(self):
        assert Importance.HIGH == "high"
        assert Importance.MEDIUM == "medium"
        assert Importance.LOW == "low"

    def test_market_sentiment_values(self):
        assert MarketSentiment.VERY_BULLISH == "very_bullish"
        assert MarketSentiment.NEUTRAL == "neutral"
        assert MarketSentiment.VERY_BEARISH == "very_bearish"

    def test_article_type_values(self):
        assert ArticleType.MORNING_BRIEFING == "morning_briefing"
        assert ArticleType.CLOSING_REVIEW == "closing_review"
        assert ArticleType.STOCK_ANALYSIS == "stock_analysis"
        assert ArticleType.WEEKLY_REVIEW == "weekly_review"

    def test_sns_platform_values(self):
        assert SNSPlatform.INSTAGRAM == "instagram"
        assert SNSPlatform.X == "x"

    def test_post_type_values(self):
        assert PostType.IMAGE == "image"
        assert PostType.TWEET == "tweet"

    def test_post_status_values(self):
        assert PostStatus.DRAFT == "draft"
        assert PostStatus.PUBLISHED == "published"
        assert PostStatus.FAILED == "failed"

    def test_research_type_values(self):
        assert ResearchType.STOCK == "stock"
        assert ResearchType.SECTOR == "sector"
        assert ResearchType.CROSS_MARKET == "cross_market"

    def test_claude_task_values(self):
        assert ClaudeTask.GENERAL == "general"
        assert ClaudeTask.DEEP_ANALYSIS == "deep_analysis"
        assert ClaudeTask.SUMMARY == "summary"


class TestBaseEntity:
    """Test BaseEntity auto-ID and ORM compatibility."""

    def test_auto_uuid(self):
        e1 = BaseEntity()
        e2 = BaseEntity()
        assert e1.id != e2.id
        assert len(e1.id) == 36  # UUID format

    def test_from_attributes(self):
        assert BaseEntity.model_config["from_attributes"] is True

    def test_to_log_dict(self):
        e = BaseEntity()
        d = e.to_log_dict()
        assert "id" in d


class TestTimestampMixin:
    """Test that created_at defaults to UTC now."""

    def test_default_created_at(self):
        m = TimestampMixin()
        assert m.created_at is not None
        assert m.created_at.tzinfo is not None


class TestNewsItem:
    """Test NewsItem model defaults and serialization."""

    def test_defaults(self):
        item = NewsItem(title="Test")
        assert item.importance == Importance.MEDIUM
        assert item.sentiment_score == 0.0
        assert item.related_tickers == []
        assert item.market == Market.KOREA

    def test_full_construction(self, sample_news_item):
        assert sample_news_item.title == "삼성전자, 반도체 투자 10조 확대"
        assert sample_news_item.importance == Importance.HIGH
        assert "005930" in sample_news_item.related_tickers

    def test_serialization_roundtrip(self, sample_news_item):
        data = sample_news_item.model_dump()
        restored = NewsItem.model_validate(data)
        assert restored.title == sample_news_item.title
        assert restored.market == sample_news_item.market

    def test_json_roundtrip(self, sample_news_item):
        json_str = sample_news_item.model_dump_json()
        restored = NewsItem.model_validate_json(json_str)
        assert restored.id == sample_news_item.id


class TestMarketSnapshot:
    """Test MarketSnapshot defaults and serialization."""

    def test_defaults(self):
        snap = MarketSnapshot()
        assert snap.index_value == 0.0
        assert snap.sentiment == MarketSentiment.NEUTRAL
        assert snap.top_gainers == []

    def test_full_construction(self, sample_market_snapshot):
        assert sample_market_snapshot.index_name == "S&P 500"
        assert sample_market_snapshot.change_percent == 0.75

    def test_serialization(self, sample_market_snapshot):
        data = sample_market_snapshot.model_dump()
        assert data["market"] == "us"
        assert data["sentiment"] == "bullish"


class TestStockAnalysis:
    """Test StockAnalysis model."""

    def test_defaults(self):
        sa = StockAnalysis(ticker="TSLA")
        assert sa.composite_score == 0.0
        assert sa.signals == []
        assert sa.recommendation == ""

    def test_full_construction(self, sample_stock_analysis):
        assert sample_stock_analysis.composite_score == 70.3
        assert len(sample_stock_analysis.signals) == 2


class TestArticle:
    """Test Article model."""

    def test_construction(self):
        a = Article(
            article_type=ArticleType.MORNING_BRIEFING,
            title="모닝 브리핑",
            content="오늘의 시장 분석",
        )
        assert a.char_count == 0
        assert a.disclaimer_included is False
        assert a.quality_score == 0.0


class TestSNSPost:
    """Test SNSPost model."""

    def test_defaults(self):
        p = SNSPost(
            platform=SNSPlatform.INSTAGRAM,
            post_type=PostType.IMAGE,
            content="Test",
        )
        assert p.status == PostStatus.DRAFT
        assert p.retry_count == 0
        assert p.hashtags == []


class TestResearchReport:
    """Test ResearchReport model."""

    def test_construction(self):
        r = ResearchReport(
            research_type=ResearchType.STOCK,
            subject="AAPL",
            title="Apple Analysis",
        )
        assert r.sections == []
        assert r.swot == {}

    def test_with_sections(self):
        r = ResearchReport(
            research_type=ResearchType.SECTOR,
            subject="반도체",
            title="반도체 섹터 분석",
            sections=[
                ReportSection(title="개요", content="...", order=0),
                ReportSection(title="전망", content="...", order=1),
            ],
        )
        assert len(r.sections) == 2
        assert r.sections[0].title == "개요"
