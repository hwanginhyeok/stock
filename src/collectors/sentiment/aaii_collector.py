"""AAII Investor Sentiment Survey collector."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors.sentiment.base import BaseSentimentCollector

# AAII publishes weekly sentiment data as an Excel file
_AAII_XLS_URL = "https://www.aaii.com/files/surveys/sentiment.xls"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def _classify_bull_bear_spread(spread: float) -> str:
    """Classify market mood from bull-bear spread.

    Args:
        spread: Bullish% - Bearish% (can be negative).

    Returns:
        Sentiment level string.
    """
    if spread >= 20:
        return "Extreme Greed"
    if spread >= 10:
        return "Greed"
    if spread >= -10:
        return "Neutral"
    if spread >= -20:
        return "Fear"
    return "Extreme Fear"


class AAIISentimentCollector(BaseSentimentCollector):
    """Collect AAII Investor Sentiment Survey data.

    The AAII survey is published weekly (Thursdays) and measures
    individual investor sentiment on the 6-month stock market outlook.
    Data available since 1987.
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch_data(self) -> pd.DataFrame:
        """Download and parse the AAII sentiment Excel file.

        Returns:
            DataFrame with Date, Bullish, Neutral, Bearish,
            and Bull-Bear Spread columns.

        Raises:
            requests.RequestException: On download failure.
            ValueError: On parse failure.
        """
        resp = requests.get(_AAII_XLS_URL, timeout=30, headers=_HEADERS)
        resp.raise_for_status()

        df = pd.read_excel(
            BytesIO(resp.content),
            sheet_name=0,
            engine="xlrd",
        )

        # Normalize column names (AAII format may vary)
        df.columns = [str(c).strip() for c in df.columns]

        return df

    def collect(self) -> list[dict[str, Any]]:
        """Collect latest AAII sentiment data.

        Returns:
            Single-element list with latest survey results, or empty
            list on failure.
        """
        try:
            df = self._fetch_data()
        except Exception as e:
            self._logger.error(
                "aaii_fetch_failed",
                error=str(e),
            )
            return []

        if df.empty:
            self._logger.warning("aaii_data_empty")
            return []

        # Find the relevant columns
        bullish_col = None
        bearish_col = None
        neutral_col = None
        spread_col = None

        for col in df.columns:
            col_lower = col.lower()
            if "bullish" in col_lower and "bear" not in col_lower:
                bullish_col = col
            elif "bearish" in col_lower:
                bearish_col = col
            elif "neutral" in col_lower:
                neutral_col = col
            elif "spread" in col_lower or "bull-bear" in col_lower:
                spread_col = col

        if not bullish_col or not bearish_col:
            self._logger.warning(
                "aaii_columns_not_found",
                columns=list(df.columns),
            )
            return []

        # Get latest row (skip NaN rows at bottom)
        df_clean = df.dropna(subset=[bullish_col])
        if df_clean.empty:
            return []

        latest = df_clean.iloc[-1]
        bullish = float(latest[bullish_col]) * 100 if float(latest[bullish_col]) <= 1 else float(latest[bullish_col])
        bearish = float(latest[bearish_col]) * 100 if float(latest[bearish_col]) <= 1 else float(latest[bearish_col])
        neutral_val = float(latest[neutral_col]) * 100 if neutral_col and float(latest[neutral_col]) <= 1 else (float(latest[neutral_col]) if neutral_col else 100 - bullish - bearish)

        if spread_col:
            spread = float(latest[spread_col]) * 100 if float(latest[spread_col]) <= 1 else float(latest[spread_col])
        else:
            spread = bullish - bearish

        # Historical averages (last 8 weeks)
        recent = df_clean.tail(8)
        avg_bullish = float(recent[bullish_col].mean())
        avg_bearish = float(recent[bearish_col].mean())
        if avg_bullish <= 1:
            avg_bullish *= 100
            avg_bearish *= 100

        result = {
            "date": str(latest.iloc[0]) if not pd.isna(latest.iloc[0]) else "unknown",
            "bullish": round(bullish, 1),
            "neutral": round(neutral_val, 1),
            "bearish": round(bearish, 1),
            "bull_bear_spread": round(spread, 1),
            "sentiment": _classify_bull_bear_spread(spread),
            "avg_bullish_8w": round(avg_bullish, 1),
            "avg_bearish_8w": round(avg_bearish, 1),
        }

        self._logger.info(
            "aaii_collected",
            bullish=result["bullish"],
            bearish=result["bearish"],
            spread=result["bull_bear_spread"],
            sentiment=result["sentiment"],
        )

        return [result]
