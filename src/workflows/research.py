"""Research workflow — on-demand deep analysis for stocks/sectors/themes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.analyzers.fundamental import FundamentalAnalyzer
from src.analyzers.screener import StockScreener
from src.analyzers.sentiment import SentimentAnalyzer
from src.analyzers.technical import TechnicalAnalyzer
from src.collectors.market.us_collector import USMarketCollector
from src.collectors.market.korea_collector import KoreaMarketCollector
from src.collectors.news.rss_collector import RSSNewsCollector
from src.core.models import (
    ClaudeTask,
    Market,
    MarketSnapshot,
    NewsItem,
    ResearchReport,
    ResearchType,
    StockAnalysis,
)
from src.generators.article import ArticleContext, ArticleGenerator
from src.storage.research_report_repository import ResearchReportRepository
from src.workflows.base import BaseWorkflow, WorkflowResult


@dataclass
class ResearchRequest:
    """Input request for on-demand research.

    Attributes:
        research_type: Type of research (STOCK, SECTOR, THEME, CROSS_MARKET).
        subject: Research subject (e.g., "NVDA" or "반도체 섹터").
        tickers: Related stock tickers.
        depth: Analysis depth ("standard" or "deep").
    """

    research_type: ResearchType
    subject: str
    tickers: list[str] = field(default_factory=list)
    depth: str = "standard"


class ResearchWorkflow(BaseWorkflow):
    """Orchestrate on-demand research: data + analysis + news + report.

    Steps:
        1. collect_data (critical) — OHLCV + fundamental data collection
        2. run_analysis (critical) — Technical + fundamental + sentiment analysis
        3. collect_news (non-critical) — Related news collection
        4. generate_report (critical) — Research report via Claude (deep_analysis)
        5. store_report (critical) — Persist report to ResearchReportRepository
    """

    name = "research"

    def __init__(self, request: ResearchRequest) -> None:
        super().__init__()
        self._request = request
        self._us_collector = USMarketCollector()
        self._kr_collector = KoreaMarketCollector()
        self._news_collector = RSSNewsCollector()
        self._technical = TechnicalAnalyzer()
        self._fundamental = FundamentalAnalyzer()
        self._sentiment = SentimentAnalyzer()
        self._screener = StockScreener()
        self._article_gen = ArticleGenerator()
        self._report_repo = ResearchReportRepository()

    def execute(self) -> WorkflowResult:
        """Execute research workflow steps.

        Returns:
            WorkflowResult with collected metrics.
        """
        result = WorkflowResult(workflow_name=self.name)
        result.data["research_type"] = self._request.research_type.value
        result.data["subject"] = self._request.subject
        result.data["depth"] = self._request.depth

        # Step 1: Collect data (critical)
        collected: dict[str, Any] = self._run_step(
            "collect_data",
            self._collect_data,
            critical=True,
        ) or {}
        result.snapshots_collected = len(collected.get("snapshots", []))

        # Step 2: Run analysis (critical)
        analyses: list[StockAnalysis] = self._run_step(
            "run_analysis",
            lambda: self._run_analysis(collected),
            critical=True,
        ) or []
        result.analyses_produced = len(analyses)

        # Step 3: Collect related news (non-critical)
        news_items: list[NewsItem] = self._run_step(
            "collect_news",
            self._collect_news,
            critical=False,
        ) or []
        result.news_collected = len(news_items)

        # Step 4: Generate research report (critical)
        report: ResearchReport | None = self._run_step(
            "generate_report",
            lambda: self._generate_report(
                collected, analyses, news_items,
            ),
            critical=True,
        )

        # Step 5: Store report (critical)
        if report:
            stored_report: ResearchReport | None = self._run_step(
                "store_report",
                lambda: self._store_report(report),
                critical=True,
            )
            if stored_report:
                result.articles_generated = 1
                result.data["report_id"] = stored_report.id
                result.data["report_title"] = stored_report.title

        return result

    def _collect_data(self) -> dict[str, Any]:
        """Collect OHLCV and market data for the research subject.

        Returns:
            Dict with 'ohlcv_data', 'snapshots', and 'market' keys.
        """
        tickers = self._request.tickers or [self._request.subject]
        market = self._detect_market(tickers[0])

        # Collect market snapshots
        if market == Market.US:
            collector = self._us_collector
        else:
            collector = self._kr_collector

        snapshots = collector.collect_indices()

        # Collect OHLCV for each ticker
        days = 180 if self._request.depth == "deep" else 120
        ohlcv_data: dict[str, Any] = {}
        for ticker in tickers:
            df = collector.collect_stock_ohlcv(ticker, days=days)
            if not df.empty:
                ohlcv_data[ticker] = df

        self._logger.info(
            "research_data_collected",
            tickers=tickers,
            ohlcv_count=len(ohlcv_data),
            snapshots_count=len(snapshots),
        )
        return {
            "ohlcv_data": ohlcv_data,
            "snapshots": snapshots,
            "market": market,
        }

    def _run_analysis(self, collected: dict[str, Any]) -> list[StockAnalysis]:
        """Run technical + fundamental analysis on collected data.

        Args:
            collected: Data dict from _collect_data.

        Returns:
            List of StockAnalysis results.
        """
        ohlcv_data = collected.get("ohlcv_data", {})
        market = collected.get("market", Market.US)

        if not ohlcv_data:
            self._logger.warning("no_ohlcv_data_for_analysis")
            return []

        analyses = self._screener.screen_and_store(ohlcv_data, market)
        self._logger.info("research_analysis_complete", count=len(analyses))
        return analyses

    def _collect_news(self) -> list[NewsItem]:
        """Collect news related to the research subject.

        Returns:
            List of news items, filtered by tickers if available.
        """
        all_news = self._news_collector.collect_and_store()

        tickers = self._request.tickers
        if not tickers:
            return all_news[:15]

        # Filter by tickers
        ticker_set = {t.upper() for t in tickers}
        related: list[NewsItem] = []
        for item in all_news:
            item_tickers = {t.upper() for t in item.related_tickers}
            if item_tickers & ticker_set:
                related.append(item)
                continue
            title_upper = item.title.upper()
            if any(t in title_upper for t in ticker_set):
                related.append(item)

        if len(related) < 3:
            related = all_news[:15]

        self._logger.info("research_news_collected", count=len(related))
        return related

    def _generate_report(
        self,
        collected: dict[str, Any],
        analyses: list[StockAnalysis],
        news_items: list[NewsItem],
    ) -> ResearchReport:
        """Generate a research report using Claude deep_analysis model.

        Args:
            collected: Collected data including snapshots.
            analyses: Stock analysis results.
            news_items: Related news items.

        Returns:
            ResearchReport model (not yet stored).
        """
        snapshots = collected.get("snapshots", [])

        # Generate article content using ArticleGenerator
        context = ArticleContext(
            market_snapshots=snapshots,
            news_items=news_items[:15],
            stock_analyses=analyses[:10],
            extra={
                "research_type": self._request.research_type.value,
                "subject": self._request.subject,
                "depth": self._request.depth,
            },
        )
        article = self._article_gen.generate_article(
            ArticleType.STOCK_ANALYSIS,
            context,
        )

        # Convert article content to ResearchReport
        report = ResearchReport(
            research_type=self._request.research_type,
            subject=self._request.subject,
            title=article.title,
            executive_summary=article.summary,
            sections=[],
            related_tickers=self._request.tickers or [self._request.subject],
            risk_factors=[],
            data_sources=["yfinance", "pykrx", "rss_news"],
            model_used=article.model_used,
        )

        self._logger.info(
            "research_report_generated",
            subject=self._request.subject,
            title=report.title[:60],
        )
        return report

    def _store_report(self, report: ResearchReport) -> ResearchReport:
        """Persist the research report to the database.

        Args:
            report: ResearchReport to store.

        Returns:
            Stored ResearchReport.
        """
        stored = self._report_repo.create(report)
        self._logger.info(
            "research_report_stored",
            report_id=stored.id,
            subject=stored.subject,
        )
        return stored

    @staticmethod
    def _detect_market(ticker: str) -> Market:
        """Detect market from ticker format.

        Korean tickers are typically all-numeric (e.g., "005930").
        US tickers contain alphabetic characters (e.g., "AAPL").

        Args:
            ticker: Stock ticker string.

        Returns:
            Market enum.
        """
        if ticker.isdigit():
            return Market.KOREA
        return Market.US
