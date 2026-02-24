"""Google Trends interest collector for stock sentiment proxy."""

from __future__ import annotations

import time
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors.sentiment.base import BaseSentimentCollector


class GoogleTrendsCollector(BaseSentimentCollector):
    """Collect Google Trends interest data as a sentiment proxy.

    Rising search interest for a stock often precedes retail investor
    activity. Sudden spikes can signal fear (crashes) or greed (FOMO).

    Uses the ``pytrends`` library (unofficial Google Trends API).
    """

    def __init__(self, request_delay_sec: float = 2.0) -> None:
        """Initialize with configurable request delay.

        Args:
            request_delay_sec: Seconds to wait between API calls.
        """
        super().__init__()
        self._delay = request_delay_sec
        self._pytrends = None

    def _get_client(self) -> Any:
        """Lazy-initialize pytrends TrendReq client.

        Returns:
            TrendReq instance.

        Raises:
            ImportError: If pytrends is not installed.
        """
        if self._pytrends is None:
            try:
                from pytrends.request import TrendReq
                self._pytrends = TrendReq(
                    hl="en-US",
                    tz=360,
                    timeout=(10, 25),
                    retries=3,
                    backoff_factor=1.0,
                )
            except ImportError:
                self._logger.error(
                    "pytrends_not_installed",
                    hint="pip install pytrends",
                )
                raise
        return self._pytrends

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=5, max=30),
        reraise=True,
    )
    def _fetch_interest(
        self,
        keywords: list[str],
        timeframe: str = "now 7-d",
        geo: str = "",
    ) -> dict[str, dict[str, Any]]:
        """Fetch Google Trends interest over time for keywords.

        Args:
            keywords: List of search terms (max 5 per request).
            timeframe: Trends timeframe (e.g., "now 7-d", "today 1-m").
            geo: Country code (e.g., "US", "KR"). Empty = worldwide.

        Returns:
            Dict of keyword -> interest data dict.

        Raises:
            Exception: On API failure.
        """
        client = self._get_client()
        client.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
        df = client.interest_over_time()

        results: dict[str, dict[str, Any]] = {}

        if df.empty:
            for kw in keywords:
                results[kw] = {
                    "current": 0,
                    "average": 0,
                    "max": 0,
                    "trend_direction": "N/A",
                    "spike_ratio": 0.0,
                }
            return results

        for kw in keywords:
            if kw not in df.columns:
                results[kw] = {
                    "current": 0,
                    "average": 0,
                    "max": 0,
                    "trend_direction": "N/A",
                    "spike_ratio": 0.0,
                }
                continue

            series = df[kw]
            current = int(series.iloc[-1])
            average = float(series.mean())
            max_val = int(series.max())

            # Trend direction: compare last 2 days vs previous 5
            if len(series) >= 7:
                recent = float(series.tail(2).mean())
                earlier = float(series.iloc[-7:-2].mean())
                if earlier > 0:
                    change = (recent - earlier) / earlier
                    if change >= 0.3:
                        direction = "Surging"
                    elif change >= 0.1:
                        direction = "Rising"
                    elif change <= -0.3:
                        direction = "Declining"
                    elif change <= -0.1:
                        direction = "Falling"
                    else:
                        direction = "Stable"
                else:
                    direction = "Stable"
            else:
                direction = "N/A"

            # Spike ratio: current vs average (>2.0 = unusual interest)
            spike = current / average if average > 0 else 0.0

            results[kw] = {
                "current": current,
                "average": round(average, 1),
                "max": max_val,
                "trend_direction": direction,
                "spike_ratio": round(spike, 2),
            }

        return results

    def collect_stock(
        self,
        keyword: str,
        geo: str = "",
        timeframe: str = "now 7-d",
    ) -> dict[str, Any]:
        """Collect Google Trends data for a single stock/keyword.

        Args:
            keyword: Search term (e.g., "NVDA", "삼성전자").
            geo: Country code.
            timeframe: Trends timeframe.

        Returns:
            Dict with keyword, interest metrics, and sentiment proxy.
        """
        try:
            data = self._fetch_interest([keyword], timeframe=timeframe, geo=geo)
            time.sleep(self._delay)
        except ImportError:
            return {
                "keyword": keyword,
                "geo": geo,
                "error": "pytrends not installed",
                "sentiment_score": 0.5,
                "sentiment": "Unknown",
            }
        except Exception as e:
            self._logger.warning(
                "google_trends_fetch_failed",
                keyword=keyword,
                error=str(e),
            )
            return {
                "keyword": keyword,
                "geo": geo,
                "error": str(e),
                "sentiment_score": 0.5,
                "sentiment": "Unknown",
            }

        interest = data.get(keyword, {})

        # Map spike ratio to sentiment score
        # spike > 2.0 = unusual attention (could be fear OR greed)
        # We use direction to disambiguate
        spike = interest.get("spike_ratio", 0.0)
        direction = interest.get("trend_direction", "Stable")

        # Base score from spike (high interest = high attention)
        if spike >= 2.0:
            attention = "Very High"
        elif spike >= 1.5:
            attention = "High"
        elif spike >= 0.8:
            attention = "Normal"
        elif spike >= 0.5:
            attention = "Low"
        else:
            attention = "Very Low"

        # Sentiment score: surging interest is ambiguous,
        # but generally correlates with momentum
        sentiment_score = min(1.0, max(0.0, spike / 2.0))
        if direction in ("Declining", "Falling"):
            sentiment_score = max(0.0, sentiment_score - 0.2)

        # Label
        if sentiment_score >= 0.7:
            sentiment = "Very High Interest"
        elif sentiment_score >= 0.55:
            sentiment = "High Interest"
        elif sentiment_score >= 0.45:
            sentiment = "Normal Interest"
        elif sentiment_score >= 0.3:
            sentiment = "Low Interest"
        else:
            sentiment = "Very Low Interest"

        self._logger.info(
            "google_trends_collected",
            keyword=keyword,
            current=interest.get("current", 0),
            spike=spike,
            direction=direction,
            attention=attention,
        )

        return {
            "keyword": keyword,
            "geo": geo,
            "current_interest": interest.get("current", 0),
            "average_interest": interest.get("average", 0),
            "max_interest": interest.get("max", 0),
            "trend_direction": direction,
            "spike_ratio": spike,
            "attention_level": attention,
            "sentiment_score": round(sentiment_score, 3),
            "sentiment": sentiment,
        }

    def collect(self) -> list[dict[str, Any]]:
        """Collect Google Trends data for configured watchlist stocks.

        Fetches US stocks with geo="US" and Korean stocks with geo="KR".

        Returns:
            List of per-keyword trend data dicts.
        """
        results: list[dict[str, Any]] = []

        # US watchlist
        us_watchlist = self._config.market.us.watchlist
        for item in us_watchlist:
            if item.ticker.startswith("^"):
                continue
            data = self.collect_stock(item.ticker, geo="US")
            results.append(data)

        # Korean watchlist (use stock names for better Korean search results)
        kr_watchlist = self._config.market.korea.watchlist
        for item in kr_watchlist:
            data = self.collect_stock(item.name, geo="KR")
            results.append(data)

        return results

    def collect_comparison(
        self,
        keywords: list[str],
        geo: str = "",
        timeframe: str = "now 7-d",
    ) -> list[dict[str, Any]]:
        """Compare Google Trends interest across multiple keywords.

        Useful for comparing relative interest between competing stocks
        (e.g., AAPL vs MSFT vs GOOGL).

        Args:
            keywords: Up to 5 keywords to compare.
            geo: Country code.
            timeframe: Trends timeframe.

        Returns:
            List of per-keyword dicts with relative interest data.
        """
        # Google Trends API allows max 5 keywords per request
        batch = keywords[:5]

        try:
            data = self._fetch_interest(batch, timeframe=timeframe, geo=geo)
        except Exception as e:
            self._logger.warning(
                "google_trends_comparison_failed",
                keywords=batch,
                error=str(e),
            )
            return []

        results = []
        for kw in batch:
            interest = data.get(kw, {})
            results.append({
                "keyword": kw,
                "geo": geo,
                "current_interest": interest.get("current", 0),
                "average_interest": interest.get("average", 0),
                "trend_direction": interest.get("trend_direction", "N/A"),
                "spike_ratio": interest.get("spike_ratio", 0.0),
            })

        return results
