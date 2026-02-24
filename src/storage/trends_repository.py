"""Repository for Google Trends interest records."""

from __future__ import annotations

from src.core.models import TrendsRecord
from src.storage.base import BaseRepository


class TrendsRepository(BaseRepository[TrendsRecord]):
    """CRUD repository for TrendsRecord (Google Trends data).

    Stores search interest data for stocks and keywords over time.
    """

    def get_by_keyword(
        self,
        keyword: str,
        limit: int = 365,
    ) -> list[TrendsRecord]:
        """Get trends history for a keyword.

        Args:
            keyword: Search keyword (e.g., "NVDA", "삼성전자").
            limit: Max records.

        Returns:
            List of TrendsRecord ordered by date descending.
        """
        return self.get_many(
            filters={"keyword": keyword},
            order_by="date",
            descending=True,
            limit=limit,
        )

    def get_by_date(self, date: str) -> list[TrendsRecord]:
        """Get all trends data for a specific date.

        Args:
            date: Date string (YYYY-MM-DD).

        Returns:
            List of TrendsRecord.
        """
        return self.get_many(
            filters={"date": date},
            order_by="keyword",
            descending=False,
            limit=500,
        )
