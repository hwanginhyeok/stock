"""Weekly review workflow — runs Saturday at 10:00 KST."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from src.collectors.market.korea_collector import KoreaMarketCollector
from src.collectors.market.us_collector import USMarketCollector
from src.core.models import (
    Article,
    ArticleType,
    Market,
    MarketSnapshot,
    NewsItem,
    StockAnalysis,
)
from src.generators.article import ArticleContext, ArticleGenerator
from src.generators.image import ImageGenerator
from src.analyzers.screener import StockScreener
from src.storage.market_snapshot_repository import MarketSnapshotRepository
from src.storage.news_repository import NewsRepository
from src.storage.stock_analysis_repository import StockAnalysisRepository
from src.workflows.base import BaseWorkflow, WorkflowResult


class WeeklyReviewWorkflow(BaseWorkflow):
    """Orchestrate weekly review: week's data aggregation + deep analysis article.

    Steps:
        1. collect_weekly_data (critical) — All indices + watchlist 5-day data
        2. aggregate_news (non-critical) — Fetch this week's news from DB
        3. aggregate_analyses (non-critical) — Fetch or re-run week's analyses
        4. generate_article (critical) — Weekly review article (deep_analysis model)
        5. generate_images (non-critical) — Weekly performance comparison charts
    """

    name = "weekly_review"

    def __init__(self) -> None:
        super().__init__()
        self._us_collector = USMarketCollector()
        self._kr_collector = KoreaMarketCollector()
        self._screener = StockScreener()
        self._article_gen = ArticleGenerator()
        self._image_gen = ImageGenerator()
        self._snapshot_repo = MarketSnapshotRepository()
        self._news_repo = NewsRepository()
        self._analysis_repo = StockAnalysisRepository()

    def execute(self) -> WorkflowResult:
        """Execute weekly review workflow steps.

        Returns:
            WorkflowResult with collected metrics.
        """
        result = WorkflowResult(workflow_name=self.name)

        # Step 1: Collect weekly market data (critical)
        snapshots: list[MarketSnapshot] = self._run_step(
            "collect_weekly_data",
            self._collect_weekly_data,
            critical=True,
        ) or []
        result.snapshots_collected = len(snapshots)

        # Step 2: Aggregate this week's news from DB (non-critical)
        news_items: list[NewsItem] = self._run_step(
            "aggregate_news",
            self._aggregate_news,
            critical=False,
        ) or []
        result.news_collected = len(news_items)

        # Step 3: Aggregate or re-run analyses (non-critical)
        analyses: list[StockAnalysis] = self._run_step(
            "aggregate_analyses",
            self._aggregate_analyses,
            critical=False,
        ) or []
        result.analyses_produced = len(analyses)

        # Step 4: Generate weekly review article (critical)
        article: Article | None = self._run_step(
            "generate_article",
            lambda: self._generate_article(snapshots, news_items, analyses),
            critical=True,
        )
        if article:
            result.articles_generated = 1
            result.data["article_id"] = article.id
            result.data["article_title"] = article.title

        # Step 5: Generate images (non-critical)
        image_paths: list[Path] = self._run_step(
            "generate_images",
            lambda: self._generate_images(snapshots, analyses),
            critical=False,
        ) or []
        result.images_generated = len(image_paths)
        result.data["image_paths"] = [str(p) for p in image_paths]

        # Store snapshots
        self._run_step(
            "store_snapshots",
            lambda: self._store_snapshots(snapshots),
            critical=False,
        )

        return result

    def _collect_weekly_data(self) -> list[MarketSnapshot]:
        """Collect all indices data for the past week.

        Returns:
            Combined list of US + Korea market snapshots.
        """
        us_snapshots = self._us_collector.collect_indices()
        kr_snapshots = self._kr_collector.collect_indices()
        all_snapshots = us_snapshots + kr_snapshots
        self._logger.info(
            "weekly_market_data_collected",
            us_count=len(us_snapshots),
            kr_count=len(kr_snapshots),
        )
        return all_snapshots

    def _aggregate_news(self) -> list[NewsItem]:
        """Fetch this week's news items from the database.

        Returns:
            List of news items from the past 7 days.
        """
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        items = self._news_repo.get_by_date_range(week_ago, now)
        self._logger.info("weekly_news_aggregated", count=len(items))
        return items

    def _aggregate_analyses(self) -> list[StockAnalysis]:
        """Fetch this week's analyses from DB, or re-run screening.

        First tries to load recent analyses from DB. If insufficient,
        re-runs screening for both markets.

        Returns:
            List of stock analyses for the week.
        """
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        existing = self._analysis_repo.get_by_date_range(week_ago, now)
        if len(existing) >= 5:
            self._logger.info(
                "weekly_analyses_from_db",
                count=len(existing),
            )
            return existing

        # Re-run screening for both markets
        analyses: list[StockAnalysis] = []

        us_ohlcv = self._us_collector.collect_watchlist_ohlcv(days=120)
        if us_ohlcv:
            us_analyses = self._screener.screen_and_store(us_ohlcv, Market.US)
            analyses.extend(us_analyses)

        kr_ohlcv = self._kr_collector.collect_watchlist_ohlcv(days=120)
        if kr_ohlcv:
            kr_analyses = self._screener.screen_and_store(kr_ohlcv, Market.KOREA)
            analyses.extend(kr_analyses)

        self._logger.info("weekly_analyses_regenerated", count=len(analyses))
        return analyses

    def _generate_article(
        self,
        snapshots: list[MarketSnapshot],
        news_items: list[NewsItem],
        analyses: list[StockAnalysis],
    ) -> Article:
        """Generate and store weekly review article using deep_analysis model.

        Args:
            snapshots: Market snapshot data.
            news_items: This week's news items.
            analyses: Stock analysis results.

        Returns:
            Generated and stored Article.
        """
        context = ArticleContext(
            market_snapshots=snapshots,
            news_items=news_items[:20],
            stock_analyses=analyses[:15],
            extra={"period": "weekly"},
        )
        return self._article_gen.generate_and_store(
            ArticleType.WEEKLY_REVIEW,
            context,
        )

    def _generate_images(
        self,
        snapshots: list[MarketSnapshot],
        analyses: list[StockAnalysis],
    ) -> list[Path]:
        """Generate weekly performance comparison charts.

        Args:
            snapshots: Market snapshots for summary card.
            analyses: Stock analyses for comparison chart.

        Returns:
            List of generated image paths.
        """
        paths: list[Path] = []

        if snapshots:
            path = self._image_gen.generate_market_summary_card(snapshots)
            paths.append(path)

        if analyses:
            path = self._image_gen.generate_performance_comparison(analyses)
            paths.append(path)

        return paths

    def _store_snapshots(self, snapshots: list[MarketSnapshot]) -> list[MarketSnapshot]:
        """Persist market snapshots to the database.

        Args:
            snapshots: Snapshots to store.

        Returns:
            List of stored snapshots.
        """
        if not snapshots:
            return []
        stored = self._snapshot_repo.create_many(snapshots)
        self._logger.info("snapshots_stored", count=len(stored))
        return stored
