"""Fetch and store 10 years of historical OHLCV price data.

Fetches data for all configured watchlist stocks and indices
(US via yfinance, KR via pykrx) and stores in the database.

Usage:
    python -m scripts.fetch_historical_prices
    python -m scripts.fetch_historical_prices --years 5
    python -m scripts.fetch_historical_prices --ticker AAPL
    python -m scripts.fetch_historical_prices --market us
"""

from __future__ import annotations

import argparse
import sys

from src.backtesting.data.price_loader import PriceLoader
from src.core.database import init_db
from src.core.logger import get_logger
from src.core.models import Market
from src.storage.ohlcv_repository import OHLCVRepository

logger = get_logger("fetch_prices")


def main() -> None:
    """Run historical price data fetch."""
    parser = argparse.ArgumentParser(
        description="Fetch historical OHLCV price data",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=10,
        help="Number of years of history (default: 10)",
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default="",
        help="Fetch only a specific ticker",
    )
    parser.add_argument(
        "--market",
        choices=["us", "korea", "all"],
        default="all",
        help="Which market to fetch (default: all)",
    )
    args = parser.parse_args()

    init_db()
    repo = OHLCVRepository()
    loader = PriceLoader(repo)

    if args.ticker:
        # Single ticker mode
        market = Market.KOREA if len(args.ticker) == 6 and args.ticker.isdigit() else Market.US
        count = loader.fetch_and_store(
            args.ticker, market=market, years=args.years,
        )
        print(f"\n{args.ticker}: {count:,}건 저장")
        return

    # Full watchlist mode
    print(f"\n전체 워치리스트 가격 데이터 수집 ({args.years}년치)")
    print("=" * 50)

    results = loader.fetch_all_watchlist(years=args.years)

    total = sum(results.values())
    print(f"\n{'=' * 50}")
    print(f"수집 완료: 총 {total:,}건")
    print(f"{'=' * 50}")

    for ticker, count in sorted(results.items()):
        status = f"{count:>6,}건" if count > 0 else "  실패"
        print(f"  {ticker:>10s}: {status}")


if __name__ == "__main__":
    main()
