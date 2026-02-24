"""StockTwits sentiment collector for US stocks."""

from __future__ import annotations

from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors.sentiment.base import BaseSentimentCollector

# StockTwits public API (no auth required for basic access)
_STOCKTWITS_API = "https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; StockRichBot/1.0)",
}


class StockTwitsCollector(BaseSentimentCollector):
    """Collect per-ticker sentiment from StockTwits.

    Uses the public StockTwits API to fetch recent messages
    for a ticker, along with user-tagged bullish/bearish sentiment.
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch_ticker(self, symbol: str) -> dict[str, Any]:
        """Fetch StockTwits stream for a single ticker.

        Args:
            symbol: US stock ticker (e.g., "AAPL").

        Returns:
            Raw JSON response dict.

        Raises:
            requests.RequestException: On network errors.
        """
        url = _STOCKTWITS_API.format(symbol=symbol)
        resp = requests.get(url, timeout=15, headers=_HEADERS)
        resp.raise_for_status()
        return resp.json()

    def collect_stock(self, symbol: str) -> dict[str, Any]:
        """Collect sentiment data for a single US stock.

        Analyzes the most recent messages and counts
        bullish/bearish/neutral sentiment tags.

        Args:
            symbol: US stock ticker (e.g., "AAPL").

        Returns:
            Dict with ticker, message count, sentiment breakdown, and score.
        """
        try:
            data = self._fetch_ticker(symbol)
        except Exception as e:
            self._logger.warning(
                "stocktwits_fetch_failed",
                symbol=symbol,
                error=str(e),
            )
            return {
                "symbol": symbol,
                "messages_count": 0,
                "bullish": 0,
                "bearish": 0,
                "neutral": 0,
                "sentiment_score": 0.5,
                "sentiment": "Unknown",
                "error": str(e),
            }

        messages = data.get("messages", [])
        bullish = 0
        bearish = 0
        neutral = 0

        for msg in messages:
            entities = msg.get("entities", {})
            sentiment_data = entities.get("sentiment", {})
            basic = sentiment_data.get("basic") if sentiment_data else None

            if basic == "Bullish":
                bullish += 1
            elif basic == "Bearish":
                bearish += 1
            else:
                neutral += 1

        total_tagged = bullish + bearish
        if total_tagged > 0:
            sentiment_score = bullish / total_tagged
        else:
            sentiment_score = 0.5

        # Classify
        if sentiment_score >= 0.7:
            sentiment_label = "Very Bullish"
        elif sentiment_score >= 0.55:
            sentiment_label = "Bullish"
        elif sentiment_score >= 0.45:
            sentiment_label = "Neutral"
        elif sentiment_score >= 0.3:
            sentiment_label = "Bearish"
        else:
            sentiment_label = "Very Bearish"

        self._logger.info(
            "stocktwits_collected",
            symbol=symbol,
            messages=len(messages),
            bullish=bullish,
            bearish=bearish,
            score=round(sentiment_score, 3),
        )

        return {
            "symbol": symbol,
            "messages_count": len(messages),
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral,
            "sentiment_score": round(sentiment_score, 3),
            "sentiment": sentiment_label,
        }

    def collect(self) -> list[dict[str, Any]]:
        """Collect StockTwits sentiment for configured US watchlist stocks.

        Returns:
            List of per-ticker sentiment dicts.
        """
        us_watchlist = self._config.market.us.watchlist
        results: list[dict[str, Any]] = []

        for item in us_watchlist:
            # Strip any prefix (^GSPC -> skip indices, only stocks)
            if item.ticker.startswith("^"):
                continue

            data = self.collect_stock(item.ticker)
            results.append(data)

        return results
