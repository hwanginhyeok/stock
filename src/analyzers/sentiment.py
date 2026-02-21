"""News sentiment analysis using Claude API (Haiku)."""

from __future__ import annotations

from typing import Any

from src.analyzers.base import BaseAnalyzer
from src.core.claude_client import ClaudeClient
from src.core.models import ClaudeTask, NewsItem

_SYSTEM_PROMPT = (
    "You are a financial news sentiment analyzer. "
    "Analyze the given news headline and content, then return ONLY a single "
    "floating-point number between -1.0 and +1.0 representing the sentiment. "
    "-1.0 = very negative, 0.0 = neutral, +1.0 = very positive. "
    "Consider the impact on stock prices and investor sentiment. "
    "Return ONLY the number, nothing else."
)


class SentimentAnalyzer(BaseAnalyzer):
    """Analyze news sentiment using Claude Haiku.

    Uses ClaudeTask.SUMMARY (Haiku model) for low-cost, low-latency
    sentiment scoring of financial news.
    """

    def __init__(self) -> None:
        super().__init__()
        self._client = ClaudeClient()

    def analyze(self, ticker: str, **kwargs: Any) -> dict[str, Any]:
        """Analyze sentiment for news items related to a ticker.

        Args:
            ticker: Stock ticker (used for logging context).
            **kwargs: Must include ``news_items`` (list of NewsItem).

        Returns:
            Dict with keys: average_sentiment, items (list of title/score pairs).
        """
        news_items: list[NewsItem] = kwargs.get("news_items", [])
        if not news_items:
            return {"average_sentiment": 0.0, "items": []}

        scored = self.analyze_batch(news_items)
        avg = sum(s for _, s in scored) / len(scored) if scored else 0.0

        return {
            "average_sentiment": round(avg, 4),
            "items": [{"title": t, "score": s} for t, s in scored],
        }

    def analyze_single(self, news_item: NewsItem) -> float:
        """Analyze sentiment for a single news item.

        Args:
            news_item: A NewsItem to analyze.

        Returns:
            Sentiment score between -1.0 and +1.0.
        """
        text = news_item.title
        if news_item.summary:
            text += f"\n{news_item.summary[:500]}"

        try:
            response = self._client.generate(
                task=ClaudeTask.SUMMARY,
                user_message=text,
                system_prompt=_SYSTEM_PROMPT,
            )
            score = self._parse_score(response.content)
            self._logger.debug(
                "sentiment_scored",
                title=news_item.title[:60],
                score=score,
            )
            return score
        except Exception as e:
            self._logger.warning(
                "sentiment_analysis_failed",
                title=news_item.title[:60],
                error=str(e),
            )
            return 0.0

    def analyze_batch(
        self,
        news_items: list[NewsItem],
    ) -> list[tuple[str, float]]:
        """Analyze sentiment for a batch of news items.

        Args:
            news_items: List of NewsItem to analyze.

        Returns:
            List of (title, score) tuples.
        """
        results: list[tuple[str, float]] = []
        for item in news_items:
            score = self.analyze_single(item)
            results.append((item.title, score))
        self._logger.info(
            "batch_sentiment_complete",
            count=len(results),
        )
        return results

    @staticmethod
    def _parse_score(raw: str) -> float:
        """Parse a numeric sentiment score from model output.

        Args:
            raw: Raw model response string.

        Returns:
            Clamped float between -1.0 and +1.0.
        """
        cleaned = raw.strip()
        try:
            score = float(cleaned)
            return max(-1.0, min(1.0, score))
        except ValueError:
            # Try to extract a number from the response
            for token in cleaned.split():
                try:
                    score = float(token)
                    return max(-1.0, min(1.0, score))
                except ValueError:
                    continue
            return 0.0
