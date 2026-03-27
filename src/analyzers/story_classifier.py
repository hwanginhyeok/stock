"""AI-powered news story classifier using Claude API.

Reads unclassified news, groups them into story threads by semantic
similarity (not keywords), and maintains story history over time.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.core.claude_client import ClaudeClient
from src.core.logger import get_logger
from src.core.models import (
    ClaudeTask,
    Market,
    NewsItem,
    NewsStoryLink,
    StoryStatus,
    StoryThread,
)
from src.storage import NewsRepository, NewsStoryLinkRepository, StoryThreadRepository

logger = get_logger(__name__)

_SYSTEM_PROMPT = """\
You are a news story classifier for a Korean/US stock market analysis platform.

Your job: given a batch of new articles and a list of existing active story threads,
classify each article into EXACTLY ONE story thread (existing or new).

A "story thread" is a DEVELOPING NARRATIVE — not a topic or keyword.
Examples:
- "Trump tariff escalation on China" is ONE story that develops over days
- "Fed rate decision March 2026" is ONE story
- Two unrelated articles about Samsung are NOT the same story

Rules:
1. Match to an existing story ONLY if the article is genuinely about the same developing event/narrative
2. Create a NEW story if no existing story fits (even if tickers overlap)
3. Each article maps to exactly one story
4. For new stories, write a concise title (Korean for KR market, English for US) and a 1-sentence summary
5. Return valid JSON only, no markdown fences

Output format:
{
  "classifications": [
    {
      "news_id": "...",
      "action": "existing",
      "story_id": "...",
      "relevance_score": 0.95
    },
    {
      "news_id": "...",
      "action": "new",
      "new_story": {
        "title": "...",
        "summary": "...",
        "related_tickers": ["TSLA", "NVDA"]
      },
      "relevance_score": 1.0
    }
  ]
}
"""

# Max articles per API call to stay within context limits
_BATCH_SIZE = 30


class StoryClassifier:
    """Classify news articles into semantic story threads using Claude."""

    def __init__(self) -> None:
        self._claude = ClaudeClient()
        self._news_repo = NewsRepository()
        self._story_repo = StoryThreadRepository()
        self._link_repo = NewsStoryLinkRepository()
        logger.info("story_classifier_initialized")

    def classify_unclassified(self, market: str | None = None) -> dict[str, int]:
        """Classify all unclassified news articles.

        Args:
            market: Optional market filter ('korea' or 'us').

        Returns:
            Dict with counts: new_stories, existing_matches, total_classified.
        """
        # 1. Get unclassified news
        unclassified = self._get_unclassified_news(market)
        if not unclassified:
            logger.info("no_unclassified_news", market=market)
            return {"new_stories": 0, "existing_matches": 0, "total_classified": 0}

        logger.info(
            "unclassified_news_found",
            count=len(unclassified),
            market=market,
        )

        # 2. Process in batches
        stats = {"new_stories": 0, "existing_matches": 0, "total_classified": 0}

        for i in range(0, len(unclassified), _BATCH_SIZE):
            batch = unclassified[i : i + _BATCH_SIZE]
            batch_stats = self._classify_batch(batch, market)
            for k in stats:
                stats[k] += batch_stats[k]

        # 3. Mark stale stories (no updates in 48h)
        stale_count = self._story_repo.mark_stale(hours=48)
        if stale_count:
            logger.info("stories_marked_stale", count=stale_count)

        logger.info("classification_complete", **stats)
        return stats

    def _get_unclassified_news(self, market: str | None) -> list[NewsItem]:
        """Get news items that haven't been classified yet."""
        classified_ids = self._link_repo.get_classified_news_ids()

        if market:
            all_news = self._news_repo.get_by_market(
                Market(market), limit=500,
            )
        else:
            all_news = self._news_repo.get_latest(limit=500)

        return [n for n in all_news if n.id not in classified_ids]

    def _classify_batch(
        self,
        articles: list[NewsItem],
        market: str | None,
    ) -> dict[str, int]:
        """Classify a batch of articles via Claude API."""
        # Build prompt
        active_stories = self._story_repo.get_active_summaries(market)
        prompt = self._build_prompt(articles, active_stories)

        # Call Claude
        response = self._claude.generate(
            ClaudeTask.SUMMARY,
            prompt,
            system_prompt=_SYSTEM_PROMPT,
        )

        # Parse response
        try:
            result = json.loads(response.content)
            classifications = result["classifications"]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(
                "classification_parse_error",
                error=str(e),
                response_preview=response.content[:200],
            )
            return {"new_stories": 0, "existing_matches": 0, "total_classified": 0}

        # Apply classifications
        return self._apply_classifications(classifications, market)

    def _build_prompt(
        self,
        articles: list[NewsItem],
        active_stories: list[dict],
    ) -> str:
        """Build the classification prompt."""
        parts = []

        # Existing stories
        if active_stories:
            parts.append("## Existing Active Stories\n")
            for s in active_stories:
                parts.append(
                    f"- ID: {s['id']}\n"
                    f"  Title: {s['title']}\n"
                    f"  Summary: {s['summary']}\n"
                    f"  Articles so far: {s['article_count']}\n"
                )
        else:
            parts.append("## No existing active stories — all will be new.\n")

        # New articles to classify
        parts.append("\n## New Articles to Classify\n")
        for a in articles:
            parts.append(
                f"- ID: {a.id}\n"
                f"  Title: {a.title}\n"
                f"  Source: {a.source}\n"
                f"  Market: {a.market}\n"
                f"  Summary: {a.summary[:200]}\n"
            )

        return "\n".join(parts)

    def _apply_classifications(
        self,
        classifications: list[dict[str, Any]],
        market: str | None,
    ) -> dict[str, int]:
        """Apply classification results to DB."""
        stats = {"new_stories": 0, "existing_matches": 0, "total_classified": 0}
        now = datetime.now(timezone.utc)

        for item in classifications:
            news_id = item.get("news_id", "")
            action = item.get("action", "")
            relevance = item.get("relevance_score", 1.0)

            if action == "existing":
                story_id = item.get("story_id", "")
                if not story_id:
                    continue
                # Link news to existing story
                link = NewsStoryLink(
                    news_id=news_id,
                    story_id=story_id,
                    relevance_score=relevance,
                )
                self._link_repo.create(link)
                self._story_repo.increment_article_count(story_id)
                stats["existing_matches"] += 1

            elif action == "new":
                new_info = item.get("new_story", {})
                if not new_info.get("title"):
                    continue
                # Create new story thread
                story = StoryThread(
                    title=new_info["title"],
                    summary=new_info.get("summary", ""),
                    market=Market(market) if market else Market.KOREA,
                    status=StoryStatus.ACTIVE,
                    related_tickers=new_info.get("related_tickers", []),
                    article_count=1,
                    first_seen_at=now,
                    last_updated_at=now,
                )
                created = self._story_repo.create(story)

                # Link news to new story
                link = NewsStoryLink(
                    news_id=news_id,
                    story_id=created.id,
                    relevance_score=relevance,
                )
                self._link_repo.create(link)
                stats["new_stories"] += 1

            stats["total_classified"] += 1

        return stats

    def get_story_briefing(self, market: str | None = None) -> str:
        """Generate a text briefing of all active stories.

        Args:
            market: Optional market filter.

        Returns:
            Formatted briefing string.
        """
        stories = self._story_repo.get_active(market)
        if not stories:
            return "No active stories."

        lines = [f"=== Active Stories ({len(stories)}) ===\n"]
        for i, s in enumerate(stories, 1):
            news = self._link_repo.get_news_for_story(s.id)
            tickers = ", ".join(s.related_tickers) if s.related_tickers else "-"
            lines.append(
                f"{i}. [{s.market.upper()}] {s.title}\n"
                f"   Summary: {s.summary}\n"
                f"   Tickers: {tickers}\n"
                f"   Articles: {s.article_count} | "
                f"First: {s.first_seen_at:%m/%d %H:%M} | "
                f"Last: {s.last_updated_at:%m/%d %H:%M}\n"
            )
            for n in news[:5]:
                lines.append(f"     - {n['title'][:60]} ({n['source']})\n")
            if len(news) > 5:
                lines.append(f"     ... +{len(news) - 5} more\n")
            lines.append("")

        return "\n".join(lines)
