"""종목별 지표 공부 스크립트.

시총 상위 종목들의 현재 지표 + 과거 예측 정확도를 함께 출력.

Usage::

    python scripts/study_stock.py NVDA
    python scripts/study_stock.py AAPL --period 2y
    python scripts/study_stock.py MSFT --no-history
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import certifi as _certifi

_cert_src = Path(_certifi.where())
try:
    str(_cert_src).encode("ascii")
except (UnicodeEncodeError, UnicodeDecodeError):
    _cert_dst = Path(os.environ.get("TEMP", "/tmp")) / "yf_certs" / "cacert.pem"
    if not _cert_dst.exists() or _cert_dst.stat().st_size != _cert_src.stat().st_size:
        _cert_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_cert_src, _cert_dst)
    os.environ.setdefault("CURL_CA_BUNDLE", str(_cert_dst))

import numpy as np
import pandas as pd
import yfinance as yf

# Project imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.analyzers.technical import TechnicalAnalyzer, _bbands
from src.analyzers.trend import classify_stock_pattern
from src.analyzers.market_sentiment import compute_trend_strength
from src.core.config import PROJECT_ROOT

# ── ANSI color helpers ──────────────────────────────────────────────────────

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

HIST_CSV = PROJECT_ROOT / "data" / "processed" / "dashboards" / "indicator_analysis_20260228.csv"

TOP20 = [
    "NVDA", "AAPL", "GOOGL", "MSFT", "AMZN",
    "META", "AVGO", "TSLA", "BRK-B", "WMT",
    "LLY",  "JPM",  "XOM",  "V",    "MA",
    "COST", "ORCL", "NFLX", "PG",   "HD",
]


def _color_val(val: float | None, good_high: bool = True, fmt: str = ".1f") -> str:
    """Return ANSI-colored string based on value direction."""
    if val is None:
        return f"{DIM}N/A{RESET}"
    color = GREEN if (val > 0) == good_high else RED
    return f"{color}{val:{fmt}}{RESET}"


def _bar(value: float, low: float = 0, high: float = 100, width: int = 20) -> str:
    """Render a simple ASCII progress bar."""
    pct = max(0.0, min(1.0, (value - low) / (high - low)))
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


def _fetch_ohlcv(ticker: str, period: str) -> pd.DataFrame:
    yf_ticker = yf.Ticker(ticker)
    df = yf_ticker.history(period=period)
    if df.empty:
        return pd.DataFrame(), yf_ticker
    cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    return df[cols], yf_ticker


def _hist_record(ticker: str) -> pd.Series | None:
    """Load 2026-02-28 indicator snapshot for a ticker."""
    if not HIST_CSV.exists():
        return None
    df = pd.read_csv(HIST_CSV)
    row = df[df["ticker"] == ticker]
    return row.iloc[0] if not row.empty else None


def _accuracy_summary(df: pd.DataFrame) -> dict[str, dict]:
    """Compute per-indicator accuracy against actual_dir (5d)."""
    results = {}
    total = len(df)
    up_mask = df["actual_dir"] == "상승"

    checks = {
        "RSI > 50": df["rsi"] > 50,
        "MACD Bullish": df["macd_bullish"] == True,
        "Supertrend Up": df["st_dir"] == 1,
        "EMA 정배열": df["ema_align"] == "정배열",
        "Price > EMA200": df["price_vs_ema200"] > 0,
        "ADX > 25": df["adx"] > 25,
        "DI Spread > 0": df["di_spread"] > 0,
        "BB Pos > 50": df["bb_pos"] > 50,
        "Vol Ratio > 1": df["vol_ratio"] > 1,
    }

    for label, signal in checks.items():
        n_signal = signal.sum()
        n_hit = (signal & up_mask).sum()
        acc = n_hit / n_signal * 100 if n_signal > 0 else 0
        results[label] = {
            "n": int(n_signal),
            "acc": round(acc, 1),
            "pct_of_total": round(n_signal / total * 100, 1),
        }
    return results


def print_header(ticker: str, name: str, sector: str, market_cap: int | None) -> None:
    cap_str = ""
    if market_cap:
        if market_cap >= 1e12:
            cap_str = f"  시총 ${market_cap/1e12:.2f}T"
        else:
            cap_str = f"  시총 ${market_cap/1e9:.0f}B"
    rank = TOP20.index(ticker) + 1 if ticker in TOP20 else "?"
    print()
    print(f"{BOLD}{'═' * 62}{RESET}")
    print(f"{BOLD}  #{rank}  {ticker}  |  {name}{RESET}")
    print(f"  Sector: {sector}{cap_str}")
    print(f"{BOLD}{'═' * 62}{RESET}")


def print_price_section(price: float, d1: float | None, w1: float | None, m1: float | None, m3: float | None) -> None:
    print(f"\n{CYAN}── 가격 변화 ──────────────────────────────────{RESET}")
    print(f"  현재가:  ${price:>10.2f}")
    print(f"  1일:     {_color_val(d1):>20s}%")
    print(f"  1주:     {_color_val(w1):>20s}%")
    print(f"  1개월:   {_color_val(m1):>20s}%")
    print(f"  3개월:   {_color_val(m3):>20s}%")


def print_indicators(
    tech_score: float,
    rsi: float | None,
    rsi_state: str,
    macd_signal: str,
    adx: float | None,
    adx_trend: str,
    di_spread: float | None,
    supertrend_dir: str,
    ema_alignment: str,
    price_vs_ema200: float | None,
    bb_pos: float | None,
    vol_ratio: float | None,
    trend_regime: str,
    pattern: str,
    pattern_kr: str,
    pattern_score: int,
) -> None:
    print(f"\n{CYAN}── 종합 점수 ──────────────────────────────────{RESET}")
    score_color = GREEN if tech_score >= 60 else (RED if tech_score < 40 else YELLOW)
    print(f"  Tech Score: {score_color}{BOLD}{tech_score:5.1f}{RESET}  {_bar(tech_score)}")

    # Trend Regime
    regime_color = GREEN if "Up" in trend_regime else (RED if "Down" in trend_regime else YELLOW)
    print(f"  Trend Regime: {regime_color}{trend_regime}{RESET}")

    # Pattern
    pat_color = GREEN if pattern == "Breakout" else (YELLOW if pattern == "Pullback" else DIM)
    print(f"  Pattern:  {pat_color}{pattern} ({pattern_kr}){RESET}  [score {pattern_score}/5]")

    print(f"\n{CYAN}── 개별 지표 ──────────────────────────────────{RESET}")

    # RSI
    rsi_color = RED if (rsi or 50) >= 70 else (GREEN if (rsi or 50) <= 30 else RESET)
    rsi_str = f"{rsi_color}{rsi:.1f}{RESET}" if rsi else f"{DIM}N/A{RESET}"
    print(f"  RSI (14):     {rsi_str:>20s}  {rsi_state}")

    # MACD
    macd_color = GREEN if macd_signal == "Bullish" else RED
    print(f"  MACD:         {macd_color}{macd_signal:>20s}{RESET}")

    # ADX
    adx_str = f"{adx:.1f}" if adx else "N/A"
    adx_strength = "강한 추세" if (adx or 0) >= 25 else "약한 추세/횡보"
    adx_color = GREEN if (adx or 0) >= 25 else DIM
    print(f"  ADX (14):     {adx_color}{adx_str:>20s}{RESET}  {adx_trend}  ({adx_strength})")

    # DI Spread
    di_color = GREEN if (di_spread or 0) > 5 else (RED if (di_spread or 0) < -5 else RESET)
    di_str = f"{di_spread:+.1f}" if di_spread is not None else "N/A"
    print(f"  DI Spread:    {di_color}{di_str:>20s}{RESET}  (+DI - -DI)")

    # Supertrend
    st_color = GREEN if supertrend_dir == "Up" else RED
    print(f"  Supertrend:   {st_color}{supertrend_dir:>20s}{RESET}")

    # EMA Alignment
    ema_color = GREEN if ema_alignment == "정배열" else (RED if ema_alignment == "역배열" else DIM)
    print(f"  EMA 정렬:     {ema_color}{ema_alignment:>20s}{RESET}")

    # Price vs EMA200
    if price_vs_ema200 is not None:
        e200_color = GREEN if price_vs_ema200 > 0 else RED
        print(f"  vs EMA200:    {e200_color}{price_vs_ema200:>+19.1f}%{RESET}")
    else:
        print(f"  vs EMA200:    {DIM}{'N/A':>20s}{RESET}")

    # BB Position
    if bb_pos is not None:
        bb_color = RED if bb_pos >= 80 else (GREEN if bb_pos <= 20 else RESET)
        print(f"  BB 위치(%):   {bb_color}{bb_pos:>19.1f}%{RESET}  {_bar(bb_pos)}")
    else:
        print(f"  BB 위치(%):   {DIM}{'N/A':>20s}{RESET}")

    # Volume Ratio
    if vol_ratio is not None:
        vr_color = GREEN if vol_ratio >= 1.5 else (DIM if vol_ratio < 0.7 else RESET)
        print(f"  Vol Ratio:    {vr_color}{vol_ratio:>19.2f}x{RESET}  (vs 20일 평균)")
    else:
        print(f"  Vol Ratio:    {DIM}{'N/A':>20s}{RESET}")


def print_historical(ticker: str) -> None:
    """Print 2026-02-28 snapshot vs actual outcome."""
    row = _hist_record(ticker)
    if row is None:
        print(f"\n{DIM}  ※ 과거 스냅샷 없음 (S&P 500 외 종목){RESET}")
        return

    print(f"\n{CYAN}── 과거 스냅샷 (2026-02-28) vs 실제 결과 ──────{RESET}")

    actual = row.get("actual_dir", "?")
    actual_color = GREEN if actual == "상승" else RED
    ret5 = row.get("ret_5d")
    ret20 = row.get("ret_20d")
    ret60 = row.get("ret_60d")

    ret_str = ""
    if isinstance(ret5, float):
        ret_str = (f"  (5d: {_color_val(ret5)}%,"
                   f" 20d: {_color_val(ret20)}%,"
                   f" 60d: {_color_val(ret60)}%)")
    print(f"  실제 5일 방향:  {actual_color}{BOLD}{actual}{RESET}{ret_str}")

    indicators_snapshot = {
        "RSI > 50":       ("rsi", lambda v: v > 50, f"{row.get('rsi', 0):.1f}"),
        "MACD Bullish":   ("macd_bullish", lambda v: v, str(row.get("macd_bullish", False))),
        "Supertrend Up":  ("st_dir", lambda v: v == 1, "Up" if row.get("st_dir") == 1 else "Down"),
        "EMA 정배열":     ("ema_align", lambda v: v == "정배열", str(row.get("ema_align", "?"))),
        "Price > EMA200": ("price_vs_ema200", lambda v: v > 0, f"{row.get('price_vs_ema200', 0):+.1f}%"),
        "ADX > 25":       ("adx", lambda v: v > 25, f"{row.get('adx', 0):.1f}"),
        "DI Spread > 0":  ("di_spread", lambda v: v > 0, f"{row.get('di_spread', 0):+.1f}"),
        "BB Pos > 50":    ("bb_pos", lambda v: v > 50, f"{row.get('bb_pos', 0):.1f}%"),
        "Vol Ratio > 1":  ("vol_ratio", lambda v: v > 1, f"{row.get('vol_ratio', 0):.2f}x"),
    }

    print(f"\n  {'지표':20s} {'스냅샷값':>12s}  {'신호':>8s}  {'맞음?':>6s}")
    print(f"  {'-'*52}")
    correct = 0
    total = 0
    for label, (col, pred_fn, val_str) in indicators_snapshot.items():
        raw = row.get(col)
        if raw is None or (isinstance(raw, float) and np.isnan(raw)):
            continue
        predicted_up = pred_fn(raw)
        actually_up = actual == "상승"
        hit = predicted_up == actually_up
        hit_str = f"{GREEN}✓{RESET}" if hit else f"{RED}✗{RESET}"
        sig_str = f"{GREEN}상승↑{RESET}" if predicted_up else f"{RED}하락↓{RESET}"
        total += 1
        if hit:
            correct += 1
        print(f"  {label:20s} {val_str:>12s}  {sig_str}  {hit_str}")

    if total:
        acc = correct / total * 100
        acc_color = GREEN if acc >= 70 else (RED if acc < 50 else YELLOW)
        print(f"\n  → 이 종목 예측 정확도: {acc_color}{BOLD}{correct}/{total} ({acc:.0f}%){RESET}")


def print_s500_accuracy() -> None:
    """Print S&P 500 전체 지표별 5일 예측 정확도."""
    if not HIST_CSV.exists():
        return
    df = pd.read_csv(HIST_CSV)
    acc = _accuracy_summary(df)
    print(f"\n{CYAN}── S&P 500 전체 지표 예측 정확도 (2026-02-28 스냅샷) ─{RESET}")
    print(f"  {'지표':22s} {'정확도':>8s}  {'신호 발생':>10s}  {'전체 비중':>8s}")
    print(f"  {'-'*54}")
    for label, d in sorted(acc.items(), key=lambda x: -x[1]["acc"]):
        acc_color = GREEN if d["acc"] >= 60 else (RED if d["acc"] < 50 else YELLOW)
        print(f"  {label:22s} {acc_color}{d['acc']:>7.1f}%{RESET}  {d['n']:>10d}  {d['pct_of_total']:>7.1f}%")


def print_signal_agreement(row: pd.Series | None, rsi: float, macd_signal: str,
                            supertrend_dir: str, ema_alignment: str,
                            price_vs_ema200: float | None, adx: float | None,
                            di_spread: float | None) -> None:
    """Show signal agreement/disagreement matrix."""
    signals = {
        "RSI > 50":       rsi > 50 if rsi else None,
        "MACD Bullish":   macd_signal == "Bullish",
        "Supertrend Up":  supertrend_dir == "Up",
        "EMA 정배열":     ema_alignment == "정배열",
        "Price > EMA200": (price_vs_ema200 or 0) > 0,
        "ADX > 25":       (adx or 0) > 25,
        "DI Spread > 0":  (di_spread or 0) > 0,
    }
    bulls = sum(1 for v in signals.values() if v is True)
    bears = sum(1 for v in signals.values() if v is False)
    total = bulls + bears
    print(f"\n{CYAN}── 신호 일치도 ────────────────────────────────{RESET}")
    print(f"  상승 신호: {GREEN}{bulls}/{total}{RESET}  |  하락 신호: {RED}{bears}/{total}{RESET}")
    bull_pct = bulls / total * 100 if total else 0
    print(f"  {_bar(bull_pct)} {bull_pct:.0f}% 상승 우세" if bull_pct >= 50
          else f"  {_bar(bull_pct)} {100-bull_pct:.0f}% 하락 우세")

    # Conflicting signals
    conflicts = []
    if (macd_signal == "Bullish") != (supertrend_dir == "Up"):
        conflicts.append("MACD ↔ Supertrend 충돌")
    if rsi and ((rsi > 50) != (ema_alignment == "정배열")):
        conflicts.append("RSI ↔ EMA 정렬 충돌")
    if adx and adx < 20 and abs(di_spread or 0) > 10:
        conflicts.append("ADX 약세이나 DI 벌어짐")
    if conflicts:
        print(f"  {YELLOW}⚠ 충돌: {', '.join(conflicts)}{RESET}")


def analyze(ticker: str, period: str = "1y", show_history: bool = True,
             show_s500: bool = True) -> None:
    ticker = ticker.upper()
    print(f"\n  Fetching {ticker}...", end=" ", flush=True)

    df, yf_ticker = _fetch_ohlcv(ticker, period)
    if df.empty:
        print(f"{RED}데이터 없음{RESET}")
        return

    info = yf_ticker.info
    name = info.get("shortName") or info.get("longName") or ticker
    sector = info.get("sector") or "N/A"
    market_cap = info.get("marketCap")
    print("OK")

    price = float(df["Close"].iloc[-1])

    # Returns
    def _ret(n: int) -> float | None:
        return round((price / float(df["Close"].iloc[-n]) - 1) * 100, 2) if len(df) > n else None

    d1, w1, m1, m3 = _ret(2), _ret(6), _ret(22), _ret(65)

    # Technical analysis
    ta = TechnicalAnalyzer()
    tech_result = ta.analyze(ticker, ohlcv=df)
    tech_score = tech_result["score"]
    indicators = tech_result.get("indicators", {})

    macd_val = indicators.get("macd")
    macd_sig_val = indicators.get("macd_signal")
    macd_signal = "Bullish" if (macd_val and macd_sig_val and macd_val > macd_sig_val) else "Bearish"

    trend = compute_trend_strength(ticker, name, df)
    ema_alignment = trend.get("ema_alignment", "N/A")
    ema_200_slope = trend.get("ema_200_slope")
    macd_histogram = indicators.get("macd_histogram")
    adx_change_5d = trend.get("adx_change_5d")
    rsi = trend.get("rsi")
    adx = trend.get("adx")
    di_spread = None
    if "plus_di" in trend and "minus_di" in trend:
        p, m = trend.get("plus_di"), trend.get("minus_di")
        if p is not None and m is not None:
            di_spread = round(float(p) - float(m), 2)

    # BB position
    bb_pos = None
    if "Close" in df.columns and len(df) >= 20:
        try:
            bb_df = _bbands(df["Close"], length=20, std_dev=2)
            upper = float(bb_df["upper"].iloc[-1])
            lower = float(bb_df["lower"].iloc[-1])
            if upper != lower:
                bb_pos = round((price - lower) / (upper - lower) * 100, 1)
        except Exception:
            pass

    # Vol ratio
    vol_ratio = None
    if "Volume" in df.columns and len(df) >= 20:
        vol_20_avg = df["Volume"].rolling(20).mean().iloc[-1]
        if vol_20_avg and vol_20_avg > 0:
            vol_ratio = round(float(df["Volume"].iloc[-1]) / float(vol_20_avg), 2)

    # BB width rank
    bb_width_rank = None
    if "Close" in df.columns and len(df) >= 20:
        try:
            bb_df2 = _bbands(df["Close"], length=20, std_dev=2)
            bb_width = bb_df2["upper"] - bb_df2["lower"]
            bb_valid = bb_width.dropna()
            lookback = min(120, len(bb_valid))
            if lookback >= 20:
                recent = bb_valid.iloc[-lookback:]
                current_w = float(recent.iloc[-1])
                bb_width_rank = round(float((recent < current_w).sum()) / len(recent) * 100, 1)
        except Exception:
            pass

    pattern_result = classify_stock_pattern(
        trend_regime=trend.get("trend_regime", "N/A"),
        ema_alignment=ema_alignment,
        supertrend_dir=trend.get("supertrend_direction", "N/A"),
        macd_signal=macd_signal,
        rsi=rsi,
        adx=adx,
        adx_change_5d=adx_change_5d,
        change_1w=w1,
        price_vs_ema200=trend.get("price_vs_ema200"),
        ema_200_slope=ema_200_slope,
        vol_ratio=vol_ratio,
        bb_width_rank=bb_width_rank,
        macd_histogram=macd_histogram,
        price=price,
    )

    # ── Print ──────────────────────────────────────────────────────────────
    print_header(ticker, name, sector, market_cap)
    print_price_section(price, d1, w1, m1, m3)
    print_indicators(
        tech_score=tech_score,
        rsi=rsi,
        rsi_state=trend.get("rsi_state", "N/A"),
        macd_signal=macd_signal,
        adx=adx,
        adx_trend=trend.get("adx_trend", "N/A"),
        di_spread=di_spread,
        supertrend_dir=trend.get("supertrend_direction", "N/A"),
        ema_alignment=ema_alignment,
        price_vs_ema200=trend.get("price_vs_ema200"),
        bb_pos=bb_pos,
        vol_ratio=vol_ratio,
        trend_regime=trend.get("trend_regime", "N/A"),
        pattern=pattern_result["pattern"],
        pattern_kr=pattern_result["pattern_kr"],
        pattern_score=pattern_result["pattern_score"],
    )
    print_signal_agreement(
        row=None, rsi=rsi or 50, macd_signal=macd_signal,
        supertrend_dir=trend.get("supertrend_direction", "N/A"),
        ema_alignment=ema_alignment,
        price_vs_ema200=trend.get("price_vs_ema200"),
        adx=adx, di_spread=di_spread,
    )
    if show_history:
        print_historical(ticker)
    if show_s500:
        print_s500_accuracy()

    print(f"\n{BOLD}{'═' * 62}{RESET}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="종목별 지표 공부 스크립트")
    parser.add_argument("ticker", help="분석할 종목 (예: NVDA)")
    parser.add_argument("--period", default="1y", help="데이터 기간 (기본: 1y)")
    parser.add_argument("--no-history", action="store_true", help="과거 스냅샷 비교 생략")
    parser.add_argument("--no-s500", action="store_true", help="S&P 500 전체 통계 생략")
    args = parser.parse_args()

    analyze(
        ticker=args.ticker,
        period=args.period,
        show_history=not args.no_history,
        show_s500=not args.no_s500,
    )


if __name__ == "__main__":
    main()
