"""Repository for NewsItem CRUD and domain queries."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

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
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with get_session() as session:
            stmt = (
                select(NewsItemDB.title)
                .where(NewsItemDB.created_at >= cutoff)
                .order_by(NewsItemDB.created_at.desc())
            )
            results = session.execute(stmt).scalars().all()
            return list(results)

    # ------------------------------------------------------------------
    # Extended queries for timeline & ticker filtering
    # ------------------------------------------------------------------

    def get_by_tickers(
        self,
        tickers: list[str],
        hours: int = 24,
        limit: int = 50,
    ) -> list[NewsItem]:
        """Get news items mentioning any of the given tickers.

        Uses JSON LIKE search on the related_tickers column.

        Args:
            tickers: List of ticker symbols to search for.
            hours: Look-back window in hours.
            limit: Maximum number of results.

        Returns:
            List of matching NewsItem, newest first.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with get_session() as session:
            stmt = (
                select(NewsItemDB)
                .where(NewsItemDB.created_at >= cutoff)
            )
            # Build OR conditions for each ticker (LIKE on JSON text)
            from sqlalchemy import or_
            ticker_conditions = [
                NewsItemDB.related_tickers.contains(f'"{t}"')
                for t in tickers
            ]
            if ticker_conditions:
                stmt = stmt.where(or_(*ticker_conditions))
            stmt = stmt.order_by(NewsItemDB.created_at.desc()).limit(limit)
            results = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(obj) for obj in results]

    def get_by_importance(
        self,
        importance: str,
        hours: int = 24,
        limit: int = 50,
    ) -> list[NewsItem]:
        """Get news items by importance level.

        Args:
            importance: Importance level ("high", "medium", "low").
            hours: Look-back window in hours.
            limit: Maximum number of results.

        Returns:
            List of matching NewsItem, newest first.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with get_session() as session:
            stmt = (
                select(NewsItemDB)
                .where(NewsItemDB.created_at >= cutoff)
                .where(NewsItemDB.importance == importance)
                .order_by(NewsItemDB.created_at.desc())
                .limit(limit)
            )
            results = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(obj) for obj in results]

    def get_timeline(
        self,
        market: Market | None = None,
        hours: int = 24,
        limit: int = 100,
    ) -> list[NewsItem]:
        """Get a chronological news timeline.

        Sorted by published_at when available, falling back to created_at.

        Args:
            market: Optional market filter.
            hours: Look-back window in hours.
            limit: Maximum number of results.

        Returns:
            List of NewsItem sorted by time descending.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with get_session() as session:
            stmt = (
                select(NewsItemDB)
                .where(NewsItemDB.created_at >= cutoff)
            )
            if market is not None:
                stmt = stmt.where(NewsItemDB.market == market.value)
            # published_at이 있으면 그걸로 정렬, 없으면 created_at
            stmt = stmt.order_by(
                func.coalesce(
                    NewsItemDB.published_at,
                    NewsItemDB.created_at,
                ).desc(),
            ).limit(limit)
            results = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(obj) for obj in results]

    def update_sentiment(self, news_id: str, score: float) -> None:
        """Update the sentiment score for a news item.

        Args:
            news_id: UUID of the news item.
            score: New sentiment score (-1.0 to +1.0).
        """
        self.update(news_id, sentiment_score=score)

    def update_tickers(self, news_id: str, tickers: list[str]) -> None:
        """Update the related tickers for a news item.

        Args:
            news_id: UUID of the news item.
            tickers: List of ticker symbols.
        """
        self.update(news_id, related_tickers=tickers)

    def get_stats(self, hours: int = 24) -> dict[str, int]:
        """Get summary statistics for recent news.

        Args:
            hours: Look-back window in hours.

        Returns:
            Dict with total, by_market, and by_importance counts.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with get_session() as session:
            # Total count
            total = session.execute(
                select(func.count())
                .select_from(NewsItemDB)
                .where(NewsItemDB.created_at >= cutoff),
            ).scalar_one()

            # By market
            market_counts = session.execute(
                select(NewsItemDB.market, func.count())
                .where(NewsItemDB.created_at >= cutoff)
                .group_by(NewsItemDB.market),
            ).all()

            # By importance
            imp_counts = session.execute(
                select(NewsItemDB.importance, func.count())
                .where(NewsItemDB.created_at >= cutoff)
                .group_by(NewsItemDB.importance),
            ).all()

            return {
                "total": total,
                "by_market": {m: c for m, c in market_counts},
                "by_importance": {i: c for i, c in imp_counts},
            }
