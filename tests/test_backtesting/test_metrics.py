"""Tests for performance metrics calculation."""

from __future__ import annotations

import pytest

from src.backtesting.engine.portfolio import Trade
from src.backtesting.metrics.performance import (
    PerformanceMetrics,
    _daily_returns,
    _max_drawdown,
    _sharpe_ratio,
    calculate_metrics,
)


class TestMaxDrawdown:
    """Tests for max drawdown calculation."""

    def test_no_drawdown(self) -> None:
        values = [100, 110, 120, 130]
        assert _max_drawdown(values) == 0.0

    def test_simple_drawdown(self) -> None:
        values = [100, 120, 90, 110]
        # Peak 120, trough 90 → dd = (120-90)/120 = 25%
        assert _max_drawdown(values) == pytest.approx(25.0)

    def test_empty(self) -> None:
        assert _max_drawdown([]) == 0.0

    def test_single_value(self) -> None:
        assert _max_drawdown([100]) == 0.0


class TestDailyReturns:
    """Tests for daily returns calculation."""

    def test_basic_returns(self) -> None:
        values = [100, 110, 105]
        returns = _daily_returns(values)
        assert len(returns) == 2
        assert returns[0] == pytest.approx(10.0)  # (110-100)/100 * 100
        assert returns[1] == pytest.approx(-4.545, rel=0.01)

    def test_empty(self) -> None:
        assert _daily_returns([]) == []
        assert _daily_returns([100]) == []


class TestSharpeRatio:
    """Tests for Sharpe ratio calculation."""

    def test_zero_returns(self) -> None:
        returns = [0.0, 0.0, 0.0]
        # With risk-free rate, excess returns are negative
        assert _sharpe_ratio(returns, 0.0) == 0.0

    def test_positive_returns(self) -> None:
        # Consistent positive returns should give positive Sharpe
        returns = [1.0, 0.5, 1.2, 0.8, 1.1] * 50
        sharpe = _sharpe_ratio(returns, 0.03)
        assert sharpe > 0

    def test_insufficient_data(self) -> None:
        assert _sharpe_ratio([], 0.03) == 0.0
        assert _sharpe_ratio([1.0], 0.03) == 0.0


class TestCalculateMetrics:
    """Tests for the main calculate_metrics function."""

    def test_empty_equity_curve(self) -> None:
        metrics = calculate_metrics({}, [], 1_000_000)
        assert metrics.total_return_pct == 0

    def test_profitable_run(self) -> None:
        equity = {
            "2024-01-01": 1_000_000,
            "2024-01-02": 1_010_000,
            "2024-01-03": 1_020_000,
            "2024-01-04": 1_015_000,
            "2024-01-05": 1_050_000,
        }
        trades = [
            Trade(
                ticker="AAPL",
                entry_date="2024-01-01",
                exit_date="2024-01-05",
                entry_price=100,
                exit_price=105,
                quantity=100,
                pnl=500,
                return_pct=5.0,
                holding_days=4,
            ),
        ]
        metrics = calculate_metrics(equity, trades, 1_000_000)
        assert metrics.total_return_pct == 5.0
        assert metrics.total_trades == 1
        assert metrics.winning_trades == 1
        assert metrics.win_rate_pct == 100.0

    def test_losing_trades(self) -> None:
        equity = {
            "2024-01-01": 1_000_000,
            "2024-01-02": 950_000,
        }
        trades = [
            Trade(
                ticker="AAPL",
                entry_date="2024-01-01",
                exit_date="2024-01-02",
                entry_price=100,
                exit_price=95,
                quantity=100,
                pnl=-500,
                return_pct=-5.0,
                holding_days=1,
            ),
        ]
        metrics = calculate_metrics(equity, trades, 1_000_000)
        assert metrics.total_return_pct == -5.0
        assert metrics.losing_trades == 1
        assert metrics.win_rate_pct == 0.0

    def test_mixed_trades(self) -> None:
        equity = {f"2024-01-{i:02d}": 1_000_000 + i * 1000 for i in range(1, 11)}
        trades = [
            Trade(
                ticker="A", entry_date="2024-01-01", exit_date="2024-01-03",
                entry_price=100, exit_price=110, quantity=10,
                pnl=100, return_pct=10.0, holding_days=2,
            ),
            Trade(
                ticker="B", entry_date="2024-01-04", exit_date="2024-01-06",
                entry_price=50, exit_price=45, quantity=20,
                pnl=-100, return_pct=-10.0, holding_days=2,
            ),
            Trade(
                ticker="C", entry_date="2024-01-07", exit_date="2024-01-09",
                entry_price=200, exit_price=220, quantity=5,
                pnl=100, return_pct=10.0, holding_days=2,
            ),
        ]
        metrics = calculate_metrics(equity, trades, 1_000_000)
        assert metrics.total_trades == 3
        assert metrics.winning_trades == 2
        assert metrics.losing_trades == 1
        assert metrics.win_rate_pct == pytest.approx(66.67, rel=0.01)
        assert metrics.max_consecutive_wins == 1  # win, lose, win
        assert metrics.max_consecutive_losses == 1
