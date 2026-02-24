"""Backtest result summary report generation."""

from __future__ import annotations

from src.backtesting.engine.backtest_engine import BacktestResult
from src.backtesting.metrics.performance import PerformanceMetrics, calculate_metrics


def generate_summary(
    result: BacktestResult,
    risk_free_rate: float = 0.03,
) -> str:
    """Generate a human-readable backtest summary report.

    Args:
        result: BacktestResult from a backtest run.
        risk_free_rate: Annual risk-free rate for Sharpe calculation.

    Returns:
        Formatted summary string.
    """
    metrics = calculate_metrics(
        equity_curve=result.equity_curve,
        trades=result.trades,
        initial_capital=result.initial_capital,
        risk_free_rate=risk_free_rate,
    )

    lines = [
        "=" * 60,
        f"  백테스트 결과: {result.strategy_name}",
        "=" * 60,
        "",
        f"  기간: {result.start_date} ~ {result.end_date}",
        f"  대상: {', '.join(result.tickers[:5])}{'...' if len(result.tickers) > 5 else ''}",
        f"  초기 자본: {result.initial_capital:,.0f}",
        f"  최종 가치: {result.final_value:,.0f}",
        "",
        "-" * 60,
        "  수익률",
        "-" * 60,
        f"  총 수익률:      {metrics.total_return_pct:+.2f}%",
        f"  연평균 수익률:   {metrics.annualized_return_pct:+.2f}%",
        f"  최대 낙폭(MDD): {metrics.max_drawdown_pct:.2f}%",
        "",
        "-" * 60,
        "  위험 지표",
        "-" * 60,
        f"  샤프 비율:   {metrics.sharpe_ratio:.2f}",
        f"  소르티노 비율: {metrics.sortino_ratio:.2f}",
        f"  투자 비중:   {metrics.exposure_pct:.1f}%",
        "",
        "-" * 60,
        "  거래 통계",
        "-" * 60,
        f"  총 거래 수:      {metrics.total_trades}",
        f"  승리/패배:       {metrics.winning_trades}/{metrics.losing_trades}",
        f"  승률:            {metrics.win_rate_pct:.1f}%",
        f"  수익 팩터:       {metrics.profit_factor:.2f}",
        f"  평균 수익 거래:  {metrics.avg_win_pct:+.2f}%",
        f"  평균 손실 거래:  {metrics.avg_loss_pct:+.2f}%",
        f"  평균 보유 기간:  {metrics.avg_holding_days:.0f}일",
        f"  최대 연승:       {metrics.max_consecutive_wins}연승",
        f"  최대 연패:       {metrics.max_consecutive_losses}연패",
        f"  최고 거래:       {metrics.best_trade_pct:+.2f}%",
        f"  최악 거래:       {metrics.worst_trade_pct:+.2f}%",
        "",
        "=" * 60,
    ]

    return "\n".join(lines)


def metrics_to_dict(result: BacktestResult) -> dict:
    """Convert backtest result to a flat dictionary for comparison.

    Args:
        result: BacktestResult from a backtest run.

    Returns:
        Dict with key metrics.
    """
    metrics = calculate_metrics(
        equity_curve=result.equity_curve,
        trades=result.trades,
        initial_capital=result.initial_capital,
    )
    return {
        "strategy": result.strategy_name,
        "period": f"{result.start_date} ~ {result.end_date}",
        "total_return_pct": metrics.total_return_pct,
        "annualized_return_pct": metrics.annualized_return_pct,
        "max_drawdown_pct": metrics.max_drawdown_pct,
        "sharpe_ratio": metrics.sharpe_ratio,
        "win_rate_pct": metrics.win_rate_pct,
        "profit_factor": metrics.profit_factor,
        "total_trades": metrics.total_trades,
    }
