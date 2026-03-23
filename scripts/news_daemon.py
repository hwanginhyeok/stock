#!/usr/bin/env python3
"""뉴스 수집 데몬 — 실시간 뉴스 수집 스케줄러 + 1회성 수집 CLI.

Usage:
    # 데몬 모드 (스케줄러 실행, 장중 30분/장외 2시간 간격)
    python scripts/news_daemon.py

    # 1회성 수집
    python scripts/news_daemon.py --once

    # 1회성 + 감성분석 포함
    python scripts/news_daemon.py --once --with-sentiment

    # KR만 수집
    python scripts/news_daemon.py --once --market kr

    # US만 수집
    python scripts/news_daemon.py --once --market us
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.logger import setup_logging
from src.workflows.news_scheduler import NewsCollectionScheduler


def main() -> None:
    parser = argparse.ArgumentParser(
        description="뉴스 수집 데몬 — 실시간 뉴스 수집 스케줄러",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="1회성 수집 후 종료 (데몬 모드 비활성)",
    )
    parser.add_argument(
        "--market",
        choices=["kr", "us"],
        default=None,
        help="특정 시장만 수집 (kr 또는 us)",
    )
    parser.add_argument(
        "--with-sentiment",
        action="store_true",
        help="감성분석 포함 (Claude API 비용 발생)",
    )
    parser.add_argument(
        "--log-format",
        choices=["json", "console"],
        default="console",
        help="로그 출력 형식 (기본: console)",
    )
    args = parser.parse_args()

    setup_logging(level="INFO", format=args.log_format)

    scheduler = NewsCollectionScheduler(
        analyze_sentiment=args.with_sentiment,
    )

    if args.once:
        result = scheduler.run_once(market_str=args.market)
        print(f"\n  ✅ {result.summary()}\n")
        if result.errors:
            for err in result.errors:
                print(f"  ⚠️  {err}")
            print()
        sys.exit(0 if not result.errors else 1)
    else:
        print("\n  🚀 뉴스 수집 데몬 시작 (Ctrl+C로 종료)\n")
        scheduler.start()


if __name__ == "__main__":
    main()
