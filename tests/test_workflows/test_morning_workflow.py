"""Tests for MorningBriefingWorkflow with all dependencies mocked."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.models import (
    Article,
    ArticleType,
    Market,
    MarketSnapshot,
    NewsItem,
    StockAnalysis,
)
from src.workflows.morning import MorningBriefingWorkflow


def _mock_all_deps():
    """Return patches for all MorningBriefingWorkflow dependencies."""
    patches = {
        "us_collector": patch(
            "src.workflows.morning.USMarketCollector",
        ),
        "kr_collector": patch(
            "src.workflows.morning.KoreaMarketCollector",
        ),
        "news_collector": patch(
            "src.workflows.morning.RSSNewsCollector",
        ),
        "screener": patch(
            "src.workflows.morning.StockScreener",
        ),
        "article_gen": patch(
            "src.workflows.morning.ArticleGenerator",
        ),
        "image_gen": patch(
            "src.workflows.morning.ImageGenerator",
        ),
        "snapshot_repo": patch(
            "src.workflows.morning.MarketSnapshotRepository",
        ),
    }
    return patches


class TestMorningBriefingWorkflow:
    """Test full morning briefing pipeline with mocked dependencies."""

    def test_successful_execution(self):
        patches = _mock_all_deps()
        mocks = {}
        for name, p in patches.items():
            mocks[name] = p.start()

        # Configure mock returns
        us_instance = mocks["us_collector"].return_value
        us_instance.collect_indices.return_value = [
            MarketSnapshot(index_name="S&P 500", index_value=5200.0),
        ]
        us_instance.collect_watchlist_ohlcv.return_value = {}

        kr_instance = mocks["kr_collector"].return_value
        kr_instance.collect_indices.return_value = [
            MarketSnapshot(index_name="KOSPI", index_value=2600.0),
        ]

        news_instance = mocks["news_collector"].return_value
        news_instance.collect_and_store.return_value = [
            NewsItem(title="Test News"),
        ]

        screener_instance = mocks["screener"].return_value
        screener_instance.screen_and_store.return_value = []

        article_instance = mocks["article_gen"].return_value
        mock_article = Article(
            article_type=ArticleType.MORNING_BRIEFING,
            title="테스트 브리핑",
            content="내용",
        )
        article_instance.generate_and_store.return_value = mock_article

        image_instance = mocks["image_gen"].return_value
        image_instance.generate_market_summary_card.return_value = Path("/tmp/chart.png")
        image_instance.generate_performance_comparison.return_value = Path("/tmp/perf.png")

        snapshot_repo_instance = mocks["snapshot_repo"].return_value
        snapshot_repo_instance.create_many.return_value = []

        try:
            wf = MorningBriefingWorkflow()
            result = wf.run()
            assert result.success is True
            assert result.snapshots_collected == 2
            assert result.news_collected == 1
            assert result.articles_generated == 1
        finally:
            for p in patches.values():
                p.stop()

    def test_critical_step_failure_aborts(self):
        patches = _mock_all_deps()
        mocks = {}
        for name, p in patches.items():
            mocks[name] = p.start()

        # Market data collection fails (critical step)
        us_instance = mocks["us_collector"].return_value
        us_instance.collect_indices.side_effect = Exception("API down")
        kr_instance = mocks["kr_collector"].return_value
        kr_instance.collect_indices.side_effect = Exception("API down")

        try:
            wf = MorningBriefingWorkflow()
            result = wf.run()
            assert result.success is False
        finally:
            for p in patches.values():
                p.stop()

    def test_non_critical_failure_continues(self):
        patches = _mock_all_deps()
        mocks = {}
        for name, p in patches.items():
            mocks[name] = p.start()

        us_instance = mocks["us_collector"].return_value
        us_instance.collect_indices.return_value = [
            MarketSnapshot(index_name="S&P 500", index_value=5200.0),
        ]
        us_instance.collect_watchlist_ohlcv.return_value = {}

        kr_instance = mocks["kr_collector"].return_value
        kr_instance.collect_indices.return_value = []

        # News collection fails (non-critical)
        news_instance = mocks["news_collector"].return_value
        news_instance.collect_and_store.side_effect = Exception("RSS down")

        screener_instance = mocks["screener"].return_value
        screener_instance.screen_and_store.return_value = []

        article_instance = mocks["article_gen"].return_value
        article_instance.generate_and_store.return_value = Article(
            article_type=ArticleType.MORNING_BRIEFING,
            title="Briefing",
            content="Content",
        )

        image_instance = mocks["image_gen"].return_value
        image_instance.generate_market_summary_card.return_value = Path("/tmp/c.png")

        snapshot_repo_instance = mocks["snapshot_repo"].return_value
        snapshot_repo_instance.create_many.return_value = []

        try:
            wf = MorningBriefingWorkflow()
            result = wf.run()
            assert result.success is True
            assert result.news_collected == 0
            assert result.articles_generated == 1
        finally:
            for p in patches.values():
                p.stop()
