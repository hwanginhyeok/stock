"""Tests for BaseRepository CRUD operations using in-memory SQLite."""

from __future__ import annotations

import pytest

from src.core.models import (
    Article,
    ArticleType,
    Market,
    MarketSnapshot,
    MarketSentiment,
    NewsItem,
    StockAnalysis,
)
from src.storage.news_repository import NewsRepository
from src.storage.market_snapshot_repository import MarketSnapshotRepository
from src.storage.stock_analysis_repository import StockAnalysisRepository
from src.storage.article_repository import ArticleRepository


@pytest.mark.integration
class TestNewsRepository:
    """Test NewsRepository CRUD with in-memory DB."""

    def test_create_and_get(self, db_session):
        repo = NewsRepository()
        item = NewsItem(title="테스트 뉴스", source="테스트")
        created = repo.create(item)
        assert created.id == item.id

        fetched = repo.get_by_id(item.id)
        assert fetched is not None
        assert fetched.title == "테스트 뉴스"

    def test_create_many(self, db_session):
        repo = NewsRepository()
        items = [
            NewsItem(title=f"뉴스 {i}", market=Market.KOREA)
            for i in range(5)
        ]
        created = repo.create_many(items)
        assert len(created) == 5

    def test_get_many_with_filter(self, db_session):
        repo = NewsRepository()
        repo.create(NewsItem(title="Korea News", market=Market.KOREA))
        repo.create(NewsItem(title="US News", market=Market.US))

        korea_items = repo.get_many(filters={"market": "korea"})
        assert len(korea_items) == 1
        assert korea_items[0].title == "Korea News"

    def test_get_many_with_limit(self, db_session):
        repo = NewsRepository()
        for i in range(10):
            repo.create(NewsItem(title=f"News {i}"))
        items = repo.get_many(limit=3)
        assert len(items) == 3

    def test_update(self, db_session):
        repo = NewsRepository()
        item = NewsItem(title="Original")
        repo.create(item)

        updated = repo.update(item.id, title="Updated")
        assert updated is not None
        assert updated.title == "Updated"

    def test_update_nonexistent(self, db_session):
        repo = NewsRepository()
        result = repo.update("nonexistent-id", title="nope")
        assert result is None

    def test_delete(self, db_session):
        repo = NewsRepository()
        item = NewsItem(title="To Delete")
        repo.create(item)

        assert repo.delete(item.id) is True
        assert repo.get_by_id(item.id) is None

    def test_delete_nonexistent(self, db_session):
        repo = NewsRepository()
        assert repo.delete("nonexistent-id") is False

    def test_count(self, db_session):
        repo = NewsRepository()
        assert repo.count() == 0
        repo.create(NewsItem(title="A"))
        repo.create(NewsItem(title="B"))
        assert repo.count() == 2

    def test_count_with_filter(self, db_session):
        repo = NewsRepository()
        repo.create(NewsItem(title="A", market=Market.KOREA))
        repo.create(NewsItem(title="B", market=Market.US))
        assert repo.count(filters={"market": "korea"}) == 1

    def test_get_latest(self, db_session):
        repo = NewsRepository()
        for i in range(5):
            repo.create(NewsItem(title=f"News {i}"))
        latest = repo.get_latest(limit=3)
        assert len(latest) == 3

    def test_get_by_market(self, db_session):
        repo = NewsRepository()
        repo.create(NewsItem(title="KR", market=Market.KOREA))
        repo.create(NewsItem(title="US", market=Market.US))
        kr = repo.get_by_market(Market.KOREA)
        assert len(kr) == 1
        assert kr[0].title == "KR"

    def test_json_fields_roundtrip(self, db_session):
        repo = NewsRepository()
        item = NewsItem(
            title="Tickers Test",
            related_tickers=["AAPL", "MSFT"],
            related_sectors=["Tech"],
        )
        repo.create(item)
        fetched = repo.get_by_id(item.id)
        assert fetched.related_tickers == ["AAPL", "MSFT"]
        assert fetched.related_sectors == ["Tech"]


@pytest.mark.integration
class TestMarketSnapshotRepository:
    """Test MarketSnapshotRepository."""

    def test_create_and_get(self, db_session):
        repo = MarketSnapshotRepository()
        snap = MarketSnapshot(
            date="2026-02-22",
            market=Market.US,
            index_name="S&P 500",
            index_value=5200.0,
        )
        repo.create(snap)
        fetched = repo.get_by_id(snap.id)
        assert fetched is not None
        assert fetched.index_name == "S&P 500"

    def test_json_extra_data(self, db_session):
        repo = MarketSnapshotRepository()
        snap = MarketSnapshot(
            date="2026-02-22",
            market=Market.US,
            index_name="VIX",
            extra_data={"vix_level": 18.5},
        )
        repo.create(snap)
        fetched = repo.get_by_id(snap.id)
        assert fetched.extra_data["vix_level"] == 18.5


@pytest.mark.integration
class TestStockAnalysisRepository:
    """Test StockAnalysisRepository."""

    def test_create_and_get(self, db_session):
        repo = StockAnalysisRepository()
        analysis = StockAnalysis(
            ticker="AAPL",
            name="Apple",
            composite_score=75.0,
            signals=["MACD bullish"],
        )
        repo.create(analysis)
        fetched = repo.get_by_id(analysis.id)
        assert fetched is not None
        assert fetched.ticker == "AAPL"
        assert fetched.signals == ["MACD bullish"]


@pytest.mark.integration
class TestArticleRepository:
    """Test ArticleRepository."""

    def test_create_and_get(self, db_session):
        repo = ArticleRepository()
        article = Article(
            article_type=ArticleType.MORNING_BRIEFING,
            title="모닝 브리핑",
            content="오늘의 시장 분석 내용",
            char_count=50,
        )
        repo.create(article)
        fetched = repo.get_by_id(article.id)
        assert fetched is not None
        assert fetched.title == "모닝 브리핑"
        assert fetched.article_type == ArticleType.MORNING_BRIEFING
