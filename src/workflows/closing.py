"""Closing review workflow — runs daily at 16:30 KST."""

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


class ClosingReviewWorkflow(BaseWorkflow):
    """Orchestrate closing review: KR close + US premarket + news + article.

    Steps:
        1. collect_kr_closing (critical) — Korea market closing data
        2. collect_us_premarket (non-critical) — US premarket data if available
        3. collect_news (non-critical) — Today's news collection
        4. screen_stocks (non-critical) — Korea watchlist screening
        5. generate_article (critical) — Closing review article via Claude
        6. generate_images (non-critical) — Chart images
    """

    name = "closing_review"

    def __init__(self) -> None:
        super().__init__()
        self._kr_collector = KoreaMarketCollector()
        self._us_collector = USMarketCollector()
        self._news_collector = RSSNewsCollector()
        self._screener = StockScreener()
        self._article_gen = ArticleGenerator()
        self._image_gen = ImageGenerator()
        self._snapshot_repo = MarketSnapshotRepository()

    def execute(self) -> WorkflowResult:
        """Execute closing review workflow steps.

        Returns:
            WorkflowResult with collected metrics.
        """
        result = WorkflowResult(workflow_name=self.name)

        # Step 1: Collect Korea closing data (critical)
        kr_snapshots: list[MarketSnapshot] = self._run_step(
            "collect_kr_closing",
            self._collect_kr_closing,
            critical=True,
        ) or []
        result.snapshots_collected += len(kr_snapshots)

        # Step 2: Collect US premarket data (non-critical)
        us_snapshots: list[MarketSnapshot] = self._run_step(
            "collect_us_premarket",
            self._collect_us_premarket,
            critical=False,
        ) or []
        result.snapshots_collected += len(us_snapshots)

        all_snapshots = kr_snapshots + us_snapshots

        # Step 3: Collect news (non-critical)
        news_items: list[NewsItem] = self._run_step(
            "collect_news",
            self._collect_news,
            critical=False,
        ) or []
        result.news_collected = len(news_items)

        # Step 4: Screen Korea stocks (non-critical)
        analyses: list[StockAnalysis] = self._run_step(
            "screen_stocks",
            self._screen_stocks,
            critical=False,
        ) or []
        result.analyses_produced = len(analyses)

        # Step 5: Generate article (critical)
        article: Article | None = self._run_step(
            "generate_article",
            lambda: self._generate_article(all_snapshots, news_items, analyses),
            critical=True,
        )
        if article:
            result.articles_generated = 1
            result.data["article_id"] = article.id
            result.data["article_title"] = article.title

        # Step 6: Generate images (non-critical)
        image_paths: list[Path] = self._run_step(
            "generate_images",
            lambda: self._generate_images(all_snapshots, analyses),
            critical=False,
        ) or []
        result.images_generated = len(image_paths)
        result.data["image_paths"] = [str(p) for p in image_paths]

        # Store snapshots
        self._run_step(
            "store_snapshots",
            lambda: self._store_snapshots(all_snapshots),
            critical=False,
        )

        return result

    def _collect_kr_closing(self) -> list[MarketSnapshot]:
        """Collect Korea market closing data.

        Returns:
            List of Korean market index snapshots.
        """
        snapshots = self._kr_collector.collect_indices()
        self._logger.info("kr_closing_collected", count=len(snapshots))
        return snapshots

    def _collect_us_premarket(self) -> list[MarketSnapshot]:
        """Collect US market data (latest available, may include premarket).

        Returns:
            List of US market index snapshots.
        """
        snapshots = self._us_collector.collect_indices()
        self._logger.info("us_premarket_collected", count=len(snapshots))
        return snapshots

    def _collect_news(self) -> list[NewsItem]:
        """Collect and store today's RSS news.

        Returns:
            List of collected and stored news items.
        """
        return self._news_collector.collect_and_store()

    def _screen_stocks(self) -> list[StockAnalysis]:
        """Screen Korea watchlist stocks.

        Returns:
            List of stock analyses sorted by composite score.
        """
        ohlcv_data = self._kr_collector.collect_watchlist_ohlcv(days=120)
        if not ohlcv_data:
            self._logger.info("no_kr_ohlcv_for_screening")
            return []
        return self._screener.screen_and_store(ohlcv_data, Market.KOREA)

    def _generate_article(
        self,
        snapshots: list[MarketSnapshot],
        news_items: list[NewsItem],
        analyses: list[StockAnalysis],
    ) -> Article:
        """Generate and store closing review article.

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
            ArticleType.CLOSING_REVIEW,
            context,
        )

    def _generate_images(
        self,
        snapshots: list[MarketSnapshot],
        analyses: list[StockAnalysis],
    ) -> list[Path]:
        """Generate chart images for the closing review.

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
