"""Generic base repository with CRUD operations."""

from __future__ import annotations

import json
from typing import Any, Generic, TypeVar, get_args, get_origin

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.core.database import (
    Base,
    _JSON_FIELDS,
    _get_orm_map,
    get_session,
    pydantic_to_orm,
)
from src.core.exceptions import DatabaseError
from src.core.logger import get_logger
from src.core.models import BaseEntity

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(Generic[T]):
    """Generic CRUD repository for Pydantic domain models.

    Handles ORM conversion internally so callers only work with
    Pydantic models.

    Example::

        repo = NewsRepository()
        item = repo.create(NewsItem(title="Test"))
        items = repo.get_many(filters={"market": "korea"}, limit=10)
    """

    def __init__(self) -> None:
        self._orm_map = _get_orm_map()
        self._pydantic_type = self._resolve_pydantic_type()
        self._orm_class = self._orm_map.get(self._pydantic_type)
        if self._orm_class is None:
            raise DatabaseError(
                f"No ORM mapping for {self._pydantic_type.__name__}",
                {"model_type": self._pydantic_type.__name__},
            )
        logger.debug(
            "repository_initialized",
            model=self._pydantic_type.__name__,
            orm=self._orm_class.__name__,
        )

    def _resolve_pydantic_type(self) -> type[T]:
        """Resolve the concrete Pydantic type from Generic[T]."""
        for base in type(self).__orig_bases__:  # type: ignore[attr-defined]
            origin = get_origin(base)
            if origin is BaseRepository or origin is type(self).__bases__[0]:
                args = get_args(base)
                if args:
                    return args[0]
        raise DatabaseError(
            "Cannot resolve generic type parameter T",
            {"class": type(self).__name__},
        )

    def _orm_to_pydantic(self, orm_obj: Base) -> T:
        """Convert an ORM instance back to a Pydantic model.

        Automatically deserializes JSON string fields.

        Args:
            orm_obj: SQLAlchemy ORM instance.

        Returns:
            Pydantic model instance.
        """
        data: dict[str, Any] = {}
        for column in orm_obj.__table__.columns:
            key = column.name
            value = getattr(orm_obj, key)
            if key in _JSON_FIELDS and isinstance(value, str):
                try:
                    value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass
            data[key] = value
        return self._pydantic_type.model_validate(data)

    def create(self, model: T) -> T:
        """Insert a single entity.

        Args:
            model: Pydantic model to insert.

        Returns:
            The inserted model with any DB-generated defaults.
        """
        with get_session() as session:
            orm_obj = pydantic_to_orm(model)
            session.add(orm_obj)
            session.flush()
            result = self._orm_to_pydantic(orm_obj)
        logger.debug("entity_created", model=self._pydantic_type.__name__, id=model.id)
        return result

    def create_many(self, models: list[T]) -> list[T]:
        """Bulk insert multiple entities.

        Args:
            models: List of Pydantic models to insert.

        Returns:
            List of inserted models.
        """
        if not models:
            return []
        with get_session() as session:
            orm_objects = [pydantic_to_orm(m) for m in models]
            session.add_all(orm_objects)
            session.flush()
            results = [self._orm_to_pydantic(obj) for obj in orm_objects]
        logger.debug(
            "entities_created",
            model=self._pydantic_type.__name__,
            count=len(results),
        )
        return results

    def get_by_id(self, entity_id: str) -> T | None:
        """Retrieve an entity by its UUID.

        Args:
            entity_id: UUID string.

        Returns:
            The matching model or None.
        """
        with get_session() as session:
            orm_obj = session.get(self._orm_class, entity_id)
            if orm_obj is None:
                return None
            return self._orm_to_pydantic(orm_obj)

    def get_many(
        self,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        descending: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[T]:
        """Query entities with optional filters, ordering, and pagination.

        Args:
            filters: Column-value pairs for WHERE clauses.
            order_by: Column name to order by.
            descending: Sort direction (default: descending).
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            List of matching models.
        """
        with get_session() as session:
            stmt = select(self._orm_class)
            stmt = self._apply_filters(stmt, filters)
            if order_by and hasattr(self._orm_class, order_by):
                col = getattr(self._orm_class, order_by)
                stmt = stmt.order_by(col.desc() if descending else col.asc())
            stmt = stmt.limit(limit).offset(offset)
            results = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(obj) for obj in results]

    def update(self, entity_id: str, **updates: Any) -> T | None:
        """Partially update an entity by ID.

        Args:
            entity_id: UUID string.
            **updates: Column-value pairs to update.

        Returns:
            The updated model or None if not found.
        """
        with get_session() as session:
            orm_obj = session.get(self._orm_class, entity_id)
            if orm_obj is None:
                return None
            for key, value in updates.items():
                if hasattr(orm_obj, key):
                    if key in _JSON_FIELDS and not isinstance(value, str):
                        value = json.dumps(value, ensure_ascii=False, default=str)
                    setattr(orm_obj, key, value)
            session.flush()
            result = self._orm_to_pydantic(orm_obj)
        logger.debug(
            "entity_updated",
            model=self._pydantic_type.__name__,
            id=entity_id,
            fields=list(updates.keys()),
        )
        return result

    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID.

        Args:
            entity_id: UUID string.

        Returns:
            True if deleted, False if not found.
        """
        with get_session() as session:
            orm_obj = session.get(self._orm_class, entity_id)
            if orm_obj is None:
                return False
            session.delete(orm_obj)
        logger.debug(
            "entity_deleted",
            model=self._pydantic_type.__name__,
            id=entity_id,
        )
        return True

    def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count entities matching optional filters.

        Args:
            filters: Column-value pairs for WHERE clauses.

        Returns:
            Number of matching entities.
        """
        with get_session() as session:
            stmt = select(func.count()).select_from(self._orm_class)
            stmt = self._apply_filters(stmt, filters)
            return session.execute(stmt).scalar_one()

    def _apply_filters(self, stmt: Any, filters: dict[str, Any] | None) -> Any:
        """Apply column=value filters to a SELECT statement."""
        if not filters:
            return stmt
        for key, value in filters.items():
            if hasattr(self._orm_class, key):
                col = getattr(self._orm_class, key)
                stmt = stmt.where(col == value)
        return stmt

    def _query_with_session(
        self,
        session: Session,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        descending: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[T]:
        """Run a filtered query within an existing session (for subclass use)."""
        stmt = select(self._orm_class)
        stmt = self._apply_filters(stmt, filters)
        if order_by and hasattr(self._orm_class, order_by):
            col = getattr(self._orm_class, order_by)
            stmt = stmt.order_by(col.desc() if descending else col.asc())
        stmt = stmt.limit(limit).offset(offset)
        results = session.execute(stmt).scalars().all()
        return [self._orm_to_pydantic(obj) for obj in results]
