"""Korea market data collector using pykrx."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from src.collectors.market.base import BaseMarketCollector
from src.core.exceptions import CollectionError
from src.core.models import Market, MarketSentiment, MarketSnapshot


def _get_pykrx() -> Any:
    """Lazy-import pykrx.stock to defer heavy dependency."""
    try:
        from pykrx import stock
        return stock
    except ImportError as e:
        raise CollectionError(
            "pykrx is not installed. Run: pip install pykrx",
            {"error": str(e)},
        ) from e


class KoreaMarketCollector(BaseMarketCollector):
    """Collect Korean market data (KOSPI/KOSDAQ) using pykrx.

    pykrx uses ``YYYYMMDD`` date format for all API calls.
    """

    market = Market.KOREA

    def collect_indices(self) -> list[MarketSnapshot]:
        """Collect KOSPI and KOSDAQ index data.

        Returns:
            List of MarketSnapshot for each configured Korean index.
        """
        korea_config = self._config.market.korea
        today = datetime.now()
        today_str = today.strftime("%Y%m%d")
        date_display = today.strftime("%Y-%m-%d")

        # Look back a few days to handle weekends/holidays
        start_str = (today - timedelta(days=7)).strftime("%Y%m%d")

        snapshots: list[MarketSnapshot] = []
        for index_info in korea_config.indices:
            try:
                snapshot = self._collect_single_index(
                    code=index_info.code,
                    name=index_info.name,
                    start=start_str,
                    end=today_str,
                    date_display=date_display,
                )
                if snapshot:
                    snapshots.append(snapshot)
            except Exception as e:
                self._logger.warning(
                    "index_collection_failed",
                    index=index_info.name,
                    error=str(e),
                )
        self._logger.info("korea_indices_collected", count=len(snapshots))
        return snapshots

    def collect_stock_ohlcv(
        self,
        ticker: str,
        days: int = 120,
    ) -> pd.DataFrame:
        """Collect OHLCV data for a Korean stock.

        Args:
            ticker: Korean stock code (e.g., "005930").
            days: Number of calendar days of history.

        Returns:
            DataFrame with [Open, High, Low, Close, Volume] columns.
            Returns empty DataFrame on failure or non-trading days.
        """
        pykrx_stock = _get_pykrx()
        today = datetime.now()
        start = today - timedelta(days=days)
        start_str = start.strftime("%Y%m%d")
        end_str = today.strftime("%Y%m%d")

        try:
            df = pykrx_stock.get_market_ohlcv(start_str, end_str, ticker)
            if df.empty:
                self._logger.debug("empty_ohlcv", ticker=ticker)
                return pd.DataFrame()

            # Normalize column names to English
            column_map = {
                "시가": "Open",
                "고가": "High",
                "저가": "Low",
                "종가": "Close",
                "거래량": "Volume",
            }
            df = df.rename(columns=column_map)
            standard_cols = ["Open", "High", "Low", "Close", "Volume"]
            available = [c for c in standard_cols if c in df.columns]
            df = df[available]
            self._logger.debug("ohlcv_collected", ticker=ticker, rows=len(df))
            return df
        except Exception as e:
            self._logger.warning(
                "ohlcv_collection_failed",
                ticker=ticker,
                error=str(e),
            )
            return pd.DataFrame()

    def collect_watchlist_ohlcv(
        self,
        days: int = 120,
    ) -> dict[str, pd.DataFrame]:
        """Collect OHLCV data for all Korean watchlist stocks.

        Args:
            days: Number of calendar days of history.

        Returns:
            Dict mapping ticker -> OHLCV DataFrame.
        """
        watchlist = self._config.market.korea.watchlist
        result: dict[str, pd.DataFrame] = {}
        for item in watchlist:
            df = self.collect_stock_ohlcv(item.ticker, days)
            if not df.empty:
                result[item.ticker] = df
        self._logger.info(
            "watchlist_ohlcv_collected",
            market="korea",
            count=len(result),
        )
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _collect_single_index(
        self,
        code: str,
        name: str,
        start: str,
        end: str,
        date_display: str,
    ) -> MarketSnapshot | None:
        """Collect data for a single Korean market index.

        Args:
            code: pykrx index code (e.g., "1001" for KOSPI).
            name: Display name.
            start: Start date YYYYMMDD.
            end: End date YYYYMMDD.
            date_display: Display date YYYY-MM-DD.

        Returns:
            MarketSnapshot or None on failure.
        """
        pykrx_stock = _get_pykrx()
        df = pykrx_stock.get_index_ohlcv(start, end, code)
        if df.empty:
            self._logger.debug("empty_index_data", index=name)
            return None

        # Use the most recent available row
        latest = df.iloc[-1]
        close_col = "종가" if "종가" in df.columns else "Close"
        volume_col = "거래량" if "거래량" in df.columns else "Volume"

        index_value = float(latest.get(close_col, 0))
        volume = int(latest.get(volume_col, 0))

        # Compute change percent from previous row if available
        change_percent = 0.0
        if len(df) >= 2:
            prev_close = float(df.iloc[-2].get(close_col, 0))
            if prev_close > 0:
                change_percent = round(
                    (index_value - prev_close) / prev_close * 100, 2,
                )

        sentiment = self._classify_sentiment(change_percent)
        actual_date = str(df.index[-1].date()) if hasattr(df.index[-1], "date") else date_display

        return MarketSnapshot(
            date=actual_date,
            market=Market.KOREA,
            index_name=name,
            index_value=index_value,
            change_percent=change_percent,
            volume=volume,
            sentiment=sentiment,
        )

    @staticmethod
    def _classify_sentiment(change_pct: float) -> MarketSentiment:
        """Classify market sentiment from daily change percent.

        Args:
            change_pct: Daily percentage change.

        Returns:
            MarketSentiment enum value.
        """
        if change_pct >= 2.0:
            return MarketSentiment.VERY_BULLISH
        if change_pct >= 0.5:
            return MarketSentiment.BULLISH
        if change_pct <= -2.0:
            return MarketSentiment.VERY_BEARISH
        if change_pct <= -0.5:
            return MarketSentiment.BEARISH
        return MarketSentiment.NEUTRAL
