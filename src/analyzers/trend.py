"""Trend indicators: ADX, Supertrend, ATR — pure pandas implementation."""

from __future__ import annotations

import numpy as np
import pandas as pd


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
