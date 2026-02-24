"""Repository for per-ticker community sentiment records."""

from __future__ import annotations

from src.core.models import CommunitySentiment
from src.storage.base import BaseRepository


class CommunitySentimentRepository(BaseRepository[CommunitySentiment]):
    """CRUD repository for CommunitySentiment (per-ticker, per-source).

    Stores sentiment from Naver, StockTwits, Reddit for individual stocks.
    """

    def get_by_ticker(
        self,
        ticker: str,
        limit: int = 100,
    ) -> list[CommunitySentiment]:
        """Get sentiment history for a single ticker.

        Args:
            ticker: Stock ticker symbol.
            limit: Max records to return.

        Returns:
            List of CommunitySentiment ordered by date descending.
        """
        return self.get_many(
            filters={"ticker": ticker},
            order_by="date",
            descending=True,
            limit=limit,
        )

    def get_by_date(self, date: str) -> list[CommunitySentiment]:
        """Get all community sentiment for a specific date.

        Args:
            date: Date string (YYYY-MM-DD).

        Returns:
            List of CommunitySentiment.
        """
        return self.get_many(
            filters={"date": date},
            order_by="ticker",
            descending=False,
            limit=500,
        )

    def get_by_source(
        self,
        source: str,
        date: str | None = None,
        limit: int = 100,
    ) -> list[CommunitySentiment]:
        """Get records by source, optionally filtered by date.

        Args:
            source: Source name (e.g., "naver", "stocktwits", "reddit").
            date: Optional date filter.
            limit: Max records.

        Returns:
            List of CommunitySentiment.
        """
        filters: dict[str, str] = {"source": source}
        if date:
            filters["date"] = date
        return self.get_many(
            filters=filters,
            order_by="date",
            descending=True,
            limit=limit,
        )
