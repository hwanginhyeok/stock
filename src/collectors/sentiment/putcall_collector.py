"""CBOE Put/Call Ratio collector."""

from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors.sentiment.base import BaseSentimentCollector

# CBOE published CSV endpoints
_CBOE_URLS = {
    "total": "https://www.cboe.com/publish/ScheduledTask/MktData/datahouse/totalpc.csv",
    "equity": "https://www.cboe.com/publish/ScheduledTask/MktData/datahouse/equitypc.csv",
    "index": "https://www.cboe.com/publish/ScheduledTask/MktData/datahouse/indexpc.csv",
}

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; StockRichBot/1.0)",
}


def _classify_putcall(ratio: float) -> str:
    """Classify put/call ratio into sentiment level.

    Args:
        ratio: Put/Call ratio value.

    Returns:
        Sentiment level string.

    Note:
        High P/C ratio (>1.0) = excessive put buying = Fear (contrarian bullish).
        Low P/C ratio (<0.7) = excessive call buying = Greed (contrarian bearish).
    """
    if ratio >= 1.2:
        return "Extreme Fear"
    if ratio >= 1.0:
        return "Fear"
    if ratio >= 0.7:
        return "Neutral"
    if ratio >= 0.5:
        return "Greed"
    return "Extreme Greed"


class PutCallRatioCollector(BaseSentimentCollector):
    """Collect CBOE Put/Call Ratio data from published CSV files.

    Fetches total, equity-only, and index put/call ratios.
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch_csv(self, url: str) -> pd.DataFrame:
        """Fetch and parse a CBOE put/call CSV.

        Args:
            url: CBOE CSV download URL.

        Returns:
            DataFrame with Date index and CALLS, PUTS, TOTAL, P/C Ratio columns.

        Raises:
            requests.RequestException: On network errors.
            ValueError: If CSV parsing fails.
        """
        resp = requests.get(url, timeout=15, headers=_HEADERS)
        resp.raise_for_status()

        df = pd.read_csv(
            StringIO(resp.text),
            header=2,
            index_col=0,
            parse_dates=True,
        )
        df = df.dropna(how="all")
        return df

    def collect(self) -> list[dict[str, Any]]:
        """Collect put/call ratio data for total, equity, and index.

        Returns:
            List of dicts with latest put/call ratio data per type.
        """
        results: list[dict[str, Any]] = []

        for ratio_type, url in _CBOE_URLS.items():
            try:
                df = self._fetch_csv(url)
                if df.empty:
                    self._logger.warning(
                        "empty_putcall_data",
                        type=ratio_type,
                    )
                    continue

                latest = df.iloc[-1]
                date_str = str(df.index[-1].date()) if hasattr(df.index[-1], "date") else str(df.index[-1])

                pc_ratio = float(latest.get("P/C Ratio", 0))

                # 5-day and 20-day moving averages for trend
                pc_col = "P/C Ratio"
                ma5 = float(df[pc_col].tail(5).mean()) if len(df) >= 5 else pc_ratio
                ma20 = float(df[pc_col].tail(20).mean()) if len(df) >= 20 else pc_ratio

                results.append({
                    "type": ratio_type,
                    "date": date_str,
                    "calls": int(latest.get("CALLS", 0)),
                    "puts": int(latest.get("PUTS", 0)),
                    "total": int(latest.get("TOTAL", 0)),
                    "pc_ratio": round(pc_ratio, 4),
                    "pc_ratio_ma5": round(ma5, 4),
                    "pc_ratio_ma20": round(ma20, 4),
                    "sentiment": _classify_putcall(pc_ratio),
                })

                self._logger.info(
                    "putcall_collected",
                    type=ratio_type,
                    ratio=round(pc_ratio, 4),
                    sentiment=_classify_putcall(pc_ratio),
                )

            except Exception as e:
                self._logger.warning(
                    "putcall_collection_failed",
                    type=ratio_type,
                    error=str(e),
                )

        return results
