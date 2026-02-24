"""CNN Fear & Greed Index collector."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors.sentiment.base import BaseSentimentCollector


# CNN internal data endpoint (unofficial — may break without notice)
_CNN_API_URL = (
    "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
)

_LEVEL_LABELS = {
    (0, 25): "Extreme Fear",
    (25, 45): "Fear",
    (45, 55): "Neutral",
    (55, 75): "Greed",
    (75, 101): "Extreme Greed",
}


def _score_to_level(score: float) -> str:
    """Map a 0-100 score to a human-readable level label.

    Args:
        score: Fear & Greed score (0-100).

    Returns:
        Level label string.
    """
    for (lo, hi), label in _LEVEL_LABELS.items():
        if lo <= score < hi:
            return label
    return "Unknown"


class CNNFearGreedCollector(BaseSentimentCollector):
    """Collect CNN Fear & Greed Index via unofficial API.

    Falls back to the ``fear-and-greed`` PyPI package if the
    direct API call fails.
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch_from_api(self) -> dict[str, Any]:
        """Fetch current Fear & Greed data from CNN's internal endpoint.

        Returns:
            Dict with score, level, timestamp, and components.

        Raises:
            requests.RequestException: On network or HTTP errors.
        """
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        url = f"{_CNN_API_URL}/{today}"
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; StockRichBot/1.0)",
        })
        resp.raise_for_status()
        data = resp.json()

        fg = data.get("fear_and_greed", {})
        score = float(fg.get("score", 0))

        return {
            "source": "cnn_api",
            "score": round(score, 1),
            "level": _score_to_level(score),
            "timestamp": fg.get("timestamp", today),
            "previous_close": float(fg.get("previous_close", 0)),
            "previous_1_week": float(fg.get("previous_1_week", 0)),
            "previous_1_month": float(fg.get("previous_1_month", 0)),
            "previous_1_year": float(fg.get("previous_1_year", 0)),
        }

    def _fetch_from_package(self) -> dict[str, Any]:
        """Fallback: fetch via the ``fear-and-greed`` PyPI package.

        Returns:
            Dict with score, level, and last_update.
        """
        try:
            import fear_and_greed

            result = fear_and_greed.get()
            score = float(result.value)
            return {
                "source": "fear_and_greed_package",
                "score": round(score, 1),
                "level": result.description.replace("_", " ").title(),
                "timestamp": result.last_update.isoformat(),
            }
        except ImportError:
            self._logger.warning(
                "fear_and_greed_package_not_installed",
                hint="pip install fear-and-greed",
            )
            return {}
        except Exception as e:
            self._logger.warning(
                "fear_and_greed_package_failed",
                error=str(e),
            )
            return {}

    def collect(self) -> list[dict[str, Any]]:
        """Collect CNN Fear & Greed Index.

        Tries the direct API first, falls back to the PyPI package.

        Returns:
            Single-element list with Fear & Greed data dict,
            or empty list on total failure.
        """
        # Try direct API
        try:
            data = self._fetch_from_api()
            self._logger.info(
                "cnn_fear_greed_collected",
                score=data["score"],
                level=data["level"],
                source="cnn_api",
            )
            return [data]
        except Exception as e:
            self._logger.warning(
                "cnn_api_failed_trying_package",
                error=str(e),
            )

        # Fallback to package
        data = self._fetch_from_package()
        if data:
            self._logger.info(
                "cnn_fear_greed_collected",
                score=data["score"],
                level=data["level"],
                source="package_fallback",
            )
            return [data]

        self._logger.error("cnn_fear_greed_collection_failed")
        return []
