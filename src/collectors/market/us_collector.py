"""US market data collector using yfinance."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import yfinance as yf

from src.collectors.market.base import BaseMarketCollector
from src.core.models import Market, MarketSentiment, MarketSnapshot


class USMarketCollector(BaseMarketCollector):
    """Collect US market data (S&P 500, NASDAQ, DOW, VIX) using yfinance."""

    market = Market.US

    def collect_indices(self) -> list[MarketSnapshot]:
        """Collect US market index data.

        Returns:
            List of MarketSnapshot for each configured US index.
        """
        us_config = self._config.market.us
        date_display = datetime.now().strftime("%Y-%m-%d")

        snapshots: list[MarketSnapshot] = []
        for index_info in us_config.indices:
            try:
                snapshot = self._collect_single_index(
                    ticker=index_info.ticker,
                    name=index_info.name,
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
        self._logger.info("us_indices_collected", count=len(snapshots))
        return snapshots

    def collect_stock_ohlcv(
        self,
        ticker: str,
        days: int = 120,
    ) -> pd.DataFrame:
        """Collect OHLCV data for a US stock.

        Args:
            ticker: US stock ticker (e.g., "AAPL").
            days: Number of calendar days of history.

        Returns:
            DataFrame with [Open, High, Low, Close, Volume] columns.
        """
        try:
            period = self._days_to_period(days)
            yf_ticker = yf.Ticker(ticker)
            df = yf_ticker.history(period=period)
            if df.empty:
                self._logger.debug("empty_ohlcv", ticker=ticker)
                return pd.DataFrame()

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
        """Collect OHLCV data for all US watchlist stocks.

        Args:
            days: Number of calendar days of history.

        Returns:
            Dict mapping ticker -> OHLCV DataFrame.
        """
        watchlist = self._config.market.us.watchlist
        result: dict[str, pd.DataFrame] = {}
        for item in watchlist:
            df = self.collect_stock_ohlcv(item.ticker, days)
            if not df.empty:
                result[item.ticker] = df
        self._logger.info(
            "watchlist_ohlcv_collected",
            market="us",
            count=len(result),
        )
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _collect_single_index(
        self,
        ticker: str,
        name: str,
        date_display: str,
    ) -> MarketSnapshot | None:
        """Collect data for a single US index.

        Args:
            ticker: yfinance ticker symbol (e.g., "^GSPC").
            name: Display name.
            date_display: Display date YYYY-MM-DD.

        Returns:
            MarketSnapshot or None on failure.
        """
        yf_ticker = yf.Ticker(ticker)
        hist = yf_ticker.history(period="5d")
        if hist.empty:
            self._logger.debug("empty_index_data", index=name)
            return None

        latest = hist.iloc[-1]
        index_value = float(latest.get("Close", 0))
        volume = int(latest.get("Volume", 0))

        change_percent = 0.0
        if len(hist) >= 2:
            prev_close = float(hist.iloc[-2].get("Close", 0))
            if prev_close > 0:
                change_percent = round(
                    (index_value - prev_close) / prev_close * 100, 2,
                )

        # VIX uses its own sentiment classification
        is_vix = ticker == "^VIX"
        sentiment = (
            self._classify_vix_sentiment(index_value)
            if is_vix
            else self._classify_sentiment(change_percent)
        )

        actual_date = (
            str(hist.index[-1].date())
            if hasattr(hist.index[-1], "date")
            else date_display
        )

        extra_data = {}
        if is_vix:
            extra_data["vix_level"] = index_value

        return MarketSnapshot(
            date=actual_date,
            market=Market.US,
            index_name=name,
            index_value=index_value,
            change_percent=change_percent,
            volume=volume,
            sentiment=sentiment,
            extra_data=extra_data,
        )

    @staticmethod
    def _classify_sentiment(change_pct: float) -> MarketSentiment:
        """Classify market sentiment from daily change percent.

        Args:
            change_pct: Daily percentage change.

        Returns:
            MarketSentiment enum value.
        """
        if change_pct >= 1.5:
            return MarketSentiment.VERY_BULLISH
        if change_pct >= 0.3:
            return MarketSentiment.BULLISH
        if change_pct <= -1.5:
            return MarketSentiment.VERY_BEARISH
        if change_pct <= -0.3:
            return MarketSentiment.BEARISH
        return MarketSentiment.NEUTRAL

    @staticmethod
    def _classify_vix_sentiment(vix_value: float) -> MarketSentiment:
        """Classify sentiment based on VIX level.

        Args:
            vix_value: Current VIX index value.

        Returns:
            MarketSentiment (inverted — high VIX = bearish).
        """
        if vix_value >= 30:
            return MarketSentiment.VERY_BEARISH
        if vix_value >= 20:
            return MarketSentiment.BEARISH
        if vix_value <= 12:
            return MarketSentiment.VERY_BULLISH
        if vix_value <= 15:
            return MarketSentiment.BULLISH
        return MarketSentiment.NEUTRAL

    @staticmethod
    def _days_to_period(days: int) -> str:
        """Convert calendar days to a yfinance period string.

        Args:
            days: Number of calendar days.

        Returns:
            yfinance period string (e.g., "6mo", "1y").
        """
        if days <= 7:
            return "5d"
        if days <= 30:
            return "1mo"
        if days <= 90:
            return "3mo"
        if days <= 180:
            return "6mo"
        return "1y"
