"""SMA 정배열/역배열 + 눌림목 매수 시그널.

1-52: SMA 5/10/20/50 + VWMA100 기반 정배열 감지와
SMA20/50 터치 후 반등 매수 시그널.

trend.py의 EMA 20/50/200 사양과 충돌 없이 공존한다. 호출자가 두 결과를
모두 받아 조합하여 사용한다 (예: 차트 마커, 모멘텀 점수).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

__all__ = [
    "classify_sma_alignment",
    "detect_pullback_buy_signal",
    "sma_series",
    "vwma_series",
]


def sma_series(series: pd.Series, period: int) -> pd.Series:
    """단순 이동평균(SMA) 시리즈."""
    return series.rolling(window=period, min_periods=period).mean()


def vwma_series(df: pd.DataFrame, period: int) -> pd.Series:
    """Volume-Weighted Moving Average 시리즈.

    Args:
        df: OHLCV DataFrame (Close, Volume 컬럼 필수).
        period: 기간.

    Returns:
        VWMA Series. 거래량 합이 0인 구간은 NaN.
    """
    close = df["Close"]
    vol = df["Volume"]
    pv = (close * vol).rolling(window=period, min_periods=period).sum()
    vsum = vol.rolling(window=period, min_periods=period).sum()
    return pv / vsum.replace(0, np.nan)


def classify_sma_alignment(
    df: pd.DataFrame,
    sma_periods: list[int] | None = None,
    vwma_period: int = 100,
) -> dict[str, Any]:
    """SMA 5/10/20/50 + VWMA100 정배열/역배열 판정.

    마지막 봉 기준 다섯 평균선의 대소 관계로 alignment 결정한다.

    - 정배열: SMA5 > SMA10 > SMA20 > SMA50 > VWMA100
    - 역배열: SMA5 < SMA10 < SMA20 < SMA50 < VWMA100
    - 혼재: 그 외

    Args:
        df: OHLCV DataFrame. 최소 vwma_period봉 이상 필요.
        sma_periods: SMA 기간 리스트 (default [5, 10, 20, 50]).
        vwma_period: 마지막선 VWMA 기간 (default 100, 사용자 트레이딩 기준선).

    Returns:
        dict:
            alignment: "정배열" / "역배열" / "혼재" / "N/A"
            values: {"sma_5": ..., "sma_10": ..., ..., "vwma_100": ...}
            last_close: 마지막 종가
            close_vs_vwma_pct: 종가 - VWMA 괴리율 (%)
            chain_ok: 정/역배열 체인 충족 여부 (bool)
    """
    if sma_periods is None:
        sma_periods = [5, 10, 20, 50]

    result: dict[str, Any] = {
        "alignment": "N/A",
        "values": {},
        "last_close": None,
        "close_vs_vwma_pct": None,
        "chain_ok": False,
    }

    if df is None or len(df) < vwma_period:
        return result
    if not all(c in df.columns for c in ("Close", "Volume")):
        return result

    close = df["Close"]
    result["last_close"] = round(float(close.iloc[-1]), 4)

    values: dict[str, float] = {}
    chain: list[float] = []
    for p in sorted(sma_periods):
        s = sma_series(close, p).dropna()
        if s.empty:
            return result
        v = float(s.iloc[-1])
        values[f"sma_{p}"] = round(v, 4)
        chain.append(v)

    vwma = vwma_series(df, vwma_period).dropna()
    if vwma.empty:
        return result
    vwma_v = float(vwma.iloc[-1])
    values[f"vwma_{vwma_period}"] = round(vwma_v, 4)
    chain.append(vwma_v)

    result["values"] = values

    if all(chain[i] > chain[i + 1] for i in range(len(chain) - 1)):
        result["alignment"] = "정배열"
        result["chain_ok"] = True
    elif all(chain[i] < chain[i + 1] for i in range(len(chain) - 1)):
        result["alignment"] = "역배열"
        result["chain_ok"] = True
    else:
        result["alignment"] = "혼재"

    if vwma_v != 0:
        result["close_vs_vwma_pct"] = round((result["last_close"] / vwma_v - 1) * 100, 2)

    return result


def detect_pullback_buy_signal(
    df: pd.DataFrame,
    target_smas: list[int] | None = None,
    lookback: int = 5,
    touch_tolerance: float = 0.005,
    require_alignment: bool = True,
    alignment_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """정배열 상태에서 SMA20/50 터치 후 반등 매수 시그널.

    발동 조건 (모두 충족):
        1. 현재 SMA 정배열 (require_alignment=True 시).
        2. 직전 lookback봉(마지막 봉 제외) 중 한 봉의 저가가 target SMA의
           ±touch_tolerance 범위 내에서 터치.
        3. 마지막 봉의 종가가 그 SMA보다 위.
        4. 마지막 봉이 양봉(Close > Open).

    Args:
        df: OHLCV DataFrame. 최소 max(target_smas) + lookback + 1봉 필요.
        target_smas: 터치 대상 SMA 기간 (default [20, 50]).
        lookback: 터치를 살필 직전 봉 수 (default 5).
        touch_tolerance: 터치 허용 폭 (0.005 = ±0.5%).
        require_alignment: 정배열 필수 여부 (default True).
        alignment_result: 이미 계산한 alignment dict (재계산 회피용).

    Returns:
        dict:
            signal: bool
            touched_sma: "sma_20" / "sma_50" / None
            touch_offset: 마지막 봉으로부터 거꾸로 센 봉 수 (1=직전 봉, 2=두 봉 전, ...)
            touch_low: 터치 봉 저가
            bounce_close: 마지막 봉 종가
            reason: 발동/미발동 사유 (한국어)
    """
    if target_smas is None:
        target_smas = [20, 50]

    result: dict[str, Any] = {
        "signal": False,
        "touched_sma": None,
        "touch_offset": None,
        "touch_low": None,
        "bounce_close": None,
        "reason": "",
    }

    min_required = max(target_smas) + lookback + 1
    if df is None or len(df) < min_required:
        result["reason"] = f"데이터 부족 (최소 {min_required}봉 필요)"
        return result
    if not all(c in df.columns for c in ("Open", "High", "Low", "Close")):
        result["reason"] = "OHLC 컬럼 누락"
        return result

    if require_alignment:
        align = alignment_result if alignment_result is not None else classify_sma_alignment(df)
        if align.get("alignment") != "정배열":
            result["reason"] = f"정배열 아님 ({align.get('alignment')})"
            return result

    close = df["Close"]
    last_open = float(df["Open"].iloc[-1])
    last_close = float(close.iloc[-1])
    result["bounce_close"] = round(last_close, 2)

    if last_close <= last_open:
        result["reason"] = "마지막 봉 음봉/도지 (반등 미확인)"
        return result

    sma_full: dict[int, pd.Series] = {p: sma_series(close, p) for p in target_smas}

    for offset in range(1, lookback + 1):
        idx = -1 - offset
        low_at = float(df["Low"].iloc[idx])

        for p in target_smas:
            sma_at_series = sma_full[p]
            sma_at = float(sma_at_series.iloc[idx])
            if pd.isna(sma_at):
                continue

            lower = sma_at * (1 - touch_tolerance)
            upper = sma_at * (1 + touch_tolerance)
            if lower <= low_at <= upper:
                sma_now = float(sma_at_series.dropna().iloc[-1])
                if last_close > sma_now:
                    result["signal"] = True
                    result["touched_sma"] = f"sma_{p}"
                    result["touch_offset"] = offset
                    result["touch_low"] = round(low_at, 2)
                    result["reason"] = (
                        f"SMA{p} 터치 ({offset}봉 전 저가 ${low_at:.2f}, "
                        f"SMA{p} ${sma_at:.2f}) 후 양봉 반등, "
                        f"종가 ${last_close:.2f} > SMA{p} ${sma_now:.2f}"
                    )
                    return result

    result["reason"] = f"최근 {lookback}봉 SMA{target_smas} 터치 없음"
    return result
