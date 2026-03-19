"""Fetch index constituent tickers from Wikipedia and KRX."""

from __future__ import annotations

from io import StringIO

import pandas as pd
import requests

from src.core.logger import get_logger

logger = get_logger(__name__)

# KR preferred-stock suffixes to exclude (끝자리 5/7/8/9 → 우선주)
_KR_PREF_SUFFIXES = {"5", "7", "8", "9"}

_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
_NDX100_URL = "https://en.wikipedia.org/wiki/Nasdaq-100"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def _fetch_html(url: str) -> str:
    """Fetch HTML content from a URL with a browser-like User-Agent.

    Args:
        url: Target URL.

    Returns:
        HTML string.
    """
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def _yfinance_ticker(symbol: str) -> str:
    """Convert a ticker symbol to yfinance-compatible format.

    Args:
        symbol: Raw ticker symbol (e.g., "BRK.B").

    Returns:
        yfinance-compatible ticker (e.g., "BRK-B").
    """
    return symbol.strip().replace(".", "-")


def fetch_sp500_tickers() -> list[str]:
    """Fetch S&P 500 constituent tickers from Wikipedia.

    Returns:
        Sorted list of yfinance-compatible ticker symbols.
    """
    try:
        html = _fetch_html(_SP500_URL)
        tables = pd.read_html(StringIO(html), header=0)
        df = tables[0]
        tickers = df["Symbol"].dropna().astype(str).tolist()
        result = sorted({_yfinance_ticker(t) for t in tickers})
        logger.info("sp500_tickers_fetched", count=len(result))
        return result
    except Exception as e:
        logger.error("sp500_fetch_failed", error=str(e))
        return []


def fetch_ndx100_tickers() -> list[str]:
    """Fetch NASDAQ 100 constituent tickers from Wikipedia.

    Returns:
        Sorted list of yfinance-compatible ticker symbols.
    """
    try:
        html = _fetch_html(_NDX100_URL)
        tables = pd.read_html(StringIO(html), header=0)
        df = None
        for table in tables:
            if "Ticker" in table.columns:
                df = table
                break
        if df is None:
            logger.error("ndx100_table_not_found")
            return []
        tickers = df["Ticker"].dropna().astype(str).tolist()
        result = sorted({_yfinance_ticker(t) for t in tickers})
        logger.info("ndx100_tickers_fetched", count=len(result))
        return result
    except Exception as e:
        logger.error("ndx100_fetch_failed", error=str(e))
        return []


def get_combined_universe() -> list[str]:
    """Get the combined S&P 500 + NASDAQ 100 universe (deduplicated).

    Returns:
        Sorted list of unique yfinance-compatible tickers.
    """
    sp500 = set(fetch_sp500_tickers())
    ndx100 = set(fetch_ndx100_tickers())
    combined = sorted(sp500 | ndx100)
    logger.info(
        "combined_universe",
        sp500=len(sp500),
        ndx100=len(ndx100),
        total=len(combined),
    )
    return combined


def fetch_kr_top_tickers(
    n: int = 200,
    *,
    exclude_preferred: bool = True,
) -> list[tuple[str, str, int]]:
    """Fetch KOSPI + KOSDAQ top-N tickers by market capitalization.

    Uses FinanceDataReader to list all stocks from both exchanges,
    merges them, sorts by Marcap descending, and returns top N.

    Args:
        n: Number of top tickers to return.
        exclude_preferred: If True, exclude preferred stocks
            (codes ending in 5/7/8/9).

    Returns:
        List of (code, name, marcap) tuples sorted by market cap desc.
        Returns empty list on failure.
    """
    try:
        import FinanceDataReader as fdr

        frames = []
        for market in ("KOSPI", "KOSDAQ"):
            df = fdr.StockListing(market)
            if df is not None and not df.empty:
                frames.append(df)

        if not frames:
            logger.error("kr_listing_empty")
            return []

        combined = pd.concat(frames, ignore_index=True)

        # Ensure required columns exist
        if "Code" not in combined.columns or "Marcap" not in combined.columns:
            logger.error(
                "kr_listing_missing_columns",
                columns=list(combined.columns),
            )
            return []

        # Filter preferred stocks
        if exclude_preferred:
            combined = combined[
                ~combined["Code"].str[-1].isin(_KR_PREF_SUFFIXES)
            ]

        # Drop rows with missing Marcap and sort
        combined = combined.dropna(subset=["Marcap"])
        combined = combined.sort_values("Marcap", ascending=False)
        top = combined.head(n)

        result = [
            (str(row["Code"]), str(row["Name"]), int(row["Marcap"]))
            for _, row in top.iterrows()
        ]
        logger.info("kr_top_tickers_fetched", count=len(result))
        return result

    except Exception as e:
        logger.error("kr_top_tickers_failed", error=str(e))
        return []
