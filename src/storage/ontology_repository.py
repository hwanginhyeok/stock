"""Repositories for ontology objects: Entity, Event, Link, Reaction, Thesis."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update

from src.core.database import (
    NewsStoryLinkDB,
    OntologyEntityDB,
    OntologyEventDB,
    OntologyLinkDB,
    get_session,
)
from src.core.models import (
    EventStatus,
    LinkType,
    MarketReaction,
    OntologyEntity,
    OntologyEvent,
    OntologyLink,
    Thesis,
)
from src.storage.base import BaseRepository


class OntologyEntityRepository(BaseRepository[OntologyEntity]):
    """Repository for ontology entities with domain-specific queries."""

    def find_by_name(self, name: str) -> OntologyEntity | None:
        """Find an entity by exact name.

        Args:
            name: Entity name to search for.

        Returns:
            Matching entity or None.
        """
        results = self.get_many(filters={"name": name}, limit=1)
        return results[0] if results else None

    def find_by_ticker(self, ticker: str) -> OntologyEntity | None:
        """Find an entity by ticker symbol.

        Args:
            ticker: Ticker symbol (e.g. "TSLA", "BTC").

        Returns:
            Matching entity or None.
        """
        results = self.get_many(filters={"ticker": ticker}, limit=1)
        return results[0] if results else None

    def get_active(self, market: str | None = None) -> list[OntologyEntity]:
        """Get all active entities, optionally filtered by market.

        Args:
            market: Optional market filter ('korea' or 'us').

        Returns:
            List of active entities.
        """
        filters: dict[str, str] = {"status": "active"}
        if market:
            filters["market"] = market
        return self.get_many(filters=filters, order_by="created_at", limit=500)

    def get_summaries(self, market: str | None = None) -> list[dict]:
        """Get lightweight summaries of active entities for prompt output.

        Args:
            market: Optional market filter.

        Returns:
            List of dicts with id, name, entity_type, ticker.
        """
        entities = self.get_active(market)
        return [
            {
                "id": e.id,
                "name": e.name,
                "entity_type": e.entity_type,
                "ticker": e.ticker,
            }
            for e in entities
        ]


class OntologyEventRepository(BaseRepository[OntologyEvent]):
    """Repository for ontology events with domain-specific queries."""

    def get_active(self, market: str | None = None) -> list[OntologyEvent]:
        """Get all developing events, optionally filtered by market.

        Args:
            market: Optional market filter.

        Returns:
            List of developing events sorted by started_at desc.
        """
        filters: dict[str, str] = {"status": EventStatus.DEVELOPING}
        if market:
            filters["market"] = market
        return self.get_many(
            filters=filters,
            order_by="started_at",
            descending=True,
            limit=200,
        )

    def get_summaries(self, market: str | None = None) -> list[dict]:
        """Get lightweight summaries of active events for prompt output.

        Args:
            market: Optional market filter.

        Returns:
            List of dicts with id, title, event_type, severity, article_count.
        """
        events = self.get_active(market)
        return [
            {
                "id": e.id,
                "title": e.title,
                "event_type": e.event_type,
                "severity": e.severity,
                "article_count": e.article_count,
            }
            for e in events
        ]

    def increment_article_count(self, event_id: str) -> None:
        """Increment article_count and update last_article_at.

        Args:
            event_id: The event ID.
        """
        now = datetime.now(timezone.utc)
        with get_session() as session:
            stmt = (
                update(OntologyEventDB)
                .where(OntologyEventDB.id == event_id)
                .values(
                    article_count=OntologyEventDB.article_count + 1,
                    last_article_at=now,
                )
            )
            session.execute(stmt)

    def mark_stale(self, hours: int = 48) -> int:
        """Mark developing events with no new articles in N hours as stale.

        Uses last_article_at (last time an article was linked) rather than
        started_at, so events that keep receiving articles stay active.

        Args:
            hours: Hours since last article to consider stale.

        Returns:
            Number of events marked stale.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with get_session() as session:
            stmt = (
                update(OntologyEventDB)
                .where(OntologyEventDB.status == EventStatus.DEVELOPING)
                .where(OntologyEventDB.last_article_at < cutoff)
                .values(status=EventStatus.STALE)
            )
            result = session.execute(stmt)
            return result.rowcount  # type: ignore[return-value]


class OntologyLinkRepository(BaseRepository[OntologyLink]):
    """Repository for ontology links with graph query support."""

    def get_links_from(
        self, source_type: str, source_id: str, link_type: str | None = None,
    ) -> list[OntologyLink]:
        """Get all outgoing links from a source object.

        Args:
            source_type: Source object type (e.g. 'news', 'event').
            source_id: Source object ID.
            link_type: Optional filter by link type.

        Returns:
            List of outgoing links.
        """
        filters: dict[str, str] = {
            "source_type": source_type,
            "source_id": source_id,
        }
        if link_type:
            filters["link_type"] = link_type
        return self.get_many(filters=filters, limit=500)

    def get_links_to(
        self, target_type: str, target_id: str, link_type: str | None = None,
    ) -> list[OntologyLink]:
        """Get all incoming links to a target object.

        Args:
            target_type: Target object type.
            target_id: Target object ID.
            link_type: Optional filter by link type.

        Returns:
            List of incoming links.
        """
        filters: dict[str, str] = {
            "target_type": target_type,
            "target_id": target_id,
        }
        if link_type:
            filters["link_type"] = link_type
        return self.get_many(filters=filters, limit=500)

    def link_exists(
        self, link_type: str, source_type: str, source_id: str,
        target_type: str, target_id: str,
    ) -> bool:
        """Check if a specific link already exists.

        Args:
            link_type: Link type.
            source_type: Source object type.
            source_id: Source object ID.
            target_type: Target object type.
            target_id: Target object ID.

        Returns:
            True if the link exists.
        """
        with get_session() as session:
            stmt = (
                select(OntologyLinkDB.id)
                .where(OntologyLinkDB.link_type == link_type)
                .where(OntologyLinkDB.source_type == source_type)
                .where(OntologyLinkDB.source_id == source_id)
                .where(OntologyLinkDB.target_type == target_type)
                .where(OntologyLinkDB.target_id == target_id)
                .limit(1)
            )
            return session.execute(stmt).first() is not None

    def get_processed_news_ids(self) -> set[str]:
        """Get all news IDs that have been processed by the ontology extractor.

        A news item is considered processed if it has at least one outgoing
        'mentions' or 'triggers' link.

        Returns:
            Set of news_id strings.
        """
        with get_session() as session:
            stmt = (
                select(OntologyLinkDB.source_id)
                .where(OntologyLinkDB.source_type == "news")
                .where(
                    OntologyLinkDB.link_type.in_(
                        [LinkType.MENTIONS, LinkType.TRIGGERS],
                    ),
                )
            )
            results = session.execute(stmt).scalars().all()

            # Also include news from legacy story_threads (already classified)
            legacy_stmt = select(NewsStoryLinkDB.news_id)
            legacy_results = session.execute(legacy_stmt).scalars().all()

            return set(results) | set(legacy_results)

    def count_by_type(self) -> dict[str, int]:
        """Count links grouped by link_type in a single query.

        Returns:
            Dict mapping link_type to count.
        """
        with get_session() as session:
            stmt = (
                select(
                    OntologyLinkDB.link_type,
                    func.count(OntologyLinkDB.id),
                )
                .group_by(OntologyLinkDB.link_type)
            )
            rows = session.execute(stmt).all()
            return {row[0]: row[1] for row in rows}


class MarketReactionRepository(BaseRepository[MarketReaction]):
    """Repository for market reactions."""

    def get_for_event(self, event_id: str) -> list[MarketReaction]:
        """Get all reactions to a specific event.

        Args:
            event_id: The event ID.

        Returns:
            List of reactions sorted by observed_at.
        """
        return self.get_many(
            filters={"event_id": event_id},
            order_by="observed_at",
            descending=True,
            limit=100,
        )


class ThesisRepository(BaseRepository[Thesis]):
    """Repository for investment theses."""

    def get_active(self, market: str | None = None) -> list[Thesis]:
        """Get all active theses, optionally filtered by market.

        Args:
            market: Optional market filter.

        Returns:
            List of active theses sorted by strength desc.
        """
        filters: dict[str, str] = {"status": "active"}
        if market:
            filters["market"] = market
        return self.get_many(
            filters=filters, order_by="strength", descending=True, limit=100,
        )
