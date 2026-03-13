"""Batch-fetch OHLCV data for S&P 500 + NASDAQ 100 constituents.

Usage::

    python -m scripts.fetch_index_universe                    # 전체 (S&P500 + NDX100, 10년)
    python -m scripts.fetch_index_universe --years 5          # 5년치
    python -m scripts.fetch_index_universe --index sp500      # S&P 500만
    python -m scripts.fetch_index_universe --index ndx100     # NASDAQ 100만
    python -m scripts.fetch_index_universe --delay 2.0        # 요청 간격 조절
    python -m scripts.fetch_index_universe --start-from MSFT  # 중단 지점부터 재개
    python -m scripts.fetch_index_universe --dry-run          # 종목 목록만 확인
"""

from __future__ import annotations

import argparse
import sys
import time

from src.collectors.market.constituents import (
    fetch_ndx100_tickers,
    fetch_sp500_tickers,
    get_combined_universe,
)
from src.core.database import init_db
from src.core.logger import get_logger
from src.core.models import Market
from src.backtesting.data.price_loader import PriceLoader

logger = get_logger("fetch_index_universe")


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        description="S&P 500 + NASDAQ 100 OHLCV 일괄 수집",
    )
    parser.add_argument(
        "--index",
        choices=["sp500", "ndx100", "all"],
        default="all",
        help="수집 대상 인덱스 (기본: all)",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=10,
        help="수집할 연도 수 (기본: 10)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="요청 간 대기 시간(초) (기본: 1.0)",
    )
    parser.add_argument(
        "--start-from",
        type=str,
        default=None,
        help="이 티커부터 수집 시작 (알파벳순 재개용)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="종목 목록만 출력하고 수집하지 않음",
    )
    return parser


def _get_tickers(index: str) -> list[str]:
    """Get ticker list based on the selected index.

    Args:
        index: One of "sp500", "ndx100", or "all".

    Returns:
        Sorted list of ticker symbols.
    """
    if index == "sp500":
        return fetch_sp500_tickers()
    if index == "ndx100":
        return fetch_ndx100_tickers()
    return get_combined_universe()


def main() -> None:
    """Run the batch OHLCV fetch process."""
    parser = _build_parser()
    args = parser.parse_args()

    print(f"[*] 인덱스: {args.index} | 기간: {args.years}년 | 딜레이: {args.delay}초")

    tickers = _get_tickers(args.index)
    if not tickers:
        print("[!] 종목 목록을 가져올 수 없습니다.")
        sys.exit(1)

    # Apply --start-from filter
    if args.start_from:
        start = args.start_from.upper()
        try:
            idx = next(i for i, t in enumerate(tickers) if t >= start)
            skipped = idx
            tickers = tickers[idx:]
            print(f"[*] --start-from {start}: {skipped}개 스킵, {len(tickers)}개 남음")
        except StopIteration:
            print(f"[!] '{start}' 이후 종목이 없습니다.")
            sys.exit(1)

    print(f"[*] 대상 종목: {len(tickers)}개")

    if args.dry_run:
        for i, ticker in enumerate(tickers, 1):
            print(f"  {i:4d}. {ticker}")
        print(f"\n[*] 총 {len(tickers)}개 종목 (dry-run, 수집 없음)")
        return

    # Initialize database
    init_db()

    loader = PriceLoader()
    success = 0
    failed = 0
    total_records = 0
    failed_tickers: list[str] = []

    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] {ticker} ... ", end="", flush=True)
        try:
            count = loader.fetch_and_store(
                ticker, market=Market.US, years=args.years,
            )
            total_records += count
            success += 1
            if count > 0:
                print(f"신규 {count}건")
            else:
                print("이미 최신")
        except Exception as e:
            failed += 1
            failed_tickers.append(ticker)
            print(f"실패: {e}")
            logger.error("fetch_failed", ticker=ticker, error=str(e))

        if i < len(tickers):
            time.sleep(args.delay)

    # Summary
    print("\n" + "=" * 50)
    print(f"[완료] 성공: {success} | 실패: {failed} | 신규 레코드: {total_records}")
    if failed_tickers:
        print(f"[실패 종목] {', '.join(failed_tickers)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
