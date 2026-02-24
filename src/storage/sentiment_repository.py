"""Repository for sentiment history records."""

from __future__ import annotations

from src.core.models import SentimentRecord
from src.storage.base import BaseRepository


class SentimentRepository(BaseRepository[SentimentRecord]):
    """CRUD repository for SentimentRecord (market-level daily indicators).

    Stores CNN Fear & Greed, CBOE Put/Call Ratio, AAII Survey,
    and custom Fear & Greed composite scores.
    """

    def get_by_source(
        self,
        source: str,
        limit: int = 1825,
    ) -> list[SentimentRecord]:
        """Get records by source, ordered by date descending.

        Args:
            source: SentimentSource value (e.g., "cnn_fear_greed").
            limit: Max records to return (default ~5 years).

        Returns:
            List of SentimentRecord.
        """
        return self.get_many(
            filters={"source": source},
            order_by="date",
            descending=True,
            limit=limit,
        )

    def get_by_date_range(
        self,
        source: str,
        start_date: str,
        end_date: str,
    ) -> list[SentimentRecord]:
        """Get records for a source within a date range.

        Args:
            source: SentimentSource value.
            start_date: Start date (YYYY-MM-DD).
            end_date: End date (YYYY-MM-DD).

        Returns:
            List of SentimentRecord ordered by date ascending.
        """
        from sqlalchemy import select

        from src.core.database import SentimentRecordDB, get_session

        with get_session() as session:
            stmt = (
                select(SentimentRecordDB)
                .where(SentimentRecordDB.source == source)
                .where(SentimentRecordDB.date >= start_date)
                .where(SentimentRecordDB.date <= end_date)
                .order_by(SentimentRecordDB.date.asc())
            )
            results = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(obj) for obj in results]

    def get_latest(self, source: str) -> SentimentRecord | None:
        """Get the most recent record for a source.

        Args:
            source: SentimentSource value.

        Returns:
            Latest SentimentRecord or None.
        """
        records = self.get_many(
            filters={"source": source},
            order_by="date",
            descending=True,
            limit=1,
        )
        return records[0] if records else None
