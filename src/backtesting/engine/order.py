"""Order model for backtesting trades."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class OrderSide(StrEnum):
    """Trade direction."""

    BUY = "buy"
    SELL = "sell"


class Order(BaseModel):
    """A trade order executed during backtesting.

    Attributes:
        date: Execution date (YYYY-MM-DD).
        ticker: Stock ticker symbol.
        side: Buy or sell.
        quantity: Number of shares.
        price: Execution price per share.
        reason: Signal/strategy reason for the trade.
        commission: Transaction cost.
    """

    date: str
    ticker: str
    side: OrderSide
    quantity: int
    price: float
    reason: str = ""
    commission: float = 0.0

    @property
    def total_cost(self) -> float:
        """Total cost including commission."""
        return self.quantity * self.price + self.commission
