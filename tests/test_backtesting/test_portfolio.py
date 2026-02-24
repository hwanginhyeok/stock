"""Tests for Portfolio and Position management."""

from __future__ import annotations

import pytest

from src.backtesting.engine.order import Order, OrderSide
from src.backtesting.engine.portfolio import Portfolio


class TestPortfolio:
    """Tests for Portfolio class."""

    def test_initial_state(self) -> None:
        portfolio = Portfolio(initial_capital=1_000_000)
        assert portfolio.cash == 1_000_000
        assert portfolio.position_count() == 0
        assert portfolio.completed_trades == []

    def test_buy_order(self) -> None:
        portfolio = Portfolio(initial_capital=1_000_000, commission_rate=0.001)
        order = Order(
            date="2024-01-01",
            ticker="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            price=150.0,
        )
        result = portfolio.execute_order(order)
        assert result is True
        assert portfolio.has_position("AAPL")
        assert portfolio.positions["AAPL"].quantity == 10
        assert portfolio.cash < 1_000_000  # spent money

    def test_buy_insufficient_cash(self) -> None:
        portfolio = Portfolio(initial_capital=100)
        order = Order(
            date="2024-01-01",
            ticker="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            price=150.0,
        )
        result = portfolio.execute_order(order)
        assert result is False
        assert not portfolio.has_position("AAPL")

    def test_sell_order(self) -> None:
        portfolio = Portfolio(initial_capital=1_000_000, commission_rate=0)
        # Buy first
        buy = Order(
            date="2024-01-01",
            ticker="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
        )
        portfolio.execute_order(buy)
        cash_after_buy = portfolio.cash

        # Sell at higher price
        sell = Order(
            date="2024-02-01",
            ticker="AAPL",
            side=OrderSide.SELL,
            quantity=10,
            price=120.0,
        )
        result = portfolio.execute_order(sell)
        assert result is True
        assert not portfolio.has_position("AAPL")
        assert len(portfolio.completed_trades) == 1
        trade = portfolio.completed_trades[0]
        assert trade.pnl == 200.0  # (120-100) * 10
        assert trade.return_pct == 20.0

    def test_sell_nonexistent_position(self) -> None:
        portfolio = Portfolio(initial_capital=1_000_000)
        sell = Order(
            date="2024-01-01",
            ticker="AAPL",
            side=OrderSide.SELL,
            quantity=10,
            price=150.0,
        )
        result = portfolio.execute_order(sell)
        assert result is False

    def test_total_value(self) -> None:
        portfolio = Portfolio(initial_capital=1_000_000, commission_rate=0)
        buy = Order(
            date="2024-01-01",
            ticker="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
        )
        portfolio.execute_order(buy)

        total = portfolio.total_value({"AAPL": 120.0})
        # cash (1_000_000 - 1_000) + position (10 * 120)
        assert total == 1_000_000 - 1_000 + 1_200

    def test_commission_applied(self) -> None:
        portfolio = Portfolio(initial_capital=1_000_000, commission_rate=0.01)
        buy = Order(
            date="2024-01-01",
            ticker="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            price=100.0,
        )
        portfolio.execute_order(buy)
        # Cost: 100*100 + 100*100*0.01 = 10000 + 100 = 10100
        assert portfolio.cash == pytest.approx(1_000_000 - 10_100, rel=1e-2)

    def test_add_to_existing_position(self) -> None:
        portfolio = Portfolio(initial_capital=1_000_000, commission_rate=0)
        buy1 = Order(
            date="2024-01-01",
            ticker="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
        )
        buy2 = Order(
            date="2024-01-02",
            ticker="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            price=120.0,
        )
        portfolio.execute_order(buy1)
        portfolio.execute_order(buy2)
        assert portfolio.positions["AAPL"].quantity == 20

    def test_partial_sell(self) -> None:
        portfolio = Portfolio(initial_capital=1_000_000, commission_rate=0)
        buy = Order(
            date="2024-01-01",
            ticker="AAPL",
            side=OrderSide.BUY,
            quantity=20,
            price=100.0,
        )
        portfolio.execute_order(buy)

        sell = Order(
            date="2024-02-01",
            ticker="AAPL",
            side=OrderSide.SELL,
            quantity=10,
            price=120.0,
        )
        portfolio.execute_order(sell)
        assert portfolio.has_position("AAPL")
        assert portfolio.positions["AAPL"].quantity == 10
