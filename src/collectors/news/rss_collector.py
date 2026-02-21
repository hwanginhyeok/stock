"""RSS-based news collector with deduplication and DB storage."""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Any

import feedparser
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors.news.base import BaseNewsCollector
from src.collectors.news.dedup import TitleDeduplicator
from src.core.config import CollectionSettings, NewsSource
from src.core.exceptions import CollectionError
from src.core.models import Market, NewsItem
from src.storage import NewsRepository


class RSSNewsCollector(BaseNewsCollector):
    """Collect news from RSS feeds with deduplication.

    Iterates over configured RSS sources, fetches and parses entries,
    deduplicates against recently stored titles, and optionally
    persists results to the database.
    """

    def __init__(self) -> None:
        super().__init__()
        self._news_config = self._config.news_sources
        self._settings: CollectionSettings = self._news_config.collection
        self._deduplicator = TitleDeduplicator(
            threshold=self._settings.dedup_similarity_threshold,
        )
        self._repo = NewsRepository()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def collect(self) -> list[NewsItem]:
        """Collect news from all configured RSS sources.

        Returns:
            Deduplicated list of NewsItem from all sources.
        """
        all_items: list[NewsItem] = []

        # Korea sources
        for source in self._news_config.korea:
            if not source.enabled:
                continue
            items = self._fetch_source(source, Market.KOREA)
            all_items.extend(items)
            time.sleep(self._settings.request_delay_sec)

        # US sources
        for source in self._news_config.us:
            if not source.enabled:
                continue
            items = self._fetch_source(source, Market.US)
            all_items.extend(items)
            time.sleep(self._settings.request_delay_sec)

        # Deduplicate against each other
        all_items = self._deduplicator.deduplicate(all_items)

        # Deduplicate against recently stored items
        existing_titles = self._repo.get_recent_titles(
            hours=self._settings.dedup_window_hours,
        )
        if existing_titles:
            all_items = [
                item
                for item in all_items
                if not self._deduplicator.is_duplicate(item.title, existing_titles)
            ]

        self._logger.info("rss_collection_complete", total_items=len(all_items))
        return all_items

    def collect_and_store(self) -> list[NewsItem]:
        """Collect news and persist to the database.

        Returns:
            List of persisted NewsItem.
        """
        items = self.collect()
        if not items:
            self._logger.info("no_new_items_to_store")
            return []
        stored = self._repo.create_many(items)
        self._logger.info("news_stored", count=len(stored))
        return stored

    def collect_by_market(self, market: Market) -> list[NewsItem]:
        """Collect news for a single market.

        Args:
            market: Target market.

        Returns:
            Deduplicated list of NewsItem for the market.
        """
        sources = (
            self._news_config.korea
            if market == Market.KOREA
            else self._news_config.us
        )
        all_items: list[NewsItem] = []
        for source in sources:
            if not source.enabled:
                continue
            items = self._fetch_source(source, market)
            all_items.extend(items)
            time.sleep(self._settings.request_delay_sec)

        return self._deduplicator.deduplicate(all_items)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_source(self, source: NewsSource, market: Market) -> list[NewsItem]:
        """Fetch and parse a single RSS source (graceful on failure).

        Args:
            source: News source configuration.
            market: Market enum for tagging.

        Returns:
            List of NewsItem from the source, empty on failure.
        """
        try:
            feed = self._fetch_rss(source.url)
            entries = feed.get("entries", [])[:self._settings.max_articles_per_source]
            items = []
            for entry in entries:
                item = self._parse_entry(entry, source, market)
                if item is not None:
                    items.append(item)
            self._logger.info(
                "source_fetched",
                source=source.name,
                count=len(items),
            )
            return items
        except Exception as e:
            self._logger.warning(
                "source_fetch_failed",
                source=source.name,
                error=str(e),
            )
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _fetch_rss(self, url: str) -> dict[str, Any]:
        """Fetch and parse an RSS feed URL with retry.

        Args:
            url: RSS feed URL.

        Returns:
            Parsed feedparser dict.

        Raises:
            CollectionError: If the feed cannot be fetched.
        """
        response = requests.get(
            url,
            timeout=self._settings.request_timeout_sec,
            headers={"User-Agent": "StockRichBot/1.0"},
        )
        response.raise_for_status()
        feed = feedparser.parse(response.text)
        if feed.bozo and not feed.entries:
            raise CollectionError(
                f"RSS parse error for {url}",
                {"bozo_exception": str(feed.bozo_exception)},
            )
        return feed

    def _parse_entry(
        self,
        entry: Any,
        source: NewsSource,
        market: Market,
    ) -> NewsItem | None:
        """Convert a feedparser entry into a NewsItem.

        Args:
            entry: Feedparser entry dict.
            source: Source configuration.
            market: Market tag.

        Returns:
            NewsItem or None if the entry lacks a title.
        """
        title = getattr(entry, "title", "").strip()
        if not title:
            return None

        # Extract content / summary
        content = ""
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].get("value", "")
        summary = getattr(entry, "summary", "")

        # Clean HTML
        content = self._extract_text(content)
        summary = self._extract_text(summary)

        # Parse published date
        published_at = self._parse_date(entry)

        link = getattr(entry, "link", "")

        return NewsItem(
            title=title,
            content=content,
            summary=summary if summary else content[:300],
            source=source.name,
            url=link,
            category=source.category,
            market=market,
            published_at=published_at,
        )

    @staticmethod
    def _extract_text(html: str) -> str:
        """Strip HTML tags and normalize whitespace.

        Args:
            html: Raw HTML string.

        Returns:
            Plain text string.
        """
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def _parse_date(entry: Any) -> datetime | None:
        """Extract published date from a feedparser entry.

        Args:
            entry: Feedparser entry dict.

        Returns:
            Timezone-aware datetime or None.
        """
        published_parsed = getattr(entry, "published_parsed", None)
        if published_parsed:
            try:
                return datetime(*published_parsed[:6], tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass
        return None
