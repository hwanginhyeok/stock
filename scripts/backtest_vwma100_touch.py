#!/usr/bin/env python3
"""VWMA100 터치 매수 백테스트.

전략:
  - 매수: 저가가 VWMA100에 닿고 (low <= VWMA100 * 1.01), 종가는 VWMA100 위
          + 직전 N봉에서 종가가 VWMA100 위였던 적 있음 (돌파 이력)
  - 매도: 종가가 VWMA100 아래로 이탈 (close < VWMA100)
"""

from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yfinance as yf
import pandas as pd
import numpy as np

TICKER     = "TSLA"
PERIOD     = "5y"
TOUCH_PCT  = 0.01   # 저가가 VWMA100의 1% 이내면 "터치"
HISTORY_N  = 20     # 돌파 이력 탐색 봉 수
SLOPE_N    = 20     # 기울기 비교 봉 수 (우상향 필터용)


def vwma(close: pd.Series, volume: pd.Series, period: int) -> pd.Series:
    pv   = (close * volume).rolling(period, min_periods=period).sum()
    vsum = volume.rolling(period, min_periods=period).sum()
    return pv / vsum.replace(0, np.nan)


def simulate(df: pd.DataFrame, slope_filter: bool) -> list[dict]:
    trades      = []
    in_position = False
    entry_date  = None
    entry_price = None

    start = max(HISTORY_N, SLOPE_N)
    for i in range(start, len(df)):
        row   = df.iloc[i]
        vw    = row["vwma100"]
        close = row["close"]
        low   = row["low"]

        if in_position:
            if close < vw:
                pnl = (close - entry_price) / entry_price * 100
                trades.append({
                    "진입일": str(entry_date.date()),
                    "청산일": str(df.index[i].date()),
                    "진입가": round(entry_price, 2),
                    "청산가": round(close, 2),
                    "보유일": (df.index[i] - entry_date).days,
                    "수익률": round(pnl, 2),
                })
                in_position = False
        else:
            touch        = low <= vw * (1 + TOUCH_PCT)
            above        = close >= vw
            had_breakout = (df["close"].iloc[i-HISTORY_N:i] > df["vwma100"].iloc[i-HISTORY_N:i]).any()

            # 기울기 필터: VWMA100이 SLOPE_N봉 전보다 높음 (우상향)
            slope_ok = True
            if slope_filter:
                vw_past  = df["vwma100"].iloc[i - SLOPE_N]
                slope_ok = (vw > vw_past) if pd.notna(vw_past) else False

            if touch and above and had_breakout and slope_ok:
                entry_date  = df.index[i]
                entry_price = close
                in_position = True

    if in_position:
        last = df.iloc[-1]
        pnl  = (last["close"] - entry_price) / entry_price * 100
        trades.append({
            "진입일": str(entry_date.date()),
            "청산일": f"{df.index[-1].date()} 🔄",
            "진입가": round(entry_price, 2),
            "청산가": round(last["close"], 2),
            "보유일": (df.index[-1] - entry_date).days,
            "수익률": round(pnl, 2),
        })

    return trades


def stats(trades: list[dict]) -> dict:
    closed = [t for t in trades if "🔄" not in t["청산일"]]
    if not closed:
        return {}
    rets = [t["수익률"] for t in closed]
    wins = [r for r in rets if r > 0]
    loss = [r for r in rets if r <= 0]
    pf   = abs(sum(wins) / sum(loss)) if loss and sum(loss) != 0 else float("inf")
    return {
        "거래수":   len(closed),
        "승률":     round(len(wins) / len(closed) * 100, 1),
        "평균수익": round(sum(wins) / len(wins), 2) if wins else 0,
        "평균손실": round(sum(loss) / len(loss), 2) if loss else 0,
        "손익비":   round(pf, 2),
        "누적":     round(sum(rets), 2),
        "평균보유": round(sum(t["보유일"] for t in closed) / len(closed)),
        "최대손실": round(min(rets), 2),
        "최대수익": round(max(rets), 2),
    }


def run():
    print(f"\n{TICKER} {PERIOD} 데이터 다운로드 중...")
    hist = yf.Ticker(TICKER).history(period=PERIOD, interval="1d")
    df   = hist[["Open","High","Low","Close","Volume"]].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.columns = ["open","high","low","close","volume"]
    df["vwma100"] = vwma(df["close"], df["volume"], 100)
    df = df.dropna(subset=["vwma100"]).copy()
    print(f"{len(df)}봉  ({df.index[0].date()} ~ {df.index[-1].date()})\n")

    t_base   = simulate(df, slope_filter=False)
    t_slope  = simulate(df, slope_filter=True)
    s_base   = stats(t_base)
    s_slope  = stats(t_slope)

    # ── 거래 내역 비교
    W = 33
    print("─"*68)
    print(f"{'[A] 기본  (필터 없음)':^33}│{'[B] 기울기 필터 추가 (VWMA100 우상향)':^33}")
    print("─"*68)

    # 행별 정렬
    def fmt(t):
        sign = "✅" if t["수익률"] > 0 else ("🔄" if "🔄" in t["청산일"] else "❌")
        return f"{t['진입일']}~{t['청산일'][:10]}  {t['수익률']:+.1f}% {sign}"

    rows_a = [fmt(t) for t in t_base]
    rows_b = [fmt(t) for t in t_slope]
    for i in range(max(len(rows_a), len(rows_b))):
        a = rows_a[i] if i < len(rows_a) else ""
        b = rows_b[i] if i < len(rows_b) else ""
        print(f"{a:<33}│{b}")

    # ── 통계 비교
    print("\n" + "="*68)
    print(f"{'항목':<14} {'[A] 기본':>12}   {'[B] 기울기 필터':>14}   {'차이':>8}")
    print("─"*68)
    keys = [
        ("거래수",   "회",   False),
        ("승률",     "%",    False),
        ("평균수익", "%",    True),
        ("평균손실", "%",    True),
        ("손익비",   "",     False),
        ("누적",     "%",    True),
        ("평균보유", "일",   False),
        ("최대손실", "%",    True),
        ("최대수익", "%",    True),
    ]
    for key, unit, signed in keys:
        a = s_base.get(key, 0)
        b = s_slope.get(key, 0)
        diff = b - a
        sign = "+" if diff > 0 else ""
        fmt_diff = f"{sign}{diff:.1f}{unit}"
        arrow = "↑" if diff > 0 else ("↓" if diff < 0 else "─")
        print(f"  {key:<12} {a:>8}{unit}   {b:>10}{unit}   {arrow} {fmt_diff}")
    print("="*68)

    # ── 필터로 제거된 거래
    filtered = set(t["진입일"] for t in t_base) - set(t["진입일"] for t in t_slope)
    if filtered:
        removed = [t for t in t_base if t["진입일"] in filtered]
        print(f"\n[B]에서 제거된 거래 ({len(removed)}건) — VWMA100 우하향 구간:")
        for t in removed:
            sign = "✅" if t["수익률"] > 0 else "❌"
            print(f"  {t['진입일']} ~ {t['청산일'][:10]}  {t['수익률']:+.2f}%  {sign}")

    # 현재 상태
    last_vwma  = df["vwma100"].iloc[-1]
    prev_vwma  = df["vwma100"].iloc[-SLOPE_N]
    last_close = df["close"].iloc[-1]
    slope_now  = "우상향 ↑" if last_vwma > prev_vwma else "우하향 ↓"
    print(f"\n현재: 종가 ${last_close:.2f} | VWMA100 ${last_vwma:.2f} ({slope_now}) | "
          f"괴리 {(last_close/last_vwma-1)*100:+.1f}%")


if __name__ == "__main__":
    run()
