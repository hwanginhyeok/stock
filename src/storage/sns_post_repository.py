"""Repository for SNSPost CRUD and domain queries."""

from __future__ import annotations

from src.core.models import PostStatus, SNSPlatform, SNSPost
from src.storage.base import BaseRepository


class SNSPostRepository(BaseRepository[SNSPost]):
    """Repository for SNS posts with domain-specific queries."""

    def get_by_platform(
        self,
        platform: SNSPlatform,
        limit: int = 50,
    ) -> list[SNSPost]:
        """Get posts for a specific platform.

        Args:
            platform: SNSPlatform enum value.
            limit: Maximum number of results.

        Returns:
            List of SNSPost sorted by created_at descending.
        """
        return self.get_many(
            filters={"platform": platform.value},
            order_by="created_at",
            descending=True,
            limit=limit,
        )

    def get_by_status(
        self,
        status: PostStatus,
        limit: int = 50,
    ) -> list[SNSPost]:
        """Get posts by status.

        Args:
            status: PostStatus enum value.
            limit: Maximum number of results.

        Returns:
            List of SNSPost filtered by status.
        """
        return self.get_many(
            filters={"status": status.value},
            order_by="created_at",
            descending=True,
            limit=limit,
        )

    def get_pending(self, limit: int = 20) -> list[SNSPost]:
        """Get posts waiting to be published.

        Includes both DRAFT and SCHEDULED statuses.

        Args:
            limit: Maximum number of results.

        Returns:
            List of pending SNSPost.
        """
        draft = self.get_many(
            filters={"status": PostStatus.DRAFT.value},
            order_by="created_at",
            descending=False,
            limit=limit,
        )
        scheduled = self.get_many(
            filters={"status": PostStatus.SCHEDULED.value},
            order_by="created_at",
            descending=False,
            limit=limit,
        )
        combined = draft + scheduled
        combined.sort(key=lambda p: p.created_at)
        return combined[:limit]

    def update_status(
        self,
        post_id: str,
        status: PostStatus,
        error_message: str = "",
    ) -> SNSPost | None:
        """Update a post's publishing status.

        Args:
            post_id: UUID of the post.
            status: New PostStatus value.
            error_message: Optional error message for failed posts.

        Returns:
            The updated SNSPost or None if not found.
        """
        updates: dict[str, str | int] = {"status": status.value}
        if error_message:
            updates["error_message"] = error_message
        if status == PostStatus.FAILED:
            existing = self.get_by_id(post_id)
            if existing:
                updates["retry_count"] = existing.retry_count + 1
        return self.update(post_id, **updates)
