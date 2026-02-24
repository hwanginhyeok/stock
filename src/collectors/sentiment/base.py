"""Base class for sentiment data collectors."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from src.collectors.base import BaseCollector


class BaseSentimentCollector(BaseCollector):
    """Base class for sentiment data collectors.

    Sentiment collectors fetch external sentiment indicators
    (Fear/Greed indices, community opinions, put/call ratios, etc.)
    and return structured results.
    """

    @abstractmethod
    def collect(self) -> list[dict[str, Any]]:
        """Collect sentiment data from external sources.

        Returns:
            List of sentiment data dicts.
        """

    def collect_and_store(self) -> list[dict[str, Any]]:
        """Collect sentiment data and log results.

        Sentiment data is typically consumed in-memory by analyzers
        rather than stored directly in the DB. Override in subclasses
        if DB persistence is needed.

        Returns:
            List of sentiment data dicts.
        """
        results = self.collect()
        self._logger.info(
            "sentiment_collected",
            collector=type(self).__name__,
            count=len(results),
        )
        return results
