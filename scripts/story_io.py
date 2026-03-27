#!/usr/bin/env python3
"""Story tracker I/O helper for Claude Code session-based classification.

Subcommands:
    unclassified  - Print unclassified news for Claude to read and classify
    apply         - Apply Claude's classification JSON from stdin or file
    briefing      - Print active story briefing
    stats         - Print story thread statistics
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

# Capture real stdout before anything touches it, then redirect stdout to devnull
# so all structlog/print during import goes nowhere.
_out = os.fdopen(os.dup(1), "w")  # fd 1 = real stdout
_devnull = open(os.devnull, "w")
os.dup2(_devnull.fileno(), 1)  # stdout fd now points to /dev/null

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.database import init_db  # noqa: E402
from src.core.models import (  # noqa: E402
    Market,
    NewsStoryLink,
    StoryStatus,
    StoryThread,
)
from src.storage import (  # noqa: E402
    NewsRepository,
    NewsStoryLinkRepository,
    StoryThreadRepository,
)


def _restore_stdout() -> None:
    """Restore real stdout after all imports and init are done."""
    os.dup2(_out.fileno(), 1)
    sys.stdout = os.fdopen(1, "w")


def cmd_unclassified(args: argparse.Namespace) -> None:
    """Print unclassified news articles as JSON for Claude to classify."""
    news_repo = NewsRepository()
    link_repo = NewsStoryLinkRepository()
    story_repo = StoryThreadRepository()

    classified_ids = link_repo.get_classified_news_ids()

    market_filter = None
    if args.market != "all":
        market_filter = Market("korea" if args.market == "kr" else "us")

    if market_filter:
        all_news = news_repo.get_by_market(market_filter, limit=500)
    else:
        all_news = news_repo.get_latest(limit=500)

    unclassified = [n for n in all_news if n.id not in classified_ids]

    market_str = market_filter.value if market_filter else None
    active = story_repo.get_active_summaries(market_str)

    output = {
        "unclassified": [
            {
                "id": n.id,
                "title": n.title,
                "source": n.source,
                "market": n.market,
                "summary": (n.summary or n.content)[:200],
                "published_at": str(n.published_at or n.created_at),
            }
            for n in unclassified
        ],
        "active_stories": active,
    }

    _restore_stdout()
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_apply(args: argparse.Namespace) -> None:
    """Apply classification results from JSON.

    Supports placeholder story_ids (e.g. '__mideast__') that reference
    a 'new' story in the same batch. The first 'new' action creates
    the story; subsequent 'existing' actions with the same placeholder
    are resolved to the created story's real ID.
    """
    story_repo = StoryThreadRepository()
    link_repo = NewsStoryLinkRepository()

    _restore_stdout()

    if args.file:
        data = json.loads(Path(args.file).read_text())
    else:
        data = json.loads(sys.stdin.read())

    classifications = data.get("classifications", [])
    now = datetime.now(timezone.utc)
    new_count = 0
    existing_count = 0
    skip_count = 0

    # Map placeholder story_ids to real DB IDs
    alias_map: dict[str, str] = {}

    # Two-pass: first create all 'new' stories and build alias map
    for item in classifications:
        if item["action"] != "new":
            continue
        news_id = item["news_id"]
        market = item.get("market", "korea")
        relevance = item.get("relevance_score", 1.0)

        story = StoryThread(
            title=item["title"],
            summary=item.get("summary", ""),
            market=Market(market),
            status=StoryStatus.ACTIVE,
            related_tickers=item.get("tickers", []),
            article_count=1,
            first_seen_at=now,
            last_updated_at=now,
        )
        created = story_repo.create(story)

        # Link the first news to this story
        link = NewsStoryLink(
            news_id=news_id,
            story_id=created.id,
            relevance_score=relevance,
        )
        link_repo.create(link)
        new_count += 1

        # Register alias for placeholder resolution
        if "alias" in item:
            alias_map[item["alias"]] = created.id

    # Second pass: link 'existing' items, resolving placeholders
    for item in classifications:
        if item["action"] != "existing":
            continue
        news_id = item["news_id"]
        story_id = item["story_id"]
        relevance = item.get("relevance_score", 1.0)

        # Resolve placeholder (starts with __)
        if story_id.startswith("__"):
            real_id = alias_map.get(story_id)
            if not real_id:
                skip_count += 1
                continue
            story_id = real_id

        link = NewsStoryLink(
            news_id=news_id,
            story_id=story_id,
            relevance_score=relevance,
        )
        link_repo.create(link)
        story_repo.increment_article_count(story_id)
        existing_count += 1

    stale = story_repo.mark_stale(hours=48)
    msg = f"Applied: {new_count} new stories, {existing_count} existing matches"
    if skip_count:
        msg += f", {skip_count} skipped (unresolved placeholder)"
    if stale:
        msg += f", {stale} marked stale"
    print(msg)


def cmd_briefing(args: argparse.Namespace) -> None:
    """Print active story briefing."""
    story_repo = StoryThreadRepository()
    link_repo = NewsStoryLinkRepository()

    market = None
    if args.market != "all":
        market = "korea" if args.market == "kr" else "us"

    stories = story_repo.get_active(market)

    _restore_stdout()

    if not stories:
        print("No active stories.")
        return

    print(f"=== Active Stories ({len(stories)}) ===\n")
    for i, s in enumerate(stories, 1):
        news = link_repo.get_news_for_story(s.id)
        tickers = ", ".join(s.related_tickers) if s.related_tickers else "-"
        print(
            f"{i}. [{s.market.upper() if hasattr(s.market, 'upper') else s.market}] {s.title}\n"
            f"   Summary: {s.summary}\n"
            f"   Tickers: {tickers} | Articles: {s.article_count}\n"
            f"   First: {s.first_seen_at} | Last: {s.last_updated_at}"
        )
        for n in news[:5]:
            print(f"     - {n['title'][:70]} ({n['source']})")
        if len(news) > 5:
            print(f"     ... +{len(news) - 5} more")
        print()


def cmd_stats(args: argparse.Namespace) -> None:
    """Print story thread statistics."""
    story_repo = StoryThreadRepository()
    link_repo = NewsStoryLinkRepository()
    news_repo = NewsRepository()

    classified_ids = link_repo.get_classified_news_ids()
    total_news = news_repo.count()
    active = story_repo.get_active()
    stale = story_repo.get_many(filters={"status": "stale"}, limit=1000)

    _restore_stdout()
    print(f"Total news in DB: {total_news}")
    print(f"Classified: {len(classified_ids)}")
    print(f"Unclassified: {total_news - len(classified_ids)}")
    print(f"Active stories: {len(active)}")
    print(f"Stale stories: {len(stale)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Story tracker I/O helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_unc = sub.add_parser("unclassified", help="Print unclassified news")
    p_unc.add_argument("--market", choices=["kr", "us", "all"], default="all")

    p_app = sub.add_parser("apply", help="Apply classification JSON")
    p_app.add_argument("--file", help="JSON file path (default: stdin)")

    p_br = sub.add_parser("briefing", help="Print active story briefing")
    p_br.add_argument("--market", choices=["kr", "us", "all"], default="all")

    sub.add_parser("stats", help="Print statistics")

    args = parser.parse_args()
    init_db()

    {"unclassified": cmd_unclassified, "apply": cmd_apply,
     "briefing": cmd_briefing, "stats": cmd_stats}[args.command](args)


if __name__ == "__main__":
    main()
