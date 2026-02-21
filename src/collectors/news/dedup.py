"""Title-based deduplication for news items."""

from __future__ import annotations

import difflib

from src.core.logger import get_logger
from src.core.models import NewsItem

logger = get_logger(__name__)


class TitleDeduplicator:
    """Deduplicate news items based on title similarity.

    Uses ``difflib.SequenceMatcher`` for fuzzy string matching.

    Args:
        threshold: Similarity ratio above which titles are considered
            duplicates. Defaults to 0.85.
    """

    def __init__(self, threshold: float = 0.85) -> None:
        self._threshold = threshold

    def is_duplicate(self, title: str, existing_titles: list[str]) -> bool:
        """Check if a title is a near-duplicate of any existing title.

        Args:
            title: The candidate title.
            existing_titles: List of titles already collected.

        Returns:
            True if the title matches any existing title above threshold.
        """
        normalized = title.strip().lower()
        for existing in existing_titles:
            ratio = difflib.SequenceMatcher(
                None,
                normalized,
                existing.strip().lower(),
            ).ratio()
            if ratio >= self._threshold:
                logger.debug(
                    "duplicate_detected",
                    title=title[:60],
                    matched=existing[:60],
                    ratio=round(ratio, 3),
                )
                return True
        return False

    def deduplicate(self, items: list[NewsItem]) -> list[NewsItem]:
        """Remove near-duplicate news items, keeping the first occurrence.

        Args:
            items: List of NewsItem to deduplicate.

        Returns:
            Deduplicated list of NewsItem.
        """
        seen_titles: list[str] = []
        unique: list[NewsItem] = []
        for item in items:
            if not self.is_duplicate(item.title, seen_titles):
                unique.append(item)
                seen_titles.append(item.title)
        removed = len(items) - len(unique)
        if removed:
            logger.info(
                "dedup_complete",
                original=len(items),
                unique=len(unique),
                removed=removed,
            )
        return unique
