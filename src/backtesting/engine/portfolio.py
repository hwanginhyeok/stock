"""Portfolio and position management for backtesting."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.backtesting.engine.order import Order, OrderSide
from src.core.logger import get_logger

logger = get_logger("portfolio")


class Position(BaseModel):
    """An open position in a single stock.

    Attributes:
        ticker: Stock ticker symbol.
        quantity: Number of shares held.
        avg_price: Average cost basis per share.
        total_cost: Total amount invested.
    """

    ticker: str
    quantity: int = 0
    avg_price: float = 0.0
    total_cost: float = 0.0


class Trade(BaseModel):
    """A completed round-trip trade (buy then sell).

    Attributes:
        ticker: Stock ticker symbol.
        entry_date: Buy date.
        exit_date: Sell date.
        entry_price: Buy price per share.
        exit_price: Sell price per share.
        quantity: Number of shares.
        pnl: Realized profit/loss.
        return_pct: Return percentage.
        holding_days: Number of days held.
        reason_entry: Why bought.
        reason_exit: Why sold.
    """

    ticker: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    quantity: int
    pnl: float = 0.0
    return_pct: float = 0.0
    holding_days: int = 0
    reason_entry: str = ""
    reason_exit: str = ""


class Portfolio:
    """Manages cash, positions, and trade history during backtesting.

    Args:
        initial_capital: Starting cash amount.
        commission_rate: Transaction cost as fraction of trade value (default 0.1%).
    """

    def __init__(
        self,
        initial_capital: float = 10_000_000,
        commission_rate: float = 0.001,
    ) -> None:
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.positions: dict[str, Position] = {}
        self.completed_trades: list[Trade] = []
        self.order_history: list[Order] = []
        self._pending_entries: dict[str, Order] = {}

    def execute_order(self, order: Order) -> bool:
        """Execute a buy or sell order.

        Args:
            order: Order to execute.

        Returns:
            True if order was executed successfully.
        """
        commission = order.quantity * order.price * self.commission_rate
        order.commission = round(commission, 2)

        if order.side == OrderSide.BUY:
            return self._execute_buy(order)
        return self._execute_sell(order)

    def _execute_buy(self, order: Order) -> bool:
        """Execute a buy order."""
        total_cost = order.quantity * order.price + order.commission
        if total_cost > self.cash:
            logger.debug(
                "insufficient_cash",
                ticker=order.ticker,
                required=total_cost,
                available=self.cash,
            )
            return False

        self.cash -= total_cost

        if order.ticker in self.positions:
            pos = self.positions[order.ticker]
            new_total = pos.total_cost + total_cost
            new_qty = pos.quantity + order.quantity
            pos.quantity = new_qty
            pos.total_cost = new_total
            pos.avg_price = new_total / new_qty if new_qty > 0 else 0
        else:
            self.positions[order.ticker] = Position(
                ticker=order.ticker,
                quantity=order.quantity,
                avg_price=order.price,
                total_cost=total_cost,
            )

        self._pending_entries[order.ticker] = order
        self.order_history.append(order)
        return True

    def _execute_sell(self, order: Order) -> bool:
        """Execute a sell order."""
        if order.ticker not in self.positions:
            return False

        pos = self.positions[order.ticker]
        sell_qty = min(order.quantity, pos.quantity)
        if sell_qty <= 0:
            return False

        proceeds = sell_qty * order.price - order.commission
        self.cash += proceeds

        # Record completed trade
        entry_order = self._pending_entries.get(order.ticker)
        entry_date = entry_order.date if entry_order else ""
        entry_price = pos.avg_price

        pnl = (order.price - entry_price) * sell_qty - order.commission
        return_pct = ((order.price / entry_price) - 1) * 100 if entry_price > 0 else 0

        # Calculate holding days
        holding_days = 0
        if entry_date and order.date:
            try:
                from datetime import datetime

                d1 = datetime.strptime(entry_date, "%Y-%m-%d")
                d2 = datetime.strptime(order.date, "%Y-%m-%d")
                holding_days = (d2 - d1).days
            except ValueError:
                pass

        self.completed_trades.append(
            Trade(
                ticker=order.ticker,
                entry_date=entry_date,
                exit_date=order.date,
                entry_price=entry_price,
                exit_price=order.price,
                quantity=sell_qty,
                pnl=round(pnl, 2),
                return_pct=round(return_pct, 2),
                holding_days=holding_days,
                reason_entry=entry_order.reason if entry_order else "",
                reason_exit=order.reason,
            )
        )

        pos.quantity -= sell_qty
        if pos.quantity <= 0:
            del self.positions[order.ticker]
            self._pending_entries.pop(order.ticker, None)
        else:
            pos.total_cost = pos.quantity * pos.avg_price

        self.order_history.append(order)
        return True

    def total_value(self, current_prices: dict[str, float]) -> float:
        """Calculate total portfolio value (cash + positions).

        Args:
            current_prices: Dict mapping ticker to current price.

        Returns:
            Total portfolio value.
        """
        position_value = sum(
            pos.quantity * current_prices.get(pos.ticker, pos.avg_price)
            for pos in self.positions.values()
        )
        return self.cash + position_value

    def position_count(self) -> int:
        """Number of open positions."""
        return len(self.positions)

    def has_position(self, ticker: str) -> bool:
        """Check if a position exists for a ticker."""
        return ticker in self.positions and self.positions[ticker].quantity > 0
