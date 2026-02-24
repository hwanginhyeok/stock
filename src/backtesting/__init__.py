"""Backtesting framework for strategy validation.

Modules:
    data/       — Historical price data loading and storage
    strategy/   — Trading strategy definitions
    engine/     — Simulation engine and portfolio management
    metrics/    — Performance evaluation metrics
    report/     — Result reporting and visualization
"""

from src.backtesting.engine.backtest_engine import BacktestEngine, BacktestResult
from src.backtesting.engine.order import Order, OrderSide
from src.backtesting.engine.portfolio import Portfolio
from src.backtesting.metrics.performance import PerformanceMetrics, calculate_metrics
from src.backtesting.strategy.base import BaseStrategy, Signal, SignalType

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "BaseStrategy",
    "Order",
    "OrderSide",
    "PerformanceMetrics",
    "Portfolio",
    "Signal",
    "SignalType",
    "calculate_metrics",
]
