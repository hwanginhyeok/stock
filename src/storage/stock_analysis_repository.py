"""Repository for StockAnalysis CRUD and domain queries."""

from __future__ import annotations

from sqlalchemy import select

from src.core.database import StockAnalysisDB, get_session
from src.core.models import Market, StockAnalysis
from src.storage.base import BaseRepository


class StockAnalysisRepository(BaseRepository[StockAnalysis]):
    """Repository for stock analyses with domain-specific queries."""

    def get_by_ticker(self, ticker: str, limit: int = 10) -> list[StockAnalysis]:
        """Get analyses for a specific ticker.

        Args:
            ticker: Stock ticker symbol.
            limit: Maximum number of results.

        Returns:
            List of StockAnalysis sorted by date descending.
        """
        return self.get_many(
            filters={"ticker": ticker},
            order_by="created_at",
            descending=True,
            limit=limit,
        )

    def get_by_date(
        self,
        date: str,
        market: Market | None = None,
    ) -> list[StockAnalysis]:
        """Get all analyses for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format.
            market: Optional market filter.

        Returns:
            List of StockAnalysis for the given date.
        """
        filters: dict[str, str] = {"date": date}
        if market is not None:
            filters["market"] = market.value
        return self.get_many(
            filters=filters,
            order_by="composite_score",
            descending=True,
        )

    def get_top_scores(
        self,
        market: Market | None = None,
        limit: int = 10,
    ) -> list[StockAnalysis]:
        """Get analyses with the highest composite scores.

        Args:
            market: Optional market filter.
            limit: Maximum number of results.

        Returns:
            List of StockAnalysis sorted by composite_score descending.
        """
        filters = {}
        if market is not None:
            filters["market"] = market.value
        return self.get_many(
            filters=filters if filters else None,
            order_by="composite_score",
            descending=True,
            limit=limit,
        )

    def get_latest_by_ticker(self, ticker: str) -> StockAnalysis | None:
        """Get the most recent analysis for a ticker.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            The latest StockAnalysis or None.
        """
        with get_session() as session:
            stmt = (
                select(StockAnalysisDB)
                .where(StockAnalysisDB.ticker == ticker)
                .order_by(StockAnalysisDB.created_at.desc())
                .limit(1)
            )
            result = session.execute(stmt).scalars().first()
            if result is None:
                return None
            return self._orm_to_pydantic(result)
