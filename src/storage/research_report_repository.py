"""Repository for ResearchReport CRUD and domain queries."""

from __future__ import annotations

from src.core.models import ResearchReport, ResearchType
from src.storage.base import BaseRepository


class ResearchReportRepository(BaseRepository[ResearchReport]):
    """Repository for research reports with domain-specific queries."""

    def get_by_type(
        self,
        research_type: ResearchType,
        limit: int = 20,
    ) -> list[ResearchReport]:
        """Get reports by research type.

        Args:
            research_type: ResearchType enum value.
            limit: Maximum number of results.

        Returns:
            List of ResearchReport sorted by created_at descending.
        """
        return self.get_many(
            filters={"research_type": research_type.value},
            order_by="created_at",
            descending=True,
            limit=limit,
        )

    def get_by_subject(self, subject: str, limit: int = 10) -> list[ResearchReport]:
        """Get reports for a specific subject.

        Args:
            subject: Report subject string (e.g., ticker or sector name).
            limit: Maximum number of results.

        Returns:
            List of ResearchReport filtered by subject.
        """
        return self.get_many(
            filters={"subject": subject},
            order_by="created_at",
            descending=True,
            limit=limit,
        )

    def get_latest(self, limit: int = 10) -> list[ResearchReport]:
        """Get the most recent research reports.

        Args:
            limit: Maximum number of results.

        Returns:
            List of ResearchReport sorted by created_at descending.
        """
        return self.get_many(order_by="created_at", descending=True, limit=limit)
