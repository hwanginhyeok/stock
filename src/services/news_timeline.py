"""News timeline service — query, filter, format, and summarize news feeds."""

from __future__ import annotations

from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from src.core.logger import get_logger
from src.core.models import Importance, Market, NewsItem
from src.storage import NewsRepository

logger = get_logger(__name__)


@dataclass
class TimelineSummary:
    """Aggregated statistics for a news timeline.

    Attributes:
        total: Total news items in the window.
        by_market: Count per market.
        by_importance: Count per importance level.
        avg_sentiment: Average sentiment score.
        top_tickers: Most-mentioned tickers with counts.
        breaking_count: Number of HIGH importance items.
        hours: Time window used for the summary.
    """

    total: int = 0
    by_market: dict[str, int] = field(default_factory=dict)
    by_importance: dict[str, int] = field(default_factory=dict)
    avg_sentiment: float = 0.0
    top_tickers: list[tuple[str, int]] = field(default_factory=list)
    breaking_count: int = 0
    hours: int = 24


class NewsTimelineService:
    """High-level service for news timeline operations.

    Wraps NewsRepository to provide filtered timelines, summaries,
    and terminal-friendly output formatting.

    Example::

        svc = NewsTimelineService()
        items = svc.get_timeline(market="us", hours=4)
        print(svc.format_for_terminal(items))
    """

    def __init__(self) -> None:
        self._repo = NewsRepository()

    def get_timeline(
        self,
        market: str | None = None,
        ticker: str | None = None,
        hours: int = 24,
        importance: str | None = None,
        min_sentiment: float | None = None,
        limit: int = 100,
    ) -> list[NewsItem]:
        """Get a filtered news timeline.

        Args:
            market: Market filter ("kr" or "us", None for both).
            ticker: Filter by a single ticker symbol.
            hours: Look-back window in hours.
            importance: Filter by importance level ("high", "medium", "low").
            min_sentiment: Minimum sentiment score filter.
            limit: Maximum results.

        Returns:
            Filtered list of NewsItem, newest first.
        """
        market_enum = None
        if market:
            market_enum = Market.KOREA if market.lower() == "kr" else Market.US

        # Route to the most specific query
        if ticker:
            items = self._repo.get_by_tickers([ticker], hours=hours, limit=limit)
        elif importance:
            items = self._repo.get_by_importance(importance, hours=hours, limit=limit)
        else:
            items = self._repo.get_timeline(market=market_enum, hours=hours, limit=limit)

        # Apply additional filters in-memory
        if market_enum and ticker:
            items = [i for i in items if i.market == market_enum]
        if min_sentiment is not None:
            items = [i for i in items if i.sentiment_score >= min_sentiment]

        return items

    def get_summary(self, hours: int = 24) -> TimelineSummary:
        """Get aggregated statistics for the timeline.

        Args:
            hours: Look-back window in hours.

        Returns:
            TimelineSummary with counts and averages.
        """
        items = self._repo.get_timeline(hours=hours, limit=500)

        summary = TimelineSummary(hours=hours)
        summary.total = len(items)

        if not items:
            return summary

        # By market
        market_counts: dict[str, int] = {}
        for item in items:
            m = item.market.value
            market_counts[m] = market_counts.get(m, 0) + 1
        summary.by_market = market_counts

        # By importance
        imp_counts: dict[str, int] = {}
        for item in items:
            i = item.importance.value
            imp_counts[i] = imp_counts.get(i, 0) + 1
        summary.by_importance = imp_counts
        summary.breaking_count = imp_counts.get("high", 0)

        # Average sentiment
        scored = [i.sentiment_score for i in items if i.sentiment_score != 0.0]
        if scored:
            summary.avg_sentiment = round(sum(scored) / len(scored), 4)

        # Top tickers
        ticker_counts: dict[str, int] = {}
        for item in items:
            for t in item.related_tickers:
                ticker_counts[t] = ticker_counts.get(t, 0) + 1
        summary.top_tickers = sorted(
            ticker_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        return summary

    def format_for_terminal(self, items: list[NewsItem]) -> str:
        """Format news items as a terminal-friendly table.

        Args:
            items: List of NewsItem to display.

        Returns:
            Formatted string ready for print().
        """
        if not items:
            return "  뉴스 없음"

        lines: list[str] = []
        lines.append("")
        lines.append(f"  {'시간':<20} {'시장':^6} {'중요':^6} {'감성':>6}  {'제목'}")
        lines.append(f"  {'─' * 20} {'─' * 6} {'─' * 6} {'─' * 6}  {'─' * 50}")

        for item in items:
            # 시간: published_at 우선, 없으면 created_at
            ts = item.published_at or item.created_at
            if ts.tzinfo:
                ts = ts.astimezone(ZoneInfo("Asia/Seoul"))
            time_str = ts.strftime("%m/%d %H:%M")

            market_str = "KR" if item.market == Market.KOREA else "US"

            imp_str = "🔴" if item.importance == Importance.HIGH else "⚪"

            sent_str = ""
            if item.sentiment_score != 0.0:
                s = item.sentiment_score
                if s > 0.3:
                    sent_str = f"+{s:.2f}"
                elif s < -0.3:
                    sent_str = f"{s:.2f}"
                else:
                    sent_str = f" {s:.2f}"
            else:
                sent_str = "  ─   "

            # 제목 (60자로 자르기)
            title = item.title[:60]
            if len(item.title) > 60:
                title += "…"

            # 티커 태그
            ticker_tag = ""
            if item.related_tickers:
                ticker_tag = f" [{','.join(item.related_tickers[:3])}]"

            lines.append(
                f"  {time_str:<20} {market_str:^6} {imp_str:^6} {sent_str:>6}  {title}{ticker_tag}"
            )

        lines.append("")
        lines.append(f"  총 {len(items)}건")
        return "\n".join(lines)

    def format_summary(self, summary: TimelineSummary) -> str:
        """Format a timeline summary for terminal display.

        Args:
            summary: TimelineSummary to format.

        Returns:
            Formatted string.
        """
        lines: list[str] = []
        lines.append("")
        lines.append(f"  ═══ 뉴스 요약 (최근 {summary.hours}시간) ═══")
        lines.append(f"  총 {summary.total}건")
        lines.append("")

        # By market
        if summary.by_market:
            parts = [f"{k.upper()}: {v}건" for k, v in summary.by_market.items()]
            lines.append(f"  시장별: {' | '.join(parts)}")

        # Breaking
        if summary.breaking_count:
            lines.append(f"  🔴 브레이킹: {summary.breaking_count}건")

        # Sentiment
        if summary.avg_sentiment != 0.0:
            emoji = "📈" if summary.avg_sentiment > 0 else "📉"
            lines.append(f"  {emoji} 평균 감성: {summary.avg_sentiment:+.4f}")

        # Top tickers
        if summary.top_tickers:
            lines.append("")
            lines.append("  자주 언급된 종목:")
            for ticker, count in summary.top_tickers[:5]:
                lines.append(f"    {ticker}: {count}건")

        lines.append("")
        return "\n".join(lines)
