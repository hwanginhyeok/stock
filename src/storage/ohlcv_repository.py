"""Repository for historical OHLCV price records."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import select

from src.core.database import OHLCVDB, get_session
from src.core.models import OHLCVRecord
from src.storage.base import BaseRepository


class OHLCVRepository(BaseRepository[OHLCVRecord]):
    """CRUD repository for OHLCVRecord (daily price history).

    Stores Open/High/Low/Close/Volume data for stocks and indices.
    """

    def get_by_ticker(
        self,
        ticker: str,
        limit: int = 2520,
    ) -> list[OHLCVRecord]:
        """Get price history for a ticker.

        Args:
            ticker: Stock ticker or index symbol.
            limit: Max records (default ~10 years).

        Returns:
            List of OHLCVRecord ordered by date descending.
        """
        return self.get_many(
            filters={"ticker": ticker},
            order_by="date",
            descending=True,
            limit=limit,
        )

    def get_by_ticker_range(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
    ) -> list[OHLCVRecord]:
        """Get price data for a ticker within a date range.

        Args:
            ticker: Stock ticker or index symbol.
            start_date: Start date (YYYY-MM-DD).
            end_date: End date (YYYY-MM-DD).

        Returns:
            List of OHLCVRecord ordered by date ascending.
        """
        with get_session() as session:
            stmt = (
                select(OHLCVDB)
                .where(OHLCVDB.ticker == ticker)
                .where(OHLCVDB.date >= start_date)
                .where(OHLCVDB.date <= end_date)
                .order_by(OHLCVDB.date.asc())
            )
            results = session.execute(stmt).scalars().all()
            return [self._orm_to_pydantic(obj) for obj in results]

    def get_latest(self, ticker: str) -> OHLCVRecord | None:
        """Get the most recent OHLCV record for a ticker.

        Args:
            ticker: Stock ticker or index symbol.

        Returns:
            Latest OHLCVRecord or None.
        """
        records = self.get_many(
            filters={"ticker": ticker},
            order_by="date",
            descending=True,
            limit=1,
        )
        return records[0] if records else None

    def to_dataframe(
        self,
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """Get price data as a pandas DataFrame.

        Args:
            ticker: Stock ticker or index symbol.
            start_date: Optional start date filter.
            end_date: Optional end date filter.

        Returns:
            DataFrame with columns [date, open, high, low, close, volume]
            indexed by date.
        """
        if start_date and end_date:
            records = self.get_by_ticker_range(ticker, start_date, end_date)
        else:
            records = self.get_by_ticker(ticker)
            records.reverse()  # ascending order

        if not records:
            return pd.DataFrame(
                columns=["open", "high", "low", "close", "volume", "adjusted_close"],
            )

        data = [
            {
                "date": r.date,
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
                "adjusted_close": r.adjusted_close,
            }
            for r in records
        ]
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        return df
