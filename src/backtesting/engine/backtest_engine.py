"""Core backtesting simulation engine."""

from __future__ import annotations

from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from src.backtesting.engine.order import Order, OrderSide
from src.backtesting.engine.portfolio import Portfolio, Trade
from src.backtesting.strategy.base import BaseStrategy, SignalType
from src.core.logger import get_logger

logger = get_logger("backtest_engine")


class BacktestResult(BaseModel):
    """Complete results from a backtest run.

    Attributes:
        strategy_name: Name of the strategy tested.
        tickers: List of tickers tested.
        start_date: Backtest start date.
        end_date: Backtest end date.
        initial_capital: Starting capital.
        final_value: Final portfolio value.
        total_return_pct: Total return percentage.
        trades: List of completed trades.
        equity_curve: Daily portfolio values as {date: value}.
        order_count: Total number of orders executed.
    """

    strategy_name: str
    tickers: list[str] = Field(default_factory=list)
    start_date: str = ""
    end_date: str = ""
    initial_capital: float = 0.0
    final_value: float = 0.0
    total_return_pct: float = 0.0
    trades: list[Trade] = Field(default_factory=list)
    equity_curve: dict[str, float] = Field(default_factory=dict)
    order_count: int = 0


class BacktestEngine:
    """Simulates a trading strategy against historical price data.

    The engine iterates through each trading day, asks the strategy
    for signals, and executes orders through the portfolio manager.

    Args:
        initial_capital: Starting cash amount.
        commission_rate: Transaction cost fraction (default 0.1%).

    Example::

        engine = BacktestEngine(initial_capital=10_000_000)
        result = engine.run(
            strategy=SentimentContrarianStrategy(),
            prices={"AAPL": aapl_df, "MSFT": msft_df},
            start_date="2016-01-01",
            end_date="2026-01-01",
        )
    """

    def __init__(
        self,
        initial_capital: float = 10_000_000,
        commission_rate: float = 0.001,
    ) -> None:
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate

    def run(
        self,
        strategy: BaseStrategy,
        prices: dict[str, pd.DataFrame],
        *,
        start_date: str = "",
        end_date: str = "",
        context_by_date: dict[str, dict[str, Any]] | None = None,
    ) -> BacktestResult:
        """Run a backtest simulation.

        Args:
            strategy: Strategy instance to test.
            prices: Dict mapping ticker to OHLCV DataFrame (DatetimeIndex).
            start_date: Simulation start (YYYY-MM-DD). Defaults to earliest data.
            end_date: Simulation end (YYYY-MM-DD). Defaults to latest data.
            context_by_date: Optional dict mapping date string to context data
                             (sentiment scores, indicators, etc).

        Returns:
            BacktestResult with trades, equity curve, and summary stats.
        """
        logger.info(
            "backtest_start",
            strategy=strategy.name,
            tickers=list(prices.keys()),
        )

        # Build unified date index
        trading_dates = self._build_date_index(prices, start_date, end_date)
        if not trading_dates:
            logger.warning("no_trading_dates")
            return BacktestResult(strategy_name=strategy.name)

        portfolio = Portfolio(
            initial_capital=self.initial_capital,
            commission_rate=self.commission_rate,
        )

        strategy.initialize(list(prices.keys()))

        equity_curve: dict[str, float] = {}
        context_by_date = context_by_date or {}

        for date_ts in trading_dates:
            date_str = date_ts.strftime("%Y-%m-%d")

            # Prepare price slices up to current date
            price_slices = {}
            current_prices: dict[str, float] = {}
            for ticker, df in prices.items():
                df_slice = df[df.index <= date_ts]
                if not df_slice.empty:
                    price_slices[ticker] = df_slice
                    current_prices[ticker] = float(df_slice["close"].iloc[-1])

            if not price_slices:
                continue

            # Get context for this date
            context = context_by_date.get(date_str)

            # Generate signals
            signals = strategy.generate_signals(date_str, price_slices, context)

            # Execute signals
            for signal in signals:
                if signal.signal_type == SignalType.HOLD:
                    continue

                ticker = signal.ticker
                if ticker not in current_prices:
                    continue

                price = current_prices[ticker]

                if signal.signal_type == SignalType.BUY:
                    if portfolio.has_position(ticker):
                        continue  # Already in position

                    # Calculate quantity from allocation
                    invest_amount = portfolio.cash * signal.allocation
                    quantity = int(invest_amount / price) if price > 0 else 0
                    if quantity <= 0:
                        continue

                    order = Order(
                        date=date_str,
                        ticker=ticker,
                        side=OrderSide.BUY,
                        quantity=quantity,
                        price=price,
                        reason=signal.reason,
                    )
                    if portfolio.execute_order(order):
                        strategy.on_trade(ticker, SignalType.BUY, date_str)

                elif signal.signal_type == SignalType.SELL:
                    if not portfolio.has_position(ticker):
                        continue

                    pos = portfolio.positions[ticker]
                    order = Order(
                        date=date_str,
                        ticker=ticker,
                        side=OrderSide.SELL,
                        quantity=pos.quantity,
                        price=price,
                        reason=signal.reason,
                    )
                    if portfolio.execute_order(order):
                        strategy.on_trade(ticker, SignalType.SELL, date_str)

            # Record equity
            equity_curve[date_str] = round(
                portfolio.total_value(current_prices), 2,
            )

        # Final value
        final_value = equity_curve.get(
            trading_dates[-1].strftime("%Y-%m-%d"),
            self.initial_capital,
        )
        total_return = (
            ((final_value / self.initial_capital) - 1) * 100
            if self.initial_capital > 0
            else 0
        )

        result = BacktestResult(
            strategy_name=strategy.name,
            tickers=list(prices.keys()),
            start_date=trading_dates[0].strftime("%Y-%m-%d"),
            end_date=trading_dates[-1].strftime("%Y-%m-%d"),
            initial_capital=self.initial_capital,
            final_value=round(final_value, 2),
            total_return_pct=round(total_return, 2),
            trades=portfolio.completed_trades,
            equity_curve=equity_curve,
            order_count=len(portfolio.order_history),
        )

        logger.info(
            "backtest_complete",
            strategy=strategy.name,
            total_return=f"{total_return:.2f}%",
            trades=len(portfolio.completed_trades),
        )
        return result

    def _build_date_index(
        self,
        prices: dict[str, pd.DataFrame],
        start_date: str,
        end_date: str,
    ) -> list[pd.Timestamp]:
        """Build sorted list of unique trading dates across all tickers."""
        all_dates: set[pd.Timestamp] = set()
        for df in prices.values():
            all_dates.update(df.index)

        if not all_dates:
            return []

        sorted_dates = sorted(all_dates)

        if start_date:
            start_ts = pd.Timestamp(start_date)
            sorted_dates = [d for d in sorted_dates if d >= start_ts]
        if end_date:
            end_ts = pd.Timestamp(end_date)
            sorted_dates = [d for d in sorted_dates if d <= end_ts]

        return sorted_dates
