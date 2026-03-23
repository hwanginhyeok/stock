"""Repository for StoryThread and NewsStoryLink CRUD and queries."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update

from src.core.database import (
    NewsItemDB,
    NewsStoryLinkDB,
    StoryThreadDB,
    get_session,
)
from src.core.models import NewsStoryLink, StoryStatus, StoryThread
from src.storage.base import BaseRepository


class StoryThreadRepository(BaseRepository[StoryThread]):
    """Repository for story threads with domain-specific queries."""

    def get_active(self, market: str | None = None) -> list[StoryThread]:
        """Get all active story threads, optionally filtered by market.

        Args:
            market: Optional market filter ('korea' or 'us').

        Returns:
            List of active StoryThread sorted by last_updated_at desc.
        """
        filters: dict[str, str] = {"status": StoryStatus.ACTIVE}
        if market:
            filters["market"] = market
        return self.get_many(
            filters=filters,
            order_by="last_updated_at",
            descending=True,
            limit=200,
        )

    def get_active_summaries(self, market: str | None = None) -> list[dict]:
        """Get lightweight summaries of active stories for classification prompt.

        Args:
            market: Optional market filter.

        Returns:
            List of dicts with id, title, summary, article_count.
        """
        stories = self.get_active(market)
        return [
            {
                "id": s.id,
                "title": s.title,
                "summary": s.summary,
                "article_count": s.article_count,
            }
            for s in stories
        ]

    def increment_article_count(self, story_id: str) -> None:
        """Increment article_count and update last_updated_at.

        Args:
            story_id: The story thread ID.
        """
        now = datetime.now(timezone.utc)
        with get_session() as session:
            stmt = (
                update(StoryThreadDB)
                .where(StoryThreadDB.id == story_id)
                .values(
                    article_count=StoryThreadDB.article_count + 1,
                    last_updated_at=now,
                )
            )
            session.execute(stmt)

    def mark_stale(self, hours: int = 48) -> int:
        """Mark active stories with no updates in N hours as stale.

        Args:
            hours: Hours since last update to consider stale.

        Returns:
            Number of stories marked stale.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with get_session() as session:
            stmt = (
                update(StoryThreadDB)
                .where(StoryThreadDB.status == StoryStatus.ACTIVE)
                .where(StoryThreadDB.last_updated_at < cutoff)
                .values(status=StoryStatus.STALE)
            )
            result = session.execute(stmt)
            return result.rowcount  # type: ignore[return-value]


class NewsStoryLinkRepository(BaseRepository[NewsStoryLink]):
    """Repository for news-story link mappings."""

    def get_classified_news_ids(self) -> set[str]:
        """Get all news IDs that have already been classified.

        Returns:
            Set of news_id strings.
        """
        with get_session() as session:
            stmt = select(NewsStoryLinkDB.news_id)
            results = session.execute(stmt).scalars().all()
            return set(results)

    def get_news_for_story(self, story_id: str) -> list[dict]:
        """Get all news items linked to a story thread.

        Args:
            story_id: The story thread ID.

        Returns:
            List of dicts with news title, source, url, published_at.
        """
        with get_session() as session:
            stmt = (
                select(
                    NewsItemDB.title,
                    NewsItemDB.source,
                    NewsItemDB.url,
                    NewsItemDB.published_at,
                    NewsItemDB.created_at,
                    NewsStoryLinkDB.relevance_score,
                )
                .join(NewsStoryLinkDB, NewsItemDB.id == NewsStoryLinkDB.news_id)
                .where(NewsStoryLinkDB.story_id == story_id)
                .order_by(NewsItemDB.created_at.desc())
            )
            rows = session.execute(stmt).all()
            return [
                {
                    "title": r.title,
                    "source": r.source,
                    "url": r.url,
                    "published_at": str(r.published_at or r.created_at),
                    "relevance_score": r.relevance_score,
                }
                for r in rows
            ]
