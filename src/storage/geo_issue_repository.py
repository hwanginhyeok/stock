"""Repository for GeoIssue (geopolitical issue tracking)."""

from __future__ import annotations

from src.core.models import GeoIssue
from src.storage.base import BaseRepository


class GeoIssueRepository(BaseRepository[GeoIssue]):
    """Repository for geopolitical issues."""

    def get_active(self) -> list[GeoIssue]:
        """Get all active geopolitical issues.

        Returns:
            List of active GeoIssue instances.
        """
        return self.get_many(
            filters={"status": "active"},
            order_by="created_at",
            limit=100,
        )

    def get_by_status(self, status: str) -> list[GeoIssue]:
        """Get issues by status.

        Args:
            status: Issue status (active, monitoring, resolved).

        Returns:
            List of matching GeoIssue instances.
        """
        return self.get_many(
            filters={"status": status},
            order_by="created_at",
            limit=100,
        )
