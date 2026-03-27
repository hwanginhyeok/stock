#!/usr/bin/env python3
"""Classify collected news into story threads using Claude API.

Usage:
    python scripts/classify_news.py --market kr
    python scripts/classify_news.py --market us
    python scripts/classify_news.py --market all
    python scripts/classify_news.py --market kr --briefing
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.database import init_db
from src.analyzers.story_classifier import StoryClassifier


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify news into story threads")
    parser.add_argument(
        "--market",
        choices=["kr", "us", "all"],
        required=True,
        help="Target market: kr, us, or all",
    )
    parser.add_argument(
        "--briefing",
        action="store_true",
        help="Print active story briefing after classification",
    )
    args = parser.parse_args()

    # Ensure tables exist
    init_db()

    classifier = StoryClassifier()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if args.market == "all":
        stats_kr = classifier.classify_unclassified("korea")
        stats_us = classifier.classify_unclassified("us")
        print(
            f"[{now}] KR: {stats_kr['total_classified']} classified "
            f"({stats_kr['new_stories']} new, {stats_kr['existing_matches']} existing)"
        )
        print(
            f"[{now}] US: {stats_us['total_classified']} classified "
            f"({stats_us['new_stories']} new, {stats_us['existing_matches']} existing)"
        )
    else:
        market = "korea" if args.market == "kr" else "us"
        stats = classifier.classify_unclassified(market)
        label = args.market.upper()
        print(
            f"[{now}] {label}: {stats['total_classified']} classified "
            f"({stats['new_stories']} new, {stats['existing_matches']} existing)"
        )

    if args.briefing:
        print()
        if args.market in ("kr", "all"):
            print(classifier.get_story_briefing("korea"))
        if args.market in ("us", "all"):
            print(classifier.get_story_briefing("us"))


if __name__ == "__main__":
    main()
