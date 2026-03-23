#!/usr/bin/env python3
"""뉴스 타임라인 조회 CLI.

Usage:
    # 최근 24시간 타임라인
    python scripts/news_timeline.py

    # US 뉴스만, 최근 4시간
    python scripts/news_timeline.py --market us --hours 4

    # 특정 티커 뉴스
    python scripts/news_timeline.py --ticker TSLA

    # 브레이킹 뉴스만
    python scripts/news_timeline.py --importance high

    # 요약만
    python scripts/news_timeline.py --summary

    # 요약 + 타임라인
    python scripts/news_timeline.py --summary --hours 12
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.logger import setup_logging
from src.services.news_timeline import NewsTimelineService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="뉴스 타임라인 조회",
    )
    parser.add_argument(
        "--market",
        choices=["kr", "us"],
        default=None,
        help="시장 필터 (kr 또는 us)",
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default=None,
        help="티커 심볼 필터 (예: TSLA, 005930)",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="조회 시간 범위 (기본: 24시간)",
    )
    parser.add_argument(
        "--importance",
        choices=["high", "medium", "low"],
        default=None,
        help="중요도 필터",
    )
    parser.add_argument(
        "--min-sentiment",
        type=float,
        default=None,
        help="최소 감성 점수 필터 (예: 0.3)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="최대 결과 수 (기본: 50)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="요약 통계 출력",
    )
    args = parser.parse_args()

    # 로깅은 최소화 (CLI 출력이 주목적)
    setup_logging(level="WARNING", format="console")

    svc = NewsTimelineService()

    if args.summary:
        summary = svc.get_summary(hours=args.hours)
        print(svc.format_summary(summary))

        # --summary만 있으면 타임라인도 출력하지 않음
        if not any([args.market, args.ticker, args.importance]):
            return

    items = svc.get_timeline(
        market=args.market,
        ticker=args.ticker,
        hours=args.hours,
        importance=args.importance,
        min_sentiment=args.min_sentiment,
        limit=args.limit,
    )

    print(svc.format_for_terminal(items))


if __name__ == "__main__":
    main()
