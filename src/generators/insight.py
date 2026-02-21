"""Insight generator for short SNS-friendly market comments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.models import ClaudeTask, MarketSnapshot, StockAnalysis
from src.generators.base import BaseGenerator

_SYSTEM_PROMPT = (
    "당신은 주식 시장 전문 SNS 콘텐츠 작성자입니다. "
    "간결하고 임팩트 있는 한 줄 코멘트를 작성합니다. "
    "투자 권유나 종목 추천 표현은 절대 사용하지 마세요. "
    "숫자와 팩트 중심으로 작성하세요."
)


@dataclass
class InsightContext:
    """Input context for market insight generation.

    Attributes:
        market_snapshots: Current market state data.
        top_movers: Notable stock movers.
        key_events: Key market events or headlines.
    """

    market_snapshots: list[MarketSnapshot] = field(default_factory=list)
    top_movers: list[dict[str, Any]] = field(default_factory=list)
    key_events: list[str] = field(default_factory=list)


class InsightGenerator(BaseGenerator):
    """Generate short market insights for SNS posts.

    Uses Claude Haiku (SUMMARY task) for low-cost, low-latency
    generation of one-line market comments and stock comments.
    """

    def generate(self, **kwargs: Any) -> str:
        """Generate a market insight.

        Args:
            **kwargs: Must include ``context`` (InsightContext). Optional:
                ``max_chars`` (int, default 280).

        Returns:
            Short insight text string.
        """
        context: InsightContext = kwargs["context"]
        max_chars: int = kwargs.get("max_chars", 280)
        return self.generate_market_insight(context, max_chars=max_chars)

    def generate_market_insight(
        self,
        context: InsightContext,
        max_chars: int = 280,
    ) -> str:
        """Generate a short market insight comment.

        Args:
            context: Market data and events context.
            max_chars: Maximum character length (default 280 for X/Twitter).

        Returns:
            Short market comment string. Empty string on failure.
        """
        # Build a concise data summary for the prompt
        parts: list[str] = []

        for snap in context.market_snapshots[:3]:
            sign = "+" if snap.change_percent >= 0 else ""
            parts.append(
                f"{snap.index_name}: {snap.index_value:,.2f} ({sign}{snap.change_percent}%)"
            )

        if context.top_movers:
            movers = ", ".join(
                f"{m.get('name', m.get('ticker', '?'))}({m.get('change_percent', 0):+.1f}%)"
                for m in context.top_movers[:5]
            )
            parts.append(f"주요 등락: {movers}")

        if context.key_events:
            events = "; ".join(context.key_events[:3])
            parts.append(f"주요 이벤트: {events}")

        data_summary = "\n".join(parts)

        user_message = (
            f"다음 시장 데이터를 바탕으로 {max_chars}자 이내의 "
            f"임팩트 있는 시장 코멘트 한 줄을 작성하세요. "
            f"해시태그 없이 본문만 작성하세요.\n\n{data_summary}"
        )

        try:
            insight = self._generate_content(
                ClaudeTask.SUMMARY,
                user_message,
                _SYSTEM_PROMPT,
            )
            # Enforce character limit
            if len(insight) > max_chars:
                insight = insight[: max_chars - 3] + "..."
            return insight.strip()
        except Exception as e:
            self._logger.warning(
                "market_insight_failed",
                error=str(e),
            )
            return ""

    def generate_stock_comment(
        self,
        analysis: StockAnalysis,
        max_chars: int = 200,
    ) -> str:
        """Generate a short comment for a single stock.

        Args:
            analysis: StockAnalysis result for the stock.
            max_chars: Maximum character length.

        Returns:
            Short stock comment string. Empty string on failure.
        """
        signals_str = ", ".join(analysis.signals[:5]) if analysis.signals else "없음"
        data_summary = (
            f"종목: {analysis.name} ({analysis.ticker})\n"
            f"종합 점수: {analysis.composite_score:.1f}/100\n"
            f"기술 점수: {analysis.technical_score:.1f} | "
            f"기본 점수: {analysis.fundamental_score:.1f}\n"
            f"시그널: {signals_str}\n"
            f"분석 의견: {analysis.recommendation}"
        )

        user_message = (
            f"다음 종목 분석 데이터를 바탕으로 {max_chars}자 이내의 "
            f"간결한 종목 코멘트 한 줄을 작성하세요. "
            f"투자 권유 없이 객관적 팩트만 언급하세요.\n\n{data_summary}"
        )

        try:
            comment = self._generate_content(
                ClaudeTask.SUMMARY,
                user_message,
                _SYSTEM_PROMPT,
            )
            if len(comment) > max_chars:
                comment = comment[: max_chars - 3] + "..."
            return comment.strip()
        except Exception as e:
            self._logger.warning(
                "stock_comment_failed",
                ticker=analysis.ticker,
                error=str(e),
            )
            return ""
