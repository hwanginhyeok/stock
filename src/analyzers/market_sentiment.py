"""Market sentiment analysis: custom Fear/Greed index and market diagnosis."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.analyzers.technical import _rsi
from src.analyzers.trend import _adx, _supertrend


def compute_fear_greed(
    vix_value: float,
    index_data: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """Compute a custom Fear/Greed index (0=Extreme Fear, 100=Extreme Greed).

    Components (equal weight):
        1. VIX component: inversely mapped (VIX 10→90, VIX 40→10)
        2. Average RSI component: mean RSI across all indices
        3. Market momentum: average 20-day return across indices

    Args:
        vix_value: Current VIX level.
        index_data: Dict of index_ticker -> OHLCV DataFrame.

    Returns:
        Dict with fear_greed score, level label, and component breakdown.
    """
    # VIX component (inverted: low VIX = greed, high VIX = fear)
    vix_score = max(0, min(100, 100 - (vix_value - 10) * (90 / 30)))

    # RSI component (mean RSI mapped: RSI 30→20, RSI 50→50, RSI 70→80)
    rsi_values: list[float] = []
    for df in index_data.values():
        if len(df) >= 20 and "Close" in df.columns:
            rsi_series = _rsi(df["Close"], 14)
            last_rsi = rsi_series.dropna()
            if not last_rsi.empty:
                rsi_values.append(float(last_rsi.iloc[-1]))

    if rsi_values:
        avg_rsi = sum(rsi_values) / len(rsi_values)
        rsi_score = max(0, min(100, avg_rsi))
    else:
        avg_rsi = 50.0
        rsi_score = 50.0

    # Momentum component (20-day return average)
    momentum_values: list[float] = []
    for df in index_data.values():
        if len(df) >= 20 and "Close" in df.columns:
            close = df["Close"]
            ret_20d = (float(close.iloc[-1]) / float(close.iloc[-20]) - 1) * 100
            momentum_values.append(ret_20d)

    if momentum_values:
        avg_momentum = sum(momentum_values) / len(momentum_values)
        # Map: -10% → 10, 0% → 50, +10% → 90
        momentum_score = max(0, min(100, 50 + avg_momentum * 4))
    else:
        avg_momentum = 0.0
        momentum_score = 50.0

    # Weighted average
    fear_greed = (vix_score * 0.4 + rsi_score * 0.3 + momentum_score * 0.3)
    fear_greed = round(max(0, min(100, fear_greed)), 1)

    # Level label
    if fear_greed >= 80:
        level = "Extreme Greed"
    elif fear_greed >= 60:
        level = "Greed"
    elif fear_greed >= 40:
        level = "Neutral"
    elif fear_greed >= 20:
        level = "Fear"
    else:
        level = "Extreme Fear"

    return {
        "score": fear_greed,
        "level": level,
        "components": {
            "vix": {"value": vix_value, "score": round(vix_score, 1)},
            "rsi": {"value": round(avg_rsi, 1), "score": round(rsi_score, 1)},
            "momentum": {"value": round(avg_momentum, 2), "score": round(momentum_score, 1)},
        },
    }


def compute_trend_strength(
    ticker: str,
    name: str,
    df: pd.DataFrame,
) -> dict[str, Any]:
    """Compute trend strength summary for a single index/stock.

    Args:
        ticker: Ticker symbol.
        name: Display name.
        df: OHLCV DataFrame.

    Returns:
        Dict with ADX, Supertrend direction, RSI state.
    """
    result: dict[str, Any] = {
        "ticker": ticker,
        "name": name,
        "adx": None,
        "adx_trend": "N/A",
        "supertrend_direction": "N/A",
        "rsi": None,
        "rsi_state": "N/A",
    }

    if len(df) < 30 or "Close" not in df.columns:
        return result

    # ADX
    if all(c in df.columns for c in ("High", "Low", "Close")):
        adx_df = _adx(df)
        adx_last = adx_df["ADX"].dropna()
        if not adx_last.empty:
            adx_val = float(adx_last.iloc[-1])
            result["adx"] = round(adx_val, 1)
            if adx_val >= 25:
                result["adx_trend"] = "Strong"
            elif adx_val >= 20:
                result["adx_trend"] = "Moderate"
            else:
                result["adx_trend"] = "Weak"

        # Supertrend
        st_df = _supertrend(df)
        st_dir = st_df["direction"].dropna()
        if not st_dir.empty:
            direction = int(st_dir.iloc[-1])
            result["supertrend_direction"] = "Bullish" if direction == 1 else "Bearish"

    # RSI
    rsi_series = _rsi(df["Close"], 14)
    rsi_last = rsi_series.dropna()
    if not rsi_last.empty:
        rsi_val = float(rsi_last.iloc[-1])
        result["rsi"] = round(rsi_val, 1)
        if rsi_val >= 70:
            result["rsi_state"] = "Overbought"
        elif rsi_val <= 30:
            result["rsi_state"] = "Oversold"
        else:
            result["rsi_state"] = "Neutral"

    return result


def market_diagnosis(
    fear_greed: dict[str, Any],
    trend_data: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate overall market diagnosis.

    Args:
        fear_greed: Fear/Greed index result.
        trend_data: List of trend strength dicts for each index.

    Returns:
        Dict with verdict, description, and detail factors.
    """
    fg_score = fear_greed["score"]

    # Count bullish/bearish signals
    bullish = 0
    bearish = 0
    for t in trend_data:
        if t["supertrend_direction"] == "Bullish":
            bullish += 1
        elif t["supertrend_direction"] == "Bearish":
            bearish += 1

        if t["rsi_state"] == "Overbought":
            bearish += 0.5
        elif t["rsi_state"] == "Oversold":
            bullish += 0.5

    # Combine signals
    net = bullish - bearish
    total = len(trend_data) if trend_data else 1

    if fg_score >= 60 and net > 0:
        verdict = "Bullish"
        description = "시장 전반적으로 강세 흐름이 유지되고 있습니다. Fear/Greed 지수가 탐욕 구간에 위치하며, 주요 지수의 추세 지표도 상승을 지지합니다."
    elif fg_score <= 40 and net < 0:
        verdict = "Bearish"
        description = "시장 전반적으로 약세 흐름이 감지됩니다. Fear/Greed 지수가 공포 구간에 위치하며, 주요 지수의 추세가 하락 방향을 가리킵니다."
    elif fg_score >= 80:
        verdict = "Caution (Overbought)"
        description = "시장이 과열 구간에 진입했습니다. 극도의 탐욕은 조정의 전조가 될 수 있으므로 주의가 필요합니다."
    elif fg_score <= 20:
        verdict = "Opportunity (Oversold)"
        description = "시장이 극도의 공포 상태입니다. 역사적으로 이 구간은 장기 투자자에게 기회가 될 수 있습니다."
    else:
        verdict = "Neutral"
        description = "시장이 뚜렷한 방향성 없이 횡보하고 있습니다. 강세와 약세 신호가 혼재하며, 추가 확인이 필요합니다."

    return {
        "verdict": verdict,
        "description": description,
        "fear_greed_score": fg_score,
        "bullish_signals": bullish,
        "bearish_signals": bearish,
        "net_signal": round(net, 1),
    }
