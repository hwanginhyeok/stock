"""Morning briefing workflow — runs daily at 08:00 KST."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.collectors.market.korea_collector import KoreaMarketCollector
from src.collectors.market.us_collector import USMarketCollector
from src.collectors.news.rss_collector import RSSNewsCollector
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
from src.workflows.base import BaseWorkflow, WorkflowResult


class MorningBriefingWorkflow(BaseWorkflow):
    """Orchestrate morning briefing: market data + news + analysis + article.

    Steps:
        1. collect_market_data (critical) — US overnight + Korea previous close
        2. collect_news (non-critical) — RSS news collection
        3. analyze_stocks (non-critical) — Watchlist screening
        4. generate_article (critical) — Morning briefing article via Claude
        5. generate_images (non-critical) — Chart images via matplotlib
        6. store_snapshots (non-critical) — Persist market snapshots to DB
    """

    name = "morning_briefing"

    def __init__(self) -> None:
        super().__init__()
        self._us_collector = USMarketCollector()
        self._kr_collector = KoreaMarketCollector()
        self._news_collector = RSSNewsCollector()
        self._screener = StockScreener()
        self._article_gen = ArticleGenerator()
        self._image_gen = ImageGenerator()
        self._snapshot_repo = MarketSnapshotRepository()

    def execute(self) -> WorkflowResult:
        """Execute morning briefing workflow steps.

        Returns:
            WorkflowResult with collected metrics.
        """
        result = WorkflowResult(workflow_name=self.name)

        # Step 1: Collect market data (critical)
        snapshots: list[MarketSnapshot] = self._run_step(
            "collect_market_data",
            self._collect_market_data,
            critical=True,
        ) or []
        result.snapshots_collected = len(snapshots)

        # Step 2: Collect news (non-critical)
        news_items: list[NewsItem] = self._run_step(
            "collect_news",
            self._collect_news,
            critical=False,
        ) or []
        result.news_collected = len(news_items)

        # Step 3: Analyze stocks (non-critical)
        analyses: list[StockAnalysis] = self._run_step(
            "analyze_stocks",
            self._analyze_stocks,
            critical=False,
        ) or []
        result.analyses_produced = len(analyses)

        # Step 4: Generate article (critical)
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

        # Step 6: Store snapshots (non-critical)
        self._run_step(
            "store_snapshots",
            lambda: self._store_snapshots(snapshots),
            critical=False,
        )

        return result

    def _collect_market_data(self) -> list[MarketSnapshot]:
        """Collect US overnight and Korea previous close data.

        Returns:
            Combined list of market snapshots from both markets.
        """
        us_snapshots = self._us_collector.collect_indices()
        kr_snapshots = self._kr_collector.collect_indices()
        all_snapshots = us_snapshots + kr_snapshots
        self._logger.info(
            "market_data_collected",
            us_count=len(us_snapshots),
            kr_count=len(kr_snapshots),
        )
        return all_snapshots

    def _collect_news(self) -> list[NewsItem]:
        """Collect and store RSS news from all configured sources.

        Returns:
            List of collected and stored news items.
        """
        return self._news_collector.collect_and_store()

    def _analyze_stocks(self) -> list[StockAnalysis]:
        """Screen US watchlist stocks.

        Returns:
            List of stock analyses sorted by composite score.
        """
        ohlcv_data = self._us_collector.collect_watchlist_ohlcv(days=120)
        if not ohlcv_data:
            self._logger.info("no_ohlcv_data_for_screening")
            return []
        return self._screener.screen_and_store(ohlcv_data, Market.US)

    def _generate_article(
        self,
        snapshots: list[MarketSnapshot],
        news_items: list[NewsItem],
        analyses: list[StockAnalysis],
    ) -> Article:
        """Generate and store morning briefing article.

        Args:
            snapshots: Market snapshot data.
            news_items: Collected news items.
            analyses: Stock analysis results.

        Returns:
            Generated and stored Article.
        """
        context = ArticleContext(
            market_snapshots=snapshots,
            news_items=news_items[:15],
            stock_analyses=analyses[:10],
        )
        return self._article_gen.generate_and_store(
            ArticleType.MORNING_BRIEFING,
            context,
        )

    def _generate_images(
        self,
        snapshots: list[MarketSnapshot],
        analyses: list[StockAnalysis],
    ) -> list[Path]:
        """Generate chart images for the morning briefing.

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
