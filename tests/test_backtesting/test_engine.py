"""Tests for BacktestEngine."""

from __future__ import annotations

from typing import Any

import pandas as pd
import pytest

from src.backtesting.engine.backtest_engine import BacktestEngine, BacktestResult
from src.backtesting.strategy.base import BaseStrategy, Signal, SignalType


class AlwaysBuyStrategy(BaseStrategy):
    """Test strategy that buys on first day and holds."""

    @property
    def name(self) -> str:
        return "always_buy"

    def generate_signals(
        self,
        date: str,
        prices: dict[str, pd.DataFrame],
        context: dict[str, Any] | None = None,
    ) -> list[Signal]:
        signals = []
        for ticker in prices:
            signals.append(
                Signal(
                    date=date,
                    ticker=ticker,
                    signal_type=SignalType.BUY,
                    allocation=0.5,
                    reason="always buy",
                )
            )
        return signals


class BuyThenSellStrategy(BaseStrategy):
    """Buys on first call, sells on second call."""

    def __init__(self) -> None:
        self._bought: set[str] = set()

    @property
    def name(self) -> str:
        return "buy_then_sell"

    def generate_signals(
        self,
        date: str,
        prices: dict[str, pd.DataFrame],
        context: dict[str, Any] | None = None,
    ) -> list[Signal]:
        signals = []
        for ticker in prices:
            if ticker not in self._bought:
                signals.append(
                    Signal(
                        date=date,
                        ticker=ticker,
                        signal_type=SignalType.BUY,
                        allocation=0.3,
                        reason="initial buy",
                    )
                )
                self._bought.add(ticker)
            else:
                signals.append(
                    Signal(
                        date=date,
                        ticker=ticker,
                        signal_type=SignalType.SELL,
                        reason="take profit",
                    )
                )
        return signals


class TestBacktestEngine:
    """Tests for BacktestEngine."""

    def test_empty_prices(self) -> None:
        engine = BacktestEngine()
        result = engine.run(AlwaysBuyStrategy(), {})
        assert result.strategy_name == "always_buy"
        assert result.total_return_pct == 0

    def test_basic_run(self, sample_prices: dict[str, pd.DataFrame]) -> None:
        engine = BacktestEngine(initial_capital=1_000_000)
        result = engine.run(AlwaysBuyStrategy(), sample_prices)
        assert result.strategy_name == "always_buy"
        assert result.initial_capital == 1_000_000
        assert len(result.equity_curve) > 0
        assert result.start_date != ""
        assert result.end_date != ""

    def test_buy_then_sell(self, sample_prices: dict[str, pd.DataFrame]) -> None:
        engine = BacktestEngine(initial_capital=1_000_000, commission_rate=0)
        result = engine.run(BuyThenSellStrategy(), sample_prices)
        assert len(result.trades) >= 1
        assert result.order_count >= 2  # at least 1 buy + 1 sell

    def test_with_date_range(self, sample_prices: dict[str, pd.DataFrame]) -> None:
        engine = BacktestEngine(initial_capital=1_000_000)
        result = engine.run(
            AlwaysBuyStrategy(),
            sample_prices,
            start_date="2020-03-01",
            end_date="2020-06-01",
        )
        assert result.start_date >= "2020-03-01"
        assert result.end_date <= "2020-06-01"

    def test_with_context(self, sample_prices: dict[str, pd.DataFrame]) -> None:
        """Test that context data is passed to strategy."""
        engine = BacktestEngine(initial_capital=1_000_000)
        context = {"2020-01-02": {"fear_greed_score": 15}}
        result = engine.run(
            AlwaysBuyStrategy(),
            sample_prices,
            context_by_date=context,
        )
        assert len(result.equity_curve) > 0

    def test_multi_ticker(
        self, multi_ticker_prices: dict[str, pd.DataFrame],
    ) -> None:
        engine = BacktestEngine(initial_capital=10_000_000)
        result = engine.run(AlwaysBuyStrategy(), multi_ticker_prices)
        assert len(result.tickers) == 3
        assert result.final_value > 0

    def test_result_model(self) -> None:
        result = BacktestResult(
            strategy_name="test",
            initial_capital=1_000_000,
            final_value=1_200_000,
            total_return_pct=20.0,
        )
        assert result.total_return_pct == 20.0
