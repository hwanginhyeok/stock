"""Backfill historical sentiment data into the database.

Run once to populate:
- CNN Fear & Greed: ~5 years of daily data
- CBOE Put/Call Ratio: full history (~18 years, equity/total/index)
- AAII Investor Sentiment Survey: full history (~38 years)

Usage:
    python -m scripts.backfill_sentiment
    python -m scripts.backfill_sentiment --source cnn
    python -m scripts.backfill_sentiment --source cboe
    python -m scripts.backfill_sentiment --source aaii
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from io import BytesIO, StringIO
from typing import Any

import pandas as pd
import requests

from src.core.database import init_db
from src.core.logger import get_logger
from src.core.models import SentimentRecord, SentimentSource
from src.storage import SentimentRepository

logger = get_logger("backfill_sentiment")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


# ============================================================
# CNN Fear & Greed Backfill
# ============================================================


def _backfill_cnn_fear_greed(repo: SentimentRepository) -> int:
    """Backfill CNN Fear & Greed index history (~5 years).

    Returns:
        Number of records inserted.
    """
    logger.info("backfill_cnn_start")

    start_date = (datetime.now(tz=timezone.utc) - timedelta(days=365 * 5)).strftime(
        "%Y-%m-%d"
    )
    url = f"https://production.dataviz.cnn.io/index/fearandgreed/graphdata/{start_date}"

    try:
        resp = requests.get(url, timeout=30, headers=_HEADERS)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error("cnn_backfill_fetch_failed", error=str(e))
        return 0

    historical = data.get("fear_and_greed_historical", {}).get("data", [])
    if not historical:
        logger.warning("cnn_no_historical_data")
        return 0

    # Check existing records to avoid duplicates
    latest = repo.get_latest(SentimentSource.CNN_FEAR_GREED)
    latest_date = latest.date if latest else ""

    records: list[SentimentRecord] = []
    for point in historical:
        ts = point.get("x", 0)
        score = point.get("y", 0)

        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        date_str = dt.strftime("%Y-%m-%d")

        if date_str <= latest_date:
            continue

        # Classify level
        if score >= 75:
            level = "Extreme Greed"
        elif score >= 55:
            level = "Greed"
        elif score >= 45:
            level = "Neutral"
        elif score >= 25:
            level = "Fear"
        else:
            level = "Extreme Fear"

        records.append(
            SentimentRecord(
                date=date_str,
                source=SentimentSource.CNN_FEAR_GREED,
                score=round(score, 1),
                level=level,
                components={"raw_timestamp": ts},
            )
        )

    if records:
        repo.create_many(records)

    logger.info("backfill_cnn_complete", count=len(records))
    return len(records)


# ============================================================
# CBOE Put/Call Ratio Backfill
# ============================================================

_CBOE_URLS = {
    "total": (
        "https://www.cboe.com/publish/ScheduledTask/MktData/datahouse/totalpc.csv",
        SentimentSource.CBOE_PUTCALL_TOTAL,
    ),
    "equity": (
        "https://www.cboe.com/publish/ScheduledTask/MktData/datahouse/equitypc.csv",
        SentimentSource.CBOE_PUTCALL_EQUITY,
    ),
    "index": (
        "https://www.cboe.com/publish/ScheduledTask/MktData/datahouse/indexpc.csv",
        SentimentSource.CBOE_PUTCALL_INDEX,
    ),
}


def _classify_putcall(ratio: float) -> str:
    """Classify put/call ratio into sentiment level."""
    if ratio >= 1.2:
        return "Extreme Fear"
    if ratio >= 1.0:
        return "Fear"
    if ratio >= 0.7:
        return "Neutral"
    if ratio >= 0.5:
        return "Greed"
    return "Extreme Greed"


def _backfill_cboe_putcall(repo: SentimentRepository) -> int:
    """Backfill CBOE Put/Call Ratio full history.

    Returns:
        Total number of records inserted across all 3 types.
    """
    logger.info("backfill_cboe_start")
    total = 0

    for ratio_type, (url, source) in _CBOE_URLS.items():
        try:
            resp = requests.get(url, timeout=30, headers=_HEADERS)
            resp.raise_for_status()

            df = pd.read_csv(
                StringIO(resp.text),
                header=2,
                index_col=0,
                parse_dates=True,
            )
            df = df.dropna(how="all")

            if df.empty:
                logger.warning("cboe_empty_csv", type=ratio_type)
                continue

            # Check existing
            latest = repo.get_latest(source)
            latest_date = latest.date if latest else ""

            records: list[SentimentRecord] = []
            for idx in range(len(df)):
                row = df.iloc[idx]
                date_val = df.index[idx]
                date_str = (
                    str(date_val.date())
                    if hasattr(date_val, "date")
                    else str(date_val)
                )

                if date_str <= latest_date:
                    continue

                pc_ratio = float(row.get("P/C Ratio", 0))
                calls = int(row.get("CALLS", 0))
                puts = int(row.get("PUTS", 0))

                records.append(
                    SentimentRecord(
                        date=date_str,
                        source=source,
                        score=round(pc_ratio, 4),
                        level=_classify_putcall(pc_ratio),
                        components={
                            "calls": calls,
                            "puts": puts,
                            "total": calls + puts,
                            "pc_ratio": round(pc_ratio, 4),
                        },
                    )
                )

            if records:
                # Batch insert in chunks of 500
                for i in range(0, len(records), 500):
                    chunk = records[i : i + 500]
                    repo.create_many(chunk)

            total += len(records)
            logger.info(
                "backfill_cboe_type_complete",
                type=ratio_type,
                count=len(records),
            )

        except Exception as e:
            logger.error(
                "cboe_backfill_failed",
                type=ratio_type,
                error=str(e),
            )

    logger.info("backfill_cboe_complete", total=total)
    return total


# ============================================================
# AAII Sentiment Survey Backfill
# ============================================================


def _backfill_aaii(repo: SentimentRepository) -> int:
    """Backfill AAII Investor Sentiment Survey full history.

    Returns:
        Number of records inserted.
    """
    logger.info("backfill_aaii_start")

    try:
        resp = requests.get(
            "https://www.aaii.com/files/surveys/sentiment.xls",
            timeout=30,
            headers=_HEADERS,
        )
        resp.raise_for_status()

        df = pd.read_excel(BytesIO(resp.content), sheet_name=0, engine="xlrd")
        df.columns = [str(c).strip() for c in df.columns]
    except Exception as e:
        logger.error("aaii_backfill_fetch_failed", error=str(e))
        return 0

    # Find columns
    bullish_col = None
    bearish_col = None
    neutral_col = None

    for col in df.columns:
        cl = col.lower()
        if "bullish" in cl and "bear" not in cl:
            bullish_col = col
        elif "bearish" in cl:
            bearish_col = col
        elif "neutral" in cl:
            neutral_col = col

    if not bullish_col or not bearish_col:
        logger.error("aaii_columns_not_found", columns=list(df.columns))
        return 0

    df_clean = df.dropna(subset=[bullish_col])
    if df_clean.empty:
        return 0

    # Check existing
    latest = repo.get_latest(SentimentSource.AAII_SURVEY)
    latest_date = latest.date if latest else ""

    records: list[SentimentRecord] = []
    for idx in range(len(df_clean)):
        row = df_clean.iloc[idx]

        # First column is usually the date
        raw_date = row.iloc[0]
        try:
            if isinstance(raw_date, datetime):
                date_str = raw_date.strftime("%Y-%m-%d")
            elif isinstance(raw_date, str):
                date_str = pd.to_datetime(raw_date).strftime("%Y-%m-%d")
            else:
                continue
        except Exception:
            continue

        if date_str <= latest_date:
            continue

        bullish = float(row[bullish_col])
        bearish = float(row[bearish_col])
        neutral_val = float(row[neutral_col]) if neutral_col else 1 - bullish - bearish

        # Convert from ratio to percentage if needed
        if bullish <= 1:
            bullish *= 100
            bearish *= 100
            neutral_val *= 100

        spread = bullish - bearish

        if spread >= 20:
            level = "Extreme Greed"
        elif spread >= 10:
            level = "Greed"
        elif spread >= -10:
            level = "Neutral"
        elif spread >= -20:
            level = "Fear"
        else:
            level = "Extreme Fear"

        # Score: map spread (-40 to +40) to 0-100
        score = max(0, min(100, 50 + spread * (50 / 40)))

        records.append(
            SentimentRecord(
                date=date_str,
                source=SentimentSource.AAII_SURVEY,
                score=round(score, 1),
                level=level,
                components={
                    "bullish": round(bullish, 1),
                    "bearish": round(bearish, 1),
                    "neutral": round(neutral_val, 1),
                    "bull_bear_spread": round(spread, 1),
                },
            )
        )

    if records:
        for i in range(0, len(records), 500):
            chunk = records[i : i + 500]
            repo.create_many(chunk)

    logger.info("backfill_aaii_complete", count=len(records))
    return len(records)


# ============================================================
# Main
# ============================================================


def main() -> None:
    """Run sentiment data backfill."""
    parser = argparse.ArgumentParser(description="Backfill historical sentiment data")
    parser.add_argument(
        "--source",
        choices=["cnn", "cboe", "aaii", "all"],
        default="all",
        help="Which source to backfill (default: all)",
    )
    args = parser.parse_args()

    init_db()
    repo = SentimentRepository()

    results: dict[str, int] = {}

    if args.source in ("cnn", "all"):
        results["cnn_fear_greed"] = _backfill_cnn_fear_greed(repo)

    if args.source in ("cboe", "all"):
        results["cboe_putcall"] = _backfill_cboe_putcall(repo)

    if args.source in ("aaii", "all"):
        results["aaii_survey"] = _backfill_aaii(repo)

    logger.info("backfill_complete", results=results)
    total = sum(results.values())
    print(f"\n백필 완료: 총 {total:,}건 삽입")
    for source, count in results.items():
        print(f"  - {source}: {count:,}건")


if __name__ == "__main__":
    main()
