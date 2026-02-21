"""Abstract base class for market data collectors."""

from __future__ import annotations

from abc import abstractmethod

import pandas as pd

from src.collectors.base import BaseCollector
from src.core.models import Market, MarketSnapshot


class BaseMarketCollector(BaseCollector):
    """Base class for market data collectors.

    Each subclass targets a specific market and must implement methods
    for collecting index snapshots and OHLCV data.
    """

    market: Market

    @abstractmethod
    def collect_indices(self) -> list[MarketSnapshot]:
        """Collect current index data for the market.

        Returns:
            List of MarketSnapshot for each tracked index.
        """

    @abstractmethod
    def collect_stock_ohlcv(
        self,
        ticker: str,
        days: int = 120,
    ) -> pd.DataFrame:
        """Collect OHLCV data for a single stock.

        Args:
            ticker: Stock ticker symbol.
            days: Number of trading days of history.

        Returns:
            DataFrame with columns [Open, High, Low, Close, Volume]
            and DatetimeIndex.
        """

    @abstractmethod
    def collect_watchlist_ohlcv(
        self,
        days: int = 120,
    ) -> dict[str, pd.DataFrame]:
        """Collect OHLCV data for all watchlist stocks.

        Args:
            days: Number of trading days of history.

        Returns:
            Dict mapping ticker -> OHLCV DataFrame.
        """

    def collect(self) -> list[MarketSnapshot]:
        """Collect index snapshots (alias for collect_indices).

        Returns:
            List of MarketSnapshot.
        """
        return self.collect_indices()

    def collect_and_store(self) -> list[MarketSnapshot]:
        """Collect index snapshots and persist to DB.

        Returns:
            List of persisted MarketSnapshot.
        """
        from src.storage import MarketSnapshotRepository

        snapshots = self.collect_indices()
        if not snapshots:
            self._logger.info("no_snapshots_to_store")
            return []
        repo = MarketSnapshotRepository()
        stored = repo.create_many(snapshots)
        self._logger.info("snapshots_stored", count=len(stored))
        return stored
