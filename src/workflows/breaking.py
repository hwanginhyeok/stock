"""Breaking news workflow — on-demand, triggered by external events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.collectors.market.us_collector import USMarketCollector
from src.collectors.news.rss_collector import RSSNewsCollector
from src.core.models import (
    Article,
    ArticleType,
    MarketSnapshot,
    NewsItem,
)
from src.generators.article import ArticleContext, ArticleGenerator
from src.generators.insight import InsightContext, InsightGenerator
from src.storage.market_snapshot_repository import MarketSnapshotRepository
from src.workflows.base import BaseWorkflow, WorkflowResult


@dataclass
class BreakingNewsTrigger:
    """Input trigger for breaking news workflow.

    Attributes:
        topic: Description of the breaking event (e.g., "NVDA 실적 발표").
        tickers: Related stock tickers.
        urgency: Urgency level ("normal" or "high").
    """

    topic: str
    tickers: list[str] = field(default_factory=list)
    urgency: str = "normal"


class BreakingNewsWorkflow(BaseWorkflow):
    """Orchestrate breaking news: context + related news + article + insight.

    Steps:
        1. collect_context (critical) — Current market snapshot
        2. collect_related_news (non-critical) — Related news by topic/ticker
        3. generate_article (critical) — Breaking news article
        4. generate_insight (non-critical) — SNS one-liner comment
    """

    name = "breaking_news"

    def __init__(self, trigger: BreakingNewsTrigger) -> None:
        super().__init__()
        self._trigger = trigger
        self._us_collector = USMarketCollector()
        self._news_collector = RSSNewsCollector()
        self._article_gen = ArticleGenerator()
        self._insight_gen = InsightGenerator()
        self._snapshot_repo = MarketSnapshotRepository()

    def execute(self) -> WorkflowResult:
        """Execute breaking news workflow steps.

        Returns:
            WorkflowResult with collected metrics.
        """
        result = WorkflowResult(workflow_name=self.name)
        result.data["topic"] = self._trigger.topic
        result.data["tickers"] = self._trigger.tickers
        result.data["urgency"] = self._trigger.urgency

        # Step 1: Collect current market context (critical)
        snapshots: list[MarketSnapshot] = self._run_step(
            "collect_context",
            self._collect_context,
            critical=True,
        ) or []
        result.snapshots_collected = len(snapshots)

        # Step 2: Collect related news (non-critical)
        news_items: list[NewsItem] = self._run_step(
            "collect_related_news",
            self._collect_related_news,
            critical=False,
        ) or []
        result.news_collected = len(news_items)

        # Step 3: Generate breaking news article (critical)
        article: Article | None = self._run_step(
            "generate_article",
            lambda: self._generate_article(snapshots, news_items),
            critical=True,
        )
        if article:
            result.articles_generated = 1
            result.data["article_id"] = article.id
            result.data["article_title"] = article.title

        # Step 4: Generate SNS insight (non-critical)
        insight: str = self._run_step(
            "generate_insight",
            lambda: self._generate_insight(snapshots),
            critical=False,
        ) or ""
        if insight:
            result.data["insight"] = insight

        return result

    def _collect_context(self) -> list[MarketSnapshot]:
        """Collect current market snapshot as context for the breaking event.

        Returns:
            List of current market snapshots.
        """
        snapshots = self._us_collector.collect_indices()
        # Store snapshots for reference
        if snapshots:
            self._snapshot_repo.create_many(snapshots)
        self._logger.info("breaking_context_collected", count=len(snapshots))
        return snapshots

    def _collect_related_news(self) -> list[NewsItem]:
        """Collect and filter news related to the breaking topic/tickers.

        Collects all recent news and filters by ticker mentions in title
        or related_tickers field.

        Returns:
            List of related news items.
        """
        all_news = self._news_collector.collect_and_store()

        if not self._trigger.tickers:
            return all_news[:10]

        # Filter news related to trigger tickers
        ticker_set = {t.upper() for t in self._trigger.tickers}
        related: list[NewsItem] = []
        for item in all_news:
            item_tickers = {t.upper() for t in item.related_tickers}
            if item_tickers & ticker_set:
                related.append(item)
                continue
            # Check if any ticker appears in the title
            title_upper = item.title.upper()
            if any(t in title_upper for t in ticker_set):
                related.append(item)

        # If filtering yields too few results, include unfiltered top items
        if len(related) < 3:
            related = all_news[:10]

        self._logger.info(
            "related_news_collected",
            total=len(all_news),
            related=len(related),
        )
        return related

    def _generate_article(
        self,
        snapshots: list[MarketSnapshot],
        news_items: list[NewsItem],
    ) -> Article:
        """Generate and store breaking news article.

        Uses STOCK_ANALYSIS article type for topic-focused content.

        Args:
            snapshots: Market snapshot context.
            news_items: Related news items.

        Returns:
            Generated and stored Article.
        """
        context = ArticleContext(
            market_snapshots=snapshots,
            news_items=news_items[:10],
            extra={
                "topic": self._trigger.topic,
                "tickers": self._trigger.tickers,
                "urgency": self._trigger.urgency,
            },
        )
        return self._article_gen.generate_and_store(
            ArticleType.STOCK_ANALYSIS,
            context,
        )

    def _generate_insight(
        self,
        snapshots: list[MarketSnapshot],
    ) -> str:
        """Generate a short SNS insight comment about the breaking event.

        Args:
            snapshots: Market snapshot context.

        Returns:
            Short insight string.
        """
        insight_context = InsightContext(
            market_snapshots=snapshots[:3],
            key_events=[self._trigger.topic],
        )
        return self._insight_gen.generate_market_insight(insight_context)
