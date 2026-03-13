"""Trend indicators: ADX, Supertrend, ATR, Trend Regime — pure pandas implementation."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.analyzers.technical import _ema


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range.

    Args:
        df: DataFrame with High, Low, Close columns.
        period: ATR lookback period.

    Returns:
        ATR as a pandas Series.
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)

    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def _adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Average Directional Index with +DI and -DI.

    Args:
        df: DataFrame with High, Low, Close columns.
        period: ADX lookback period.

    Returns:
        DataFrame with columns: ADX, plus_di, minus_di.
    """
    high = df["High"]
    low = df["Low"]

    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
        index=df.index,
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
        index=df.index,
    )

    atr = _atr(df, period)

    smooth_plus_dm = plus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    smooth_minus_dm = minus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    plus_di = 100 * smooth_plus_dm / atr.replace(0, np.nan)
    minus_di = 100 * smooth_minus_dm / atr.replace(0, np.nan)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    return pd.DataFrame({
        "ADX": adx,
        "plus_di": plus_di,
        "minus_di": minus_di,
    })


def _supertrend(
    df: pd.DataFrame,
    period: int = 10,
    multiplier: float = 3.0,
) -> pd.DataFrame:
    """Supertrend indicator.

    Args:
        df: DataFrame with High, Low, Close columns.
        period: ATR period for Supertrend.
        multiplier: ATR multiplier.

    Returns:
        DataFrame with columns: supertrend, direction (1=up, -1=down).
    """
    atr = _atr(df, period)
    hl2 = (df["High"] + df["Low"]) / 2
    close = df["Close"]

    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr

    supertrend = pd.Series(np.nan, index=df.index)
    direction = pd.Series(1, index=df.index, dtype=int)

    for i in range(1, len(df)):
        if pd.isna(upper_band.iloc[i]) or pd.isna(lower_band.iloc[i]):
            continue

        # Adjust bands
        if lower_band.iloc[i] > lower_band.iloc[i - 1] or close.iloc[i - 1] < lower_band.iloc[i - 1]:
            pass
        else:
            lower_band.iloc[i] = lower_band.iloc[i - 1]

        if upper_band.iloc[i] < upper_band.iloc[i - 1] or close.iloc[i - 1] > upper_band.iloc[i - 1]:
            pass
        else:
            upper_band.iloc[i] = upper_band.iloc[i - 1]

        # Direction
        prev_st = supertrend.iloc[i - 1]
        if pd.isna(prev_st):
            if close.iloc[i] > upper_band.iloc[i]:
                direction.iloc[i] = 1
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                direction.iloc[i] = -1
                supertrend.iloc[i] = upper_band.iloc[i]
        elif prev_st == upper_band.iloc[i - 1]:
            if close.iloc[i] > upper_band.iloc[i]:
                direction.iloc[i] = 1
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                direction.iloc[i] = -1
                supertrend.iloc[i] = upper_band.iloc[i]
        else:
            if close.iloc[i] < lower_band.iloc[i]:
                direction.iloc[i] = -1
                supertrend.iloc[i] = upper_band.iloc[i]
            else:
                direction.iloc[i] = 1
                supertrend.iloc[i] = lower_band.iloc[i]

    return pd.DataFrame({
        "supertrend": supertrend,
        "direction": direction,
    })


# ============================================================
# Trend Regime Classification (ADX + EMA 20/50/200)
# ============================================================

_REGIME_MAP = {
    "Strong Uptrend": "강한 상승",
    "Uptrend": "상승",
    "Sideways": "횡보",
    "Downtrend": "하락",
    "Strong Downtrend": "강한 하락",
    "Transition": "전환",
}

_PATTERN_KR = {
    "Breakout": "돌파",
    "Pullback": "눌림목",
    "Consolidation": "횡보 수렴",
}


def classify_stock_pattern(
    trend_regime: str,
    ema_alignment: str,
    supertrend_dir: str,
    macd_signal: str,
    rsi: float | None,
    adx: float | None,
    adx_change_5d: float | None,
    change_1w: float | None,
    price_vs_ema200: float | None,
    ema_200_slope: float | None,
    vol_ratio: float | None,
    bb_width_rank: float | None,
    macd_histogram: float | None,
    price: float | None = None,
) -> dict[str, Any]:
    """Classify a stock into Breakout / Pullback / Consolidation pattern.

    Each pattern checks 5 conditions; ≥ 3 matches triggers classification.
    Priority: Breakout > Pullback > Consolidation.

    Pullback requires at least one bullish gate condition (trend bullish
    OR supertrend Bullish) to prevent Sideways+Bearish stocks from
    being misclassified as pullbacks.

    Consolidation MACD flatness uses price-relative threshold (0.3% of
    price) instead of an absolute value, ensuring fair comparison across
    different price levels.

    Args:
        trend_regime: Trend regime label (e.g. "Strong Uptrend").
        ema_alignment: EMA alignment ("정배열" / "역배열" / "혼재").
        supertrend_dir: Supertrend direction ("Bullish" / "Bearish").
        macd_signal: MACD signal ("Bullish" / "Bearish").
        rsi: RSI value (0-100) or None.
        adx: Current ADX value or None.
        adx_change_5d: ADX 5-day change or None.
        change_1w: 1-week price change (%) or None.
        price_vs_ema200: Distance from EMA 200 (%) or None.
        ema_200_slope: EMA 200 10-day slope (%) or None.
        vol_ratio: Volume ratio (current / 20-day avg) or None.
        bb_width_rank: Bollinger Band width percentile (0-100) or None.
        macd_histogram: MACD histogram value or None.
        price: Current stock price for MACD normalization or None.

    Returns:
        Dict with pattern, pattern_kr, pattern_score, pattern_signals.
    """
    no_pattern: dict[str, Any] = {
        "pattern": "—",
        "pattern_kr": "—",
        "pattern_score": 0,
        "pattern_signals": [],
    }

    # --- Breakout: low-base breakout with volume surge ---
    bo_signals: list[str] = []
    if adx_change_5d is not None and adx_change_5d > 3:
        bo_signals.append("ADX rising (+{:.1f})".format(adx_change_5d))
    if vol_ratio is not None and vol_ratio > 1.5:
        bo_signals.append("Volume surge ({:.1f}x)".format(vol_ratio))
    if macd_signal == "Bullish":
        bo_signals.append("MACD Bullish")
    if supertrend_dir == "Bullish":
        bo_signals.append("ST Bullish")
    if price_vs_ema200 is not None and price_vs_ema200 > 0:
        bo_signals.append("Above EMA200")

    if len(bo_signals) >= 3:
        return {
            "pattern": "Breakout",
            "pattern_kr": _PATTERN_KR["Breakout"],
            "pattern_score": len(bo_signals),
            "pattern_signals": bo_signals,
        }

    # --- Pullback: temporary dip in strong uptrend ---
    # Gate: at least trend must be bullish OR supertrend must be Bullish.
    # Without this, Sideways + Bearish ST stocks could falsely qualify.
    has_bullish_trend = trend_regime in ("Strong Uptrend", "Uptrend")
    has_bullish_st = supertrend_dir == "Bullish"

    if has_bullish_trend or has_bullish_st:
        pb_signals: list[str] = []
        if has_bullish_trend:
            pb_signals.append("Trend: {}".format(trend_regime))
        if ema_alignment == "정배열":
            pb_signals.append("EMA 정배열")
        if change_1w is not None and change_1w < 0:
            pb_signals.append("1W dip ({:+.1f}%)".format(change_1w))
        if rsi is not None and 35 <= rsi <= 55:
            pb_signals.append("RSI neutral ({:.0f})".format(rsi))
        if has_bullish_st:
            pb_signals.append("ST Bullish")

        if len(pb_signals) >= 3:
            return {
                "pattern": "Pullback",
                "pattern_kr": _PATTERN_KR["Pullback"],
                "pattern_score": len(pb_signals),
                "pattern_signals": pb_signals,
            }

    # --- Consolidation: tight range, awaiting breakout ---
    co_signals: list[str] = []
    if adx is not None and adx < 20:
        co_signals.append("ADX low ({:.0f})".format(adx))
    if bb_width_rank is not None and bb_width_rank < 25:
        co_signals.append("BB squeeze (rank {:.0f})".format(bb_width_rank))
    if vol_ratio is not None and vol_ratio < 0.8:
        co_signals.append("Low volume ({:.1f}x)".format(vol_ratio))
    if (price_vs_ema200 is not None and price_vs_ema200 > 0) or (
        ema_200_slope is not None and ema_200_slope > 0
    ):
        co_signals.append("EMA200 supportive")
    # Price-relative MACD flatness: histogram within 0.3% of price
    if macd_histogram is not None and price is not None and price > 0:
        macd_pct = abs(macd_histogram / price) * 100
        if macd_pct < 0.3:
            co_signals.append("MACD flat ({:.2f}, {:.2f}%)".format(
                macd_histogram, macd_pct))

    if len(co_signals) >= 3:
        return {
            "pattern": "Consolidation",
            "pattern_kr": _PATTERN_KR["Consolidation"],
            "pattern_score": len(co_signals),
            "pattern_signals": co_signals,
        }

    return no_pattern


def classify_trend_regime(
    df: pd.DataFrame,
    adx_period: int = 14,
    ema_periods: list[int] | None = None,
    adx_strong: int = 25,
    adx_weak: int = 20,
) -> dict[str, Any]:
    """Classify trend regime using ADX + EMA alignment.

    Combines ADX strength with EMA 20/50/200 alignment and +DI/-DI
    direction to produce a 5-level trend classification.

    Args:
        df: OHLCV DataFrame with at least High, Low, Close columns.
        adx_period: ADX lookback period.
        ema_periods: EMA periods for alignment check (default [20, 50, 200]).
        adx_strong: ADX threshold for strong trend.
        adx_weak: ADX threshold for weak trend.

    Returns:
        Dict with keys:
            regime: English label (e.g. "Strong Uptrend")
            regime_kr: Korean label (e.g. "강한 상승")
            ema_alignment: "정배열" / "역배열" / "혼재"
            ema_200_slope: 200 EMA 10-day slope (%)
            di_spread: +DI minus -DI
            price_vs_ema200: price distance from EMA 200 (%)
    """
    if ema_periods is None:
        ema_periods = [20, 50, 200]

    result: dict[str, Any] = {
        "regime": "Sideways",
        "regime_kr": "횡보",
        "ema_alignment": "N/A",
        "ema_200_slope": None,
        "di_spread": None,
        "price_vs_ema200": None,
    }

    if len(df) < 30 or not all(c in df.columns for c in ("High", "Low", "Close")):
        return result

    close = df["Close"]

    # --- EMA calculation ---
    ema_values: dict[int, float] = {}
    ema_series: dict[int, pd.Series] = {}
    for p in ema_periods:
        s = _ema(close, p)
        ema_series[p] = s
        valid = s.dropna()
        if not valid.empty:
            ema_values[p] = float(valid.iloc[-1])

    # --- EMA alignment ---
    sorted_periods = sorted(ema_periods)  # [20, 50, 200]
    if all(p in ema_values for p in sorted_periods):
        vals = [ema_values[p] for p in sorted_periods]
        if vals[0] > vals[1] > vals[2]:
            alignment = "정배열"
        elif vals[0] < vals[1] < vals[2]:
            alignment = "역배열"
        else:
            alignment = "혼재"
        result["ema_alignment"] = alignment
    else:
        alignment = "혼재"

    # --- 200 EMA slope (10-day rate of change) ---
    max_period = max(ema_periods)
    if max_period in ema_series:
        ema_long = ema_series[max_period].dropna()
        if len(ema_long) >= 10:
            ema_now = float(ema_long.iloc[-1])
            ema_10d_ago = float(ema_long.iloc[-10])
            if ema_10d_ago != 0:
                slope = (ema_now / ema_10d_ago - 1) * 100
                result["ema_200_slope"] = round(slope, 2)

    # --- Price vs EMA 200 distance ---
    if max_period in ema_values:
        current_price = float(close.iloc[-1])
        ema_long_val = ema_values[max_period]
        if ema_long_val != 0:
            distance = (current_price / ema_long_val - 1) * 100
            result["price_vs_ema200"] = round(distance, 2)

    # --- ADX + DI ---
    adx_df = _adx(df, adx_period)
    adx_last = adx_df["ADX"].dropna()
    plus_di_last = adx_df["plus_di"].dropna()
    minus_di_last = adx_df["minus_di"].dropna()

    if adx_last.empty or plus_di_last.empty or minus_di_last.empty:
        return result

    adx_val = float(adx_last.iloc[-1])
    plus_di = float(plus_di_last.iloc[-1])
    minus_di = float(minus_di_last.iloc[-1])
    di_spread = plus_di - minus_di
    result["di_spread"] = round(di_spread, 2)

    # --- Regime classification ---
    di_bullish = plus_di > minus_di
    ema_bullish = alignment == "정배열"
    ema_bearish = alignment == "역배열"

    if adx_val >= adx_strong:
        if di_bullish and ema_bullish:
            regime = "Strong Uptrend"
        elif not di_bullish and ema_bearish:
            regime = "Strong Downtrend"
        else:
            regime = "Transition"
    elif adx_val >= adx_weak:
        if di_bullish and ema_bullish:
            regime = "Uptrend"
        elif not di_bullish and ema_bearish:
            regime = "Downtrend"
        else:
            regime = "Transition"
    else:
        regime = "Sideways"

    result["regime"] = regime
    result["regime_kr"] = _REGIME_MAP.get(regime, regime)

    return result
