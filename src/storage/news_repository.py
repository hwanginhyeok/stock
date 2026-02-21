"""Repository for NewsItem CRUD and domain queries."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from src.core.database import NewsItemDB, get_session
from src.core.models import Market, NewsItem
from src.storage.base import BaseRepository


class NewsRepository(BaseRepository[NewsItem]):
    """Repository for news items with domain-specific queries."""

    def get_latest(self, limit: int = 20) -> list[NewsItem]:
        """Get the most recent news items.

        Args:
            limit: Maximum number of items.

        Returns:
            List of NewsItem sorted by created_at descending.
        """
        return self.get_many(order_by="created_at", descending=True, limit=limit)

    def get_by_market(self, market: Market, limit: int = 50) -> list[NewsItem]:
        """Get news items for a specific market.

        Args:
            market: Market enum (KOREA or US).
            limit: Maximum number of items.

        Returns:
            List of NewsItem filtered by market.
        """
        return self.get_many(
            filters={"market": market.value},
            order_by="created_at",
            descending=True,
            limit=limit,
        )

    def get_by_date_range(
        self,
        start: datetime,
        end: datetime,
        market: Market | None = None,
    ) -> list[NewsItem]:
        """Get news items within a date range.

        Args:
            start: Range start (inclusive).
            end: Range end (inclusive).
            market: Optional market filter.

        Returns:
            List of NewsItem within the date range.
        """
        with get_session() as session:
            stmt = (
                select(NewsItemDB)
                .where(NewsItemDB.created_at >= start)
                .where(NewsItemDB.created_at <= end)
            )
            if market is not None:
                stmt = stmt.where(NewsItemDB.market == market.value)
            stmt = stmt.order_by(NewsItemDB.created_at.desc())
            results = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(obj) for obj in results]

    def get_by_category(self, category: str, limit: int = 50) -> list[NewsItem]:
        """Get news items by category.

        Args:
            category: News category string.
            limit: Maximum number of items.

        Returns:
            List of NewsItem filtered by category.
        """
        return self.get_many(
            filters={"category": category},
            order_by="created_at",
            descending=True,
            limit=limit,
        )

    def get_recent_titles(self, hours: int = 24) -> list[str]:
        """Get titles of news items from the last N hours.

        Used by deduplicator to check for existing titles.

        Args:
            hours: Number of hours to look back.

        Returns:
            List of title strings.
        """
        cutoff = datetime.now(timezone.utc).replace(
            hour=datetime.now(timezone.utc).hour,
        )
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with get_session() as session:
            stmt = (
                select(NewsItemDB.title)
                .where(NewsItemDB.created_at >= cutoff)
                .order_by(NewsItemDB.created_at.desc())
            )
            results = session.execute(stmt).scalars().all()
            return list(results)
