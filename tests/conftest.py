"""Global test fixtures — autouse mock for config and logger."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core.config import (
    CollectionSettings,
    FundamentalConfig,
    ScreeningConfig,
    StyleConfig,
    TechnicalConfig,
)
from src.core.models import (
    Importance,
    Market,
    MarketSentiment,
    MarketSnapshot,
    NewsItem,
    StockAnalysis,
)


def _build_mock_config() -> MagicMock:
    """Build a MagicMock that mimics AppConfig with sensible defaults."""
    cfg = MagicMock()

    # market sub-configs (real Pydantic models for attribute access)
    cfg.market.technical = TechnicalConfig()
    cfg.market.fundamental = FundamentalConfig()
    cfg.market.screening = ScreeningConfig()
    cfg.market.korea.indices = []
    cfg.market.korea.watchlist = []
    cfg.market.us.indices = []
    cfg.market.us.watchlist = []

    # content
    cfg.content.prohibited_expressions = [
        "꼭 사세요",
        "지금 당장 매수",
        "무조건 수익",
    ]
    cfg.content.disclaimer.ko = (
        "※ 본 콘텐츠는 투자 참고용이며, 투자 판단의 책임은 본인에게 있습니다."
    )
    cfg.content.disclaimer.en = (
        "Disclaimer: This content is for informational purposes only."
    )
    cfg.content.style = StyleConfig()
    cfg.content.article_types = {}

    # claude
    cfg.claude.models = {
        "general": "claude-sonnet-4-6",
        "deep_analysis": "claude-opus-4-6",
        "summary": "claude-haiku-4-5-20251001",
    }
    cfg.claude.default_model = "claude-sonnet-4-6"
    cfg.claude.max_tokens = {"general": 4096, "deep_analysis": 8192, "summary": 1024}
    cfg.claude.temperature = {"general": 0.7, "deep_analysis": 0.5, "summary": 0.3}

    # news
    cfg.news_sources.collection = CollectionSettings()
    cfg.news_sources.korea = []
    cfg.news_sources.us = []

    # sns
    cfg.sns.instagram.hashtag.default_tags = ["#주식", "#투자", "#주식부자"]
    cfg.sns.x.hashtag.default_tags = ["#stock", "#investing"]

    # database
    cfg.database_url = "sqlite:///:memory:"
    cfg.database.url = "sqlite:///:memory:"
    cfg.database.echo = False

    # secrets
    cfg.anthropic_api_key = "test-api-key-not-real"

    return cfg


@pytest.fixture(autouse=True)
def mock_config(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Autouse fixture that replaces get_config() everywhere.

    Prevents YAML / .env loading and provides deterministic defaults.
    """
    from src.core.config import get_config as _original

    _original.cache_clear()

    cfg = _build_mock_config()
    _fn = lambda: cfg  # noqa: E731

    _targets = [
        "src.core.config",
        "src.analyzers.base",
        "src.core.database",
        "src.generators.base",
        "src.workflows.base",
    ]
    for target in _targets:
        try:
            monkeypatch.setattr(f"{target}.get_config", _fn)
        except Exception:
            pass

    # Also patch collector base classes if already imported
    for mod in [
        "src.collectors.news.base",
        "src.collectors.market.base",
    ]:
        try:
            monkeypatch.setattr(f"{mod}.get_config", _fn)
        except Exception:
            pass

    yield cfg

    _original.cache_clear()


# ============================================================
# Sample model factories
# ============================================================


@pytest.fixture
def sample_news_item() -> NewsItem:
    """Factory for a sample NewsItem."""
    return NewsItem(
        title="삼성전자, 반도체 투자 10조 확대",
        content="삼성전자가 반도체 분야에 대규모 투자를 발표했다.",
        summary="삼성전자 반도체 투자 확대",
        source="한국경제",
        url="https://example.com/news/1",
        category="산업",
        importance=Importance.HIGH,
        sentiment_score=0.6,
        related_tickers=["005930"],
        market=Market.KOREA,
    )


@pytest.fixture
def sample_market_snapshot() -> MarketSnapshot:
    """Factory for a sample MarketSnapshot."""
    return MarketSnapshot(
        date="2026-02-22",
        market=Market.US,
        index_name="S&P 500",
        index_value=5234.56,
        change_percent=0.75,
        volume=3_500_000_000,
        sentiment=MarketSentiment.BULLISH,
    )


@pytest.fixture
def sample_stock_analysis() -> StockAnalysis:
    """Factory for a sample StockAnalysis."""
    return StockAnalysis(
        ticker="AAPL",
        name="Apple Inc.",
        market=Market.US,
        date="2026-02-22",
        technical_score=72.5,
        fundamental_score=68.0,
        composite_score=70.3,
        signals=["MACD bullish cross", "RSI oversold (28.5)"],
        recommendation="positive",
    )
