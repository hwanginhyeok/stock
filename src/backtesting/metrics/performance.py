"""Performance metrics calculation for backtesting results."""

from __future__ import annotations

import math
from typing import Any

from pydantic import BaseModel, Field

from src.backtesting.engine.portfolio import Trade


class PerformanceMetrics(BaseModel):
    """Comprehensive performance metrics for a backtest.

    Attributes:
        total_return_pct: Total return percentage.
        annualized_return_pct: Annualized return percentage.
        max_drawdown_pct: Maximum drawdown percentage.
        sharpe_ratio: Risk-adjusted return (annualized).
        sortino_ratio: Downside risk-adjusted return.
        win_rate_pct: Percentage of profitable trades.
        profit_factor: Gross profit / gross loss.
        total_trades: Number of completed round-trip trades.
        winning_trades: Number of profitable trades.
        losing_trades: Number of losing trades.
        avg_win_pct: Average winning trade return.
        avg_loss_pct: Average losing trade return.
        avg_holding_days: Average holding period in days.
        max_consecutive_wins: Longest winning streak.
        max_consecutive_losses: Longest losing streak.
        best_trade_pct: Best single trade return.
        worst_trade_pct: Worst single trade return.
        exposure_pct: Fraction of time invested.
    """

    total_return_pct: float = 0.0
    annualized_return_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    win_rate_pct: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win_pct: float = 0.0
    avg_loss_pct: float = 0.0
    avg_holding_days: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    best_trade_pct: float = 0.0
    worst_trade_pct: float = 0.0
    exposure_pct: float = 0.0


def calculate_metrics(
    equity_curve: dict[str, float],
    trades: list[Trade],
    initial_capital: float,
    risk_free_rate: float = 0.03,
) -> PerformanceMetrics:
    """Calculate comprehensive performance metrics.

    Args:
        equity_curve: Dict mapping date to portfolio value.
        trades: List of completed Trade objects.
        initial_capital: Starting capital.
        risk_free_rate: Annual risk-free rate for Sharpe calculation.

    Returns:
        PerformanceMetrics with all calculated values.
    """
    if not equity_curve:
        return PerformanceMetrics()

    values = list(equity_curve.values())
    dates = list(equity_curve.keys())
    total_days = len(values)

    # Total return
    final_value = values[-1]
    total_return = ((final_value / initial_capital) - 1) * 100 if initial_capital > 0 else 0

    # Annualized return
    years = total_days / 252 if total_days > 0 else 1
    annualized = (
        ((final_value / initial_capital) ** (1 / years) - 1) * 100
        if years > 0 and initial_capital > 0 and final_value > 0
        else 0
    )

    # Max drawdown
    max_dd = _max_drawdown(values)

    # Daily returns for Sharpe/Sortino
    daily_returns = _daily_returns(values)
    sharpe = _sharpe_ratio(daily_returns, risk_free_rate)
    sortino = _sortino_ratio(daily_returns, risk_free_rate)

    # Trade statistics
    trade_stats = _trade_statistics(trades)

    # Exposure (fraction of time with open positions)
    exposure = _calculate_exposure(trades, dates) if trades and dates else 0

    return PerformanceMetrics(
        total_return_pct=round(total_return, 2),
        annualized_return_pct=round(annualized, 2),
        max_drawdown_pct=round(max_dd, 2),
        sharpe_ratio=round(sharpe, 2),
        sortino_ratio=round(sortino, 2),
        exposure_pct=round(exposure, 2),
        **trade_stats,
    )


def _max_drawdown(values: list[float]) -> float:
    """Calculate maximum drawdown percentage."""
    if not values:
        return 0.0

    peak = values[0]
    max_dd = 0.0
    for val in values:
        if val > peak:
            peak = val
        dd = ((peak - val) / peak) * 100 if peak > 0 else 0
        max_dd = max(max_dd, dd)
    return max_dd


def _daily_returns(values: list[float]) -> list[float]:
    """Calculate daily return percentages."""
    if len(values) < 2:
        return []
    return [
        (values[i] - values[i - 1]) / values[i - 1] * 100
        for i in range(1, len(values))
        if values[i - 1] > 0
    ]


def _sharpe_ratio(daily_returns: list[float], risk_free_rate: float) -> float:
    """Calculate annualized Sharpe ratio."""
    if len(daily_returns) < 2:
        return 0.0

    daily_rf = risk_free_rate / 252
    excess = [r / 100 - daily_rf for r in daily_returns]

    mean_excess = sum(excess) / len(excess)
    variance = sum((r - mean_excess) ** 2 for r in excess) / (len(excess) - 1)
    std = math.sqrt(variance) if variance > 0 else 0

    if std == 0:
        return 0.0
    return (mean_excess / std) * math.sqrt(252)


def _sortino_ratio(daily_returns: list[float], risk_free_rate: float) -> float:
    """Calculate annualized Sortino ratio (downside deviation only)."""
    if len(daily_returns) < 2:
        return 0.0

    daily_rf = risk_free_rate / 252
    excess = [r / 100 - daily_rf for r in daily_returns]
    downside = [r for r in excess if r < 0]

    if not downside:
        return 0.0

    mean_excess = sum(excess) / len(excess)
    down_var = sum(r ** 2 for r in downside) / len(downside)
    down_std = math.sqrt(down_var)

    if down_std == 0:
        return 0.0
    return (mean_excess / down_std) * math.sqrt(252)


def _trade_statistics(trades: list[Trade]) -> dict[str, Any]:
    """Calculate trade-level statistics."""
    if not trades:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate_pct": 0.0,
            "profit_factor": 0.0,
            "avg_win_pct": 0.0,
            "avg_loss_pct": 0.0,
            "avg_holding_days": 0.0,
            "max_consecutive_wins": 0,
            "max_consecutive_losses": 0,
            "best_trade_pct": 0.0,
            "worst_trade_pct": 0.0,
        }

    winners = [t for t in trades if t.pnl > 0]
    losers = [t for t in trades if t.pnl <= 0]

    win_rate = len(winners) / len(trades) * 100

    gross_profit = sum(t.pnl for t in winners)
    gross_loss = abs(sum(t.pnl for t in losers))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    avg_win = (
        sum(t.return_pct for t in winners) / len(winners) if winners else 0
    )
    avg_loss = (
        sum(t.return_pct for t in losers) / len(losers) if losers else 0
    )

    avg_holding = sum(t.holding_days for t in trades) / len(trades)

    # Consecutive wins/losses
    max_consec_wins = 0
    max_consec_losses = 0
    current_wins = 0
    current_losses = 0
    for t in trades:
        if t.pnl > 0:
            current_wins += 1
            current_losses = 0
            max_consec_wins = max(max_consec_wins, current_wins)
        else:
            current_losses += 1
            current_wins = 0
            max_consec_losses = max(max_consec_losses, current_losses)

    returns = [t.return_pct for t in trades]
    best = max(returns) if returns else 0
    worst = min(returns) if returns else 0

    return {
        "total_trades": len(trades),
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "win_rate_pct": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else 999.99,
        "avg_win_pct": round(avg_win, 2),
        "avg_loss_pct": round(avg_loss, 2),
        "avg_holding_days": round(avg_holding, 1),
        "max_consecutive_wins": max_consec_wins,
        "max_consecutive_losses": max_consec_losses,
        "best_trade_pct": round(best, 2),
        "worst_trade_pct": round(worst, 2),
    }


def _calculate_exposure(trades: list[Trade], dates: list[str]) -> float:
    """Calculate percentage of time with open positions."""
    if not trades or not dates:
        return 0.0

    invested_dates: set[str] = set()
    for trade in trades:
        # Mark all dates between entry and exit as invested
        in_trade = False
        for d in dates:
            if d == trade.entry_date:
                in_trade = True
            if in_trade:
                invested_dates.add(d)
            if d == trade.exit_date:
                in_trade = False

    return len(invested_dates) / len(dates) * 100 if dates else 0
