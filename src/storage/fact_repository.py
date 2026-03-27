"""Repository for NewsFact entities with domain-specific queries."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select

from src.core.database import NewsFactDB, get_session
from src.core.models import NewsFact
from src.storage.base import BaseRepository


class NewsFactRepository(BaseRepository[NewsFact]):
    """Repository for extracted news facts."""

    def get_by_news_id(self, news_id: str) -> list[NewsFact]:
        """Get all facts extracted from a specific news article.

        Args:
            news_id: UUID of the source news item.

        Returns:
            List of facts linked to the news article.
        """
        return self.get_many(filters={"news_id": news_id}, limit=100)

    def get_by_market(
        self, market: str, limit: int = 200
    ) -> list[NewsFact]:
        """Get facts filtered by market.

        Args:
            market: 'korea' or 'us'.
            limit: Maximum number of facts to return.

        Returns:
            List of facts for the given market, newest first.
        """
        return self.get_many(
            filters={"market": market},
            order_by="extracted_at",
            limit=limit,
        )

    def get_recent(
        self,
        hours: int = 12,
        market: str | None = None,
        limit: int = 500,
    ) -> list[NewsFact]:
        """Get facts extracted within the last N hours.

        Args:
            hours: Lookback window in hours.
            market: Optional market filter.
            limit: Maximum number of facts to return.

        Returns:
            List of recent facts, newest first.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with get_session() as session:
            stmt = (
                select(NewsFactDB)
                .where(NewsFactDB.extracted_at >= cutoff)
            )
            if market:
                stmt = stmt.where(NewsFactDB.market == market)
            stmt = stmt.order_by(NewsFactDB.extracted_at.desc()).limit(limit)
            rows = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(r) for r in rows]

    def get_processed_news_ids(self) -> set[str]:
        """Get the set of news IDs that already have extracted facts.

        Returns:
            Set of news_id strings.
        """
        with get_session() as session:
            stmt = select(NewsFactDB.news_id).distinct()
            rows = session.execute(stmt).scalars().all()
            return set(rows)

    def get_by_type(
        self, fact_type: str, market: str | None = None, limit: int = 100
    ) -> list[NewsFact]:
        """Get facts filtered by type (numerical, earnings, policy, etc).

        Args:
            fact_type: The fact type to filter by.
            market: Optional market filter.
            limit: Maximum results.

        Returns:
            List of matching facts.
        """
        filters: dict[str, Any] = {"fact_type": fact_type}
        if market:
            filters["market"] = market
        return self.get_many(
            filters=filters, order_by="extracted_at", limit=limit
        )

    def get_by_ticker(self, ticker: str, limit: int = 50) -> list[NewsFact]:
        """Get facts mentioning a specific ticker.

        Uses LIKE query since tickers is a JSON array stored as text.
        Input is escaped via json.dumps() to prevent JSON breakage.

        Args:
            ticker: Ticker symbol to search for (e.g. "TSLA", "BTC").
            limit: Maximum results.

        Returns:
            List of facts mentioning the ticker.

        Raises:
            ValueError: If ticker is empty or None.
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError(f"Invalid ticker: {ticker!r}")
        ticker = ticker.strip()
        if not ticker:
            raise ValueError("Ticker cannot be empty")

        # json.dumps escapes special characters safely
        search_pattern = json.dumps(ticker)

        with get_session() as session:
            stmt = (
                select(NewsFactDB)
                .where(NewsFactDB.tickers.contains(search_pattern))
                .order_by(NewsFactDB.extracted_at.desc())
                .limit(limit)
            )
            rows = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(r) for r in rows]
