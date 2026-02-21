"""Abstract base class for news collectors."""

from __future__ import annotations

from abc import abstractmethod

from src.collectors.base import BaseCollector
from src.core.models import Market, NewsItem


class BaseNewsCollector(BaseCollector):
    """Base class for news data collectors.

    Adds a market-specific collection method on top of BaseCollector.
    """

    @abstractmethod
    def collect_by_market(self, market: Market) -> list[NewsItem]:
        """Collect news for a specific market.

        Args:
            market: Target market (KOREA or US).

        Returns:
            List of collected NewsItem for the given market.
        """
