#!/usr/bin/env python3
"""SMA 정배열 + 눌림목 백테스트 실행 스크립트.

1-52: TSLA 일봉 2년치로 전략 성과 측정.

Usage:
    python3 scripts/backtest_sma_strategy.py
    python3 scripts/backtest_sma_strategy.py --ticker TSLA --period 3y --capital 10000000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
import pandas as pd

from src.backtesting.engine.backtest_engine import BacktestEngine
from src.backtesting.metrics.performance import calculate_metrics
from src.backtesting.strategy.sma_alignment_strategy import SMAAlignmentStrategy


def fetch_ohlcv(ticker: str, period: str) -> pd.DataFrame:
    """yfinance로 OHLCV 데이터 다운로드 (DatetimeIndex, 소문자 컬럼)."""
    hist = yf.Ticker(ticker).history(period=period, interval="1d")
    if hist is None or hist.empty:
        raise RuntimeError(f"{ticker} 데이터 다운로드 실패")

    df = hist[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.columns = ["open", "high", "low", "close", "volume"]
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df.sort_index()
    return df


def print_report(result, metrics, ticker: str, period: str) -> str:
    """백테스트 결과 리포트 출력 및 반환."""
    lines = [
        "",
        "=" * 60,
        f" SMA 정배열 + 눌림목 백테스트 — {ticker} ({period})",
        "=" * 60,
        f" 기간: {result.start_date} ~ {result.end_date}",
        f" 초기 자본: ${result.initial_capital:,.0f}",
        f" 최종 자산: ${result.final_value:,.0f}",
        "",
        "── 수익률 ──────────────────────────────────",
        f"  총 수익률:       {metrics.total_return_pct:+.2f}%",
        f"  연환산 수익률:   {metrics.annualized_return_pct:+.2f}%",
        f"  최대 낙폭:       {metrics.max_drawdown_pct:.2f}%",
        f"  샤프 비율:       {metrics.sharpe_ratio:.2f}",
        f"  소르티노 비율:   {metrics.sortino_ratio:.2f}",
        "",
        "── 거래 통계 ──────────────────────────────",
        f"  총 거래 수:      {metrics.total_trades}회",
        f"  승률:            {metrics.win_rate_pct:.1f}%",
        f"  손익비:          {metrics.profit_factor:.2f}",
        f"  평균 수익:       {metrics.avg_win_pct:+.2f}%",
        f"  평균 손실:       {metrics.avg_loss_pct:+.2f}%",
        f"  평균 보유일:     {metrics.avg_holding_days:.1f}일",
        f"  최장 연승:       {metrics.max_consecutive_wins}회",
        f"  최장 연패:       {metrics.max_consecutive_losses}회",
        f"  최고 단일 수익:  {metrics.best_trade_pct:+.2f}%",
        f"  최악 단일 손실:  {metrics.worst_trade_pct:+.2f}%",
        f"  노출 비율:       {metrics.exposure_pct:.1f}%",
    ]

    if result.trades:
        lines += ["", "── 개별 거래 내역 ──────────────────────────"]
        for t in result.trades:
            pnl = getattr(t, 'pnl_pct', None) or getattr(t, 'return_pct', None) or 0.0
            buy_d = getattr(t, 'entry_date', '') or getattr(t, 'buy_date', '')
            sell_d = getattr(t, 'exit_date', '') or getattr(t, 'sell_date', '')
            lines.append(f"  {buy_d} → {sell_d}  {pnl:+.2f}%")

    lines += ["=" * 60, ""]
    report = "\n".join(lines)
    print(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="SMA 정배열 눌림목 백테스트")
    parser.add_argument("--ticker", default="TSLA", help="티커 (기본: TSLA)")
    parser.add_argument("--period", default="2y", choices=["1y", "2y", "3y", "5y"],
                        help="백테스트 기간 (기본: 2y)")
    parser.add_argument("--capital", type=float, default=10_000_000,
                        help="초기 자본 (기본: 10,000,000)")
    parser.add_argument("--allocation", type=float, default=0.8,
                        help="매수 시 투입 비율 (기본: 0.8)")
    parser.add_argument("--lookback", type=int, default=5,
                        help="눌림목 탐색 봉 수 (기본: 5)")
    parser.add_argument("--tolerance", type=float, default=0.005,
                        help="터치 허용 폭 (기본: 0.005 = ±0.5%%)")
    parser.add_argument("--output", default="docs/research/backtest_sma_result.md",
                        help="결과 저장 경로")
    args = parser.parse_args()

    print(f"\n데이터 다운로드 중: {args.ticker} ({args.period})...")
    df = fetch_ohlcv(args.ticker, args.period)
    print(f"  {len(df)}봉 로드 완료 ({df.index[0].date()} ~ {df.index[-1].date()})")

    strategy = SMAAlignmentStrategy(
        allocation=args.allocation,
        lookback=args.lookback,
        touch_tolerance=args.tolerance,
    )

    engine = BacktestEngine(
        initial_capital=args.capital,
        commission_rate=0.001,  # 0.1% 수수료
    )

    print(f"\n백테스트 실행: {strategy.name}...")
    result = engine.run(
        strategy=strategy,
        prices={args.ticker: df},
        start_date=df.index[0].strftime("%Y-%m-%d"),
        end_date=df.index[-1].strftime("%Y-%m-%d"),
    )

    metrics = calculate_metrics(
        equity_curve=result.equity_curve,
        trades=result.trades,
        initial_capital=result.initial_capital,
    )
    report = print_report(result, metrics, args.ticker, args.period)

    # 리포트 저장
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md_content = f"# SMA 정배열 + 눌림목 백테스트 — {args.ticker} ({args.period})\n\n```\n{report}\n```\n"
    out_path.write_text(md_content, encoding="utf-8")
    print(f"리포트 저장: {out_path}")


if __name__ == "__main__":
    main()
