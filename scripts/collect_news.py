#!/usr/bin/env python3
"""Standalone news collection script for cron scheduling.

Usage:
    python scripts/collect_news.py --market kr
    python scripts/collect_news.py --market us
    python scripts/collect_news.py --market all
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.collectors.news import RSSNewsCollector
from src.core.models import Market


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect news from RSS sources")
    parser.add_argument(
        "--market",
        choices=["kr", "us", "all"],
        required=True,
        help="Target market: kr, us, or all",
    )
    args = parser.parse_args()

    collector = RSSNewsCollector()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if args.market == "all":
        items = collector.collect_and_store()
        print(f"[{now}] ALL: {len(items)} articles stored")
    elif args.market == "kr":
        items = collector.collect_by_market(Market.KOREA)
        # store via repo directly
        if items:
            stored = collector._repo.create_many(items)
            print(f"[{now}] KR: {len(stored)} articles stored")
        else:
            print(f"[{now}] KR: 0 articles (no new items)")
    else:
        items = collector.collect_by_market(Market.US)
        if items:
            stored = collector._repo.create_many(items)
            print(f"[{now}] US: {len(stored)} articles stored")
        else:
            print(f"[{now}] US: 0 articles (no new items)")


if __name__ == "__main__":
    main()
