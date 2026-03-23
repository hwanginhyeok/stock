#!/usr/bin/env python3
"""Generate market briefing in 오선 style.

Usage::

    python scripts/generate_briefing.py --schedule morning
    python scripts/generate_briefing.py --schedule evening
    python scripts/generate_briefing.py --schedule morning --no-market  # skip yfinance
    python scripts/generate_briefing.py --schedule morning --save       # save to file
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.database import init_db  # noqa: E402
from src.generators.briefing_generator import (  # noqa: E402
    generate_briefing,
    generate_naver_html,
    save_briefing,
    save_naver_html,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate market briefing (오선 style)",
    )
    parser.add_argument(
        "--schedule",
        choices=["morning", "evening"],
        required=True,
        help="morning (06:00 KST: US recap + KR prep) or evening (18:00: KR recap + US prep)",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=12,
        help="Lookback hours for facts (default: 12)",
    )
    parser.add_argument(
        "--no-market",
        action="store_true",
        help="Skip live market data fetch (faster, facts only)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save briefing to data/briefings/",
    )
    parser.add_argument(
        "--naver",
        action="store_true",
        help="Generate Naver blog HTML (인라인 CSS, 복붙용)",
    )

    args = parser.parse_args()

    try:
        init_db()
    except Exception as e:
        print(f"Error: database init failed — {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.naver:
            html = generate_naver_html(
                schedule=args.schedule,
                hours=args.hours,
                fetch_market=not args.no_market,
            )
            path = save_naver_html(html, args.schedule)
            print(f"Naver HTML saved → {path}")
            print(f"Chrome에서 열고 Ctrl+A → Ctrl+C → 네이버 에디터에 Ctrl+V")
            sys.exit(0)

        text = generate_briefing(
            schedule=args.schedule,
            hours=args.hours,
            fetch_market=not args.no_market,
        )
        print(text)

        if args.save:
            path = save_briefing(text, args.schedule)
            print(f"\nSaved → {path}", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
