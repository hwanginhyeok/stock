"""Historical price data loader — fetches and stores OHLCV data."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd

from src.core.config import get_config
from src.core.logger import get_logger
from src.core.models import Market, OHLCVRecord
from src.storage.ohlcv_repository import OHLCVRepository

logger = get_logger("price_loader")


class PriceLoader:
    """Fetches historical OHLCV data and stores it in the database.

    Supports US stocks via yfinance and Korean stocks via pykrx.

    Example::

        loader = PriceLoader()
        count = loader.fetch_and_store("AAPL", market=Market.US, years=10)
    """

    def __init__(self, repo: OHLCVRepository | None = None) -> None:
        self._repo = repo or OHLCVRepository()

    def fetch_and_store(
        self,
        ticker: str,
        *,
        market: Market = Market.US,
        years: int = 10,
    ) -> int:
        """Fetch historical prices and store in DB.

        Skips dates already in the database (idempotent).

        Args:
            ticker: Stock ticker or index symbol.
            market: Market enum (US or KOREA).
            years: Number of years of history.

        Returns:
            Number of new records inserted.
        """
        logger.info("fetch_start", ticker=ticker, market=market, years=years)

        # Get latest existing date to avoid duplicates
        latest = self._repo.get_latest(ticker)
        latest_date = latest.date if latest else ""

        if market == Market.US:
            df = self._fetch_us(ticker, years)
        else:
            df = self._fetch_kr(ticker, years)

        if df.empty:
            logger.warning("fetch_empty", ticker=ticker)
            return 0

        records: list[OHLCVRecord] = []
        for idx in range(len(df)):
            row = df.iloc[idx]
            date_val = df.index[idx]
            date_str = (
                str(date_val.date())
                if hasattr(date_val, "date")
                else str(date_val)[:10]
            )

            if date_str <= latest_date:
                continue

            close_val = float(row.get("Close", 0))
            adj_close = float(row.get("Adj Close", close_val))

            records.append(
                OHLCVRecord(
                    date=date_str,
                    ticker=ticker,
                    market=market,
                    open=float(row.get("Open", 0)),
                    high=float(row.get("High", 0)),
                    low=float(row.get("Low", 0)),
                    close=close_val,
                    volume=int(row.get("Volume", 0)),
                    adjusted_close=adj_close,
                )
            )

        if records:
            for i in range(0, len(records), 500):
                chunk = records[i : i + 500]
                self._repo.create_many(chunk)

        logger.info("fetch_complete", ticker=ticker, count=len(records))
        return len(records)

    def fetch_all_watchlist(self, *, years: int = 10) -> dict[str, int]:
        """Fetch historical prices for all configured watchlist stocks and indices.

        Args:
            years: Number of years of history.

        Returns:
            Dict mapping ticker to number of records inserted.
        """
        config = get_config()
        results: dict[str, int] = {}

        # US indices
        for idx_cfg in config.market.us.indices:
            ticker = idx_cfg.get("ticker", "")
            if ticker:
                results[ticker] = self.fetch_and_store(
                    ticker, market=Market.US, years=years,
                )

        # US watchlist
        for stock in config.market.us.watchlist:
            ticker = stock.get("ticker", "")
            if ticker:
                results[ticker] = self.fetch_and_store(
                    ticker, market=Market.US, years=years,
                )

        # KR indices — use yfinance tickers for Korean indices
        kr_index_map = {"KOSPI": "^KS11", "KOSDAQ": "^KQ11"}
        for idx_cfg in config.market.korea.indices:
            name = idx_cfg.get("name", "")
            yf_ticker = kr_index_map.get(name, "")
            if yf_ticker:
                results[yf_ticker] = self.fetch_and_store(
                    yf_ticker, market=Market.KOREA, years=years,
                )

        # KR watchlist
        for stock in config.market.korea.watchlist:
            code = stock.get("code", "")
            if code:
                results[code] = self.fetch_and_store(
                    code, market=Market.KOREA, years=years,
                )

        return results

    def _fetch_us(self, ticker: str, years: int) -> pd.DataFrame:
        """Fetch US market OHLCV via yfinance.

        Args:
            ticker: US ticker symbol (e.g., "AAPL", "^GSPC").
            years: Number of years.

        Returns:
            DataFrame with OHLCV columns.
        """
        try:
            import yfinance as yf

            period = f"{years}y" if years <= 10 else "max"
            data = yf.Ticker(ticker).history(period=period, auto_adjust=False)
            if data.empty:
                return pd.DataFrame()

            # Normalize column names
            data.columns = [str(c).strip() for c in data.columns]
            return data
        except Exception as e:
            logger.error("yfinance_fetch_failed", ticker=ticker, error=str(e))
            return pd.DataFrame()

    def _fetch_kr(self, ticker: str, years: int) -> pd.DataFrame:
        """Fetch Korean market OHLCV via pykrx.

        Args:
            ticker: Korean stock code (e.g., "005930") or yfinance index.
            years: Number of years.

        Returns:
            DataFrame with OHLCV columns.
        """
        # If it's a yfinance-style ticker (^KS11), use yfinance
        if ticker.startswith("^"):
            return self._fetch_us(ticker, years)

        try:
            from pykrx import stock

            end_date = datetime.now(tz=timezone.utc).strftime("%Y%m%d")
            start_date = (
                datetime.now(tz=timezone.utc) - timedelta(days=365 * years)
            ).strftime("%Y%m%d")

            df = stock.get_market_ohlcv(start_date, end_date, ticker)
            if df.empty:
                return pd.DataFrame()

            # Normalize Korean column names
            col_map = {
                "시가": "Open",
                "고가": "High",
                "저가": "Low",
                "종가": "Close",
                "거래량": "Volume",
            }
            df = df.rename(columns=col_map)
            df["Adj Close"] = df["Close"]
            return df[["Open", "High", "Low", "Close", "Volume", "Adj Close"]]
        except Exception as e:
            logger.error("pykrx_fetch_failed", ticker=ticker, error=str(e))
            return pd.DataFrame()
