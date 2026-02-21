"""Repository for Article CRUD and domain queries."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from src.core.database import ArticleDB, get_session
from src.core.models import Article, ArticleType
from src.storage.base import BaseRepository


class ArticleRepository(BaseRepository[Article]):
    """Repository for generated articles with domain-specific queries."""

    def get_by_type(
        self,
        article_type: ArticleType,
        limit: int = 20,
    ) -> list[Article]:
        """Get articles by type.

        Args:
            article_type: ArticleType enum value.
            limit: Maximum number of results.

        Returns:
            List of Article sorted by created_at descending.
        """
        return self.get_many(
            filters={"article_type": article_type.value},
            order_by="created_at",
            descending=True,
            limit=limit,
        )

    def get_by_date_range(
        self,
        start: datetime,
        end: datetime,
        article_type: ArticleType | None = None,
    ) -> list[Article]:
        """Get articles within a date range.

        Args:
            start: Range start (inclusive).
            end: Range end (inclusive).
            article_type: Optional type filter.

        Returns:
            List of Article within the date range.
        """
        with get_session() as session:
            stmt = (
                select(ArticleDB)
                .where(ArticleDB.created_at >= start)
                .where(ArticleDB.created_at <= end)
            )
            if article_type is not None:
                stmt = stmt.where(ArticleDB.article_type == article_type.value)
            stmt = stmt.order_by(ArticleDB.created_at.desc())
            results = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(obj) for obj in results]

    def get_latest(
        self,
        article_type: ArticleType | None = None,
        limit: int = 10,
    ) -> list[Article]:
        """Get the most recent articles.

        Args:
            article_type: Optional type filter.
            limit: Maximum number of results.

        Returns:
            List of Article sorted by created_at descending.
        """
        filters = {}
        if article_type is not None:
            filters["article_type"] = article_type.value
        return self.get_many(
            filters=filters if filters else None,
            order_by="created_at",
            descending=True,
            limit=limit,
        )
