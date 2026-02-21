"""Repository for MarketSnapshot CRUD and domain queries."""

from __future__ import annotations

from sqlalchemy import select

from src.core.database import MarketSnapshotDB, get_session
from src.core.models import Market, MarketSnapshot
from src.storage.base import BaseRepository


class MarketSnapshotRepository(BaseRepository[MarketSnapshot]):
    """Repository for market snapshots with domain-specific queries."""

    def get_latest(self, limit: int = 10) -> list[MarketSnapshot]:
        """Get the most recent market snapshots.

        Args:
            limit: Maximum number of items.

        Returns:
            List of MarketSnapshot sorted by created_at descending.
        """
        return self.get_many(order_by="created_at", descending=True, limit=limit)

    def get_by_date(self, date: str) -> list[MarketSnapshot]:
        """Get all snapshots for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format.

        Returns:
            List of MarketSnapshot for the given date.
        """
        return self.get_many(
            filters={"date": date},
            order_by="created_at",
            descending=True,
        )

    def get_by_market(self, market: Market, limit: int = 20) -> list[MarketSnapshot]:
        """Get snapshots for a specific market.

        Args:
            market: Market enum (KOREA or US).
            limit: Maximum number of items.

        Returns:
            List of MarketSnapshot filtered by market.
        """
        return self.get_many(
            filters={"market": market.value},
            order_by="created_at",
            descending=True,
            limit=limit,
        )

    def get_by_index(
        self,
        index_name: str,
        limit: int = 30,
    ) -> list[MarketSnapshot]:
        """Get snapshots for a specific index.

        Args:
            index_name: Name of the market index (e.g., "KOSPI", "S&P 500").
            limit: Maximum number of items.

        Returns:
            List of MarketSnapshot for the given index.
        """
        return self.get_many(
            filters={"index_name": index_name},
            order_by="date",
            descending=True,
            limit=limit,
        )

    def get_latest_by_market_and_index(
        self,
        market: Market,
        index_name: str,
    ) -> MarketSnapshot | None:
        """Get the most recent snapshot for a market/index pair.

        Args:
            market: Market enum.
            index_name: Index name string.

        Returns:
            The latest MarketSnapshot or None.
        """
        with get_session() as session:
            stmt = (
                select(MarketSnapshotDB)
                .where(MarketSnapshotDB.market == market.value)
                .where(MarketSnapshotDB.index_name == index_name)
                .order_by(MarketSnapshotDB.created_at.desc())
                .limit(1)
            )
            result = session.execute(stmt).scalars().first()
            if result is None:
                return None
            return self._orm_to_pydantic(result)
