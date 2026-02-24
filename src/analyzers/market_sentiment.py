"""Market sentiment analysis: custom Fear/Greed index and market diagnosis."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.analyzers.technical import _rsi
from src.analyzers.trend import _adx, _supertrend


def _score_to_level(score: float) -> str:
    """Map a 0-100 score to a human-readable fear/greed level.

    Args:
        score: Fear & Greed score (0-100).

    Returns:
        Level label string.
    """
    if score >= 80:
        return "Extreme Greed"
    if score >= 60:
        return "Greed"
    if score >= 40:
        return "Neutral"
    if score >= 20:
        return "Fear"
    return "Extreme Fear"


def _compute_vix_score(vix_value: float) -> tuple[float, float]:
    """Compute VIX component score.

    Args:
        vix_value: Current VIX level.

    Returns:
        Tuple of (vix_value, score 0-100).
    """
    score = max(0, min(100, 100 - (vix_value - 10) * (90 / 30)))
    return vix_value, round(score, 1)


def _compute_rsi_score(index_data: dict[str, pd.DataFrame]) -> tuple[float, float]:
    """Compute average RSI component score.

    Args:
        index_data: Dict of index_ticker -> OHLCV DataFrame.

    Returns:
        Tuple of (avg_rsi, score 0-100).
    """
    rsi_values: list[float] = []
    for df in index_data.values():
        if len(df) >= 20 and "Close" in df.columns:
            rsi_series = _rsi(df["Close"], 14)
            last_rsi = rsi_series.dropna()
            if not last_rsi.empty:
                rsi_values.append(float(last_rsi.iloc[-1]))

    if rsi_values:
        avg_rsi = sum(rsi_values) / len(rsi_values)
        score = max(0, min(100, avg_rsi))
    else:
        avg_rsi = 50.0
        score = 50.0
    return round(avg_rsi, 1), round(score, 1)


def _compute_momentum_score(index_data: dict[str, pd.DataFrame]) -> tuple[float, float]:
    """Compute 20-day momentum component score.

    Args:
        index_data: Dict of index_ticker -> OHLCV DataFrame.

    Returns:
        Tuple of (avg_momentum_pct, score 0-100).
    """
    momentum_values: list[float] = []
    for df in index_data.values():
        if len(df) >= 20 and "Close" in df.columns:
            close = df["Close"]
            ret_20d = (float(close.iloc[-1]) / float(close.iloc[-20]) - 1) * 100
            momentum_values.append(ret_20d)

    if momentum_values:
        avg_momentum = sum(momentum_values) / len(momentum_values)
        score = max(0, min(100, 50 + avg_momentum * 4))
    else:
        avg_momentum = 0.0
        score = 50.0
    return round(avg_momentum, 2), round(score, 1)


def _compute_putcall_score(
    putcall_data: list[dict[str, Any]] | None,
) -> tuple[float, float] | None:
    """Compute Put/Call ratio component score.

    Args:
        putcall_data: List of put/call ratio dicts from PutCallRatioCollector.

    Returns:
        Tuple of (equity_pc_ratio, score 0-100) or None if unavailable.
    """
    if not putcall_data:
        return None

    # Prefer equity put/call ratio (most relevant for sentiment)
    equity_data = next((d for d in putcall_data if d["type"] == "equity"), None)
    if not equity_data:
        equity_data = putcall_data[0]

    ratio = equity_data["pc_ratio"]
    # Map: ratio 1.2 → 10 (fear), ratio 0.7 → 50 (neutral), ratio 0.3 → 90 (greed)
    score = max(0, min(100, 100 - (ratio - 0.3) * (90 / 0.9)))
    return round(ratio, 4), round(score, 1)


def _compute_aaii_score(
    aaii_data: list[dict[str, Any]] | None,
) -> tuple[float, float] | None:
    """Compute AAII sentiment survey component score.

    Args:
        aaii_data: List of AAII survey dicts from AAIISentimentCollector.

    Returns:
        Tuple of (bull_bear_spread, score 0-100) or None if unavailable.
    """
    if not aaii_data:
        return None

    latest = aaii_data[0]
    spread = latest.get("bull_bear_spread", 0)
    # Map: spread -30 → 10, spread 0 → 50, spread +30 → 90
    score = max(0, min(100, 50 + spread * (40 / 30)))
    return round(spread, 1), round(score, 1)


def _compute_community_score(
    community_data: list[dict[str, Any]] | None,
) -> tuple[float, float] | None:
    """Compute community sentiment component score.

    Aggregates bullish ratios from Naver or StockTwits data.

    Args:
        community_data: List of per-stock community sentiment dicts.

    Returns:
        Tuple of (avg_bullish_ratio, score 0-100) or None if unavailable.
    """
    if not community_data:
        return None

    ratios: list[float] = []
    for item in community_data:
        # Naver uses "bullish_ratio", StockTwits uses "sentiment_score"
        ratio = item.get("bullish_ratio") or item.get("sentiment_score")
        if ratio is not None:
            ratios.append(float(ratio))

    if not ratios:
        return None

    avg_ratio = sum(ratios) / len(ratios)
    # Map: 0.0 → 0, 0.5 → 50, 1.0 → 100
    score = max(0, min(100, avg_ratio * 100))
    return round(avg_ratio, 3), round(score, 1)


def compute_fear_greed(
    vix_value: float,
    index_data: dict[str, pd.DataFrame],
    *,
    putcall_data: list[dict[str, Any]] | None = None,
    aaii_data: list[dict[str, Any]] | None = None,
    community_data: list[dict[str, Any]] | None = None,
    cnn_fear_greed: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compute a custom Fear/Greed index (0=Extreme Fear, 100=Extreme Greed).

    Base components (always available):
        1. VIX: inversely mapped (VIX 10→90, VIX 40→10)
        2. Average RSI: mean RSI across all indices
        3. Market momentum: average 20-day return across indices

    Optional components (when external data is provided):
        4. Put/Call Ratio: CBOE equity put/call ratio
        5. AAII Sentiment: bull-bear spread from weekly survey
        6. Community Sentiment: aggregate from Naver/StockTwits

    CNN Fear & Greed is included as a reference but does NOT
    affect the custom score calculation.

    Weights are dynamically adjusted based on available components.

    Args:
        vix_value: Current VIX level.
        index_data: Dict of index_ticker -> OHLCV DataFrame.
        putcall_data: Optional CBOE put/call ratio data.
        aaii_data: Optional AAII sentiment survey data.
        community_data: Optional community sentiment data.
        cnn_fear_greed: Optional CNN Fear & Greed data (reference only).

    Returns:
        Dict with fear_greed score, level label, and component breakdown.
    """
    # === Base components (always computed) ===
    vix_val, vix_score = _compute_vix_score(vix_value)
    rsi_val, rsi_score = _compute_rsi_score(index_data)
    momentum_val, momentum_score = _compute_momentum_score(index_data)

    # Base weights
    components: dict[str, dict[str, Any]] = {
        "vix": {"value": vix_val, "score": vix_score, "weight": 0.25},
        "rsi": {"value": rsi_val, "score": rsi_score, "weight": 0.20},
        "momentum": {"value": momentum_val, "score": momentum_score, "weight": 0.15},
    }
    remaining_weight = 0.40  # to distribute among optional components

    # === Optional components ===
    optional_count = 0

    putcall_result = _compute_putcall_score(putcall_data)
    if putcall_result:
        optional_count += 1

    aaii_result = _compute_aaii_score(aaii_data)
    if aaii_result:
        optional_count += 1

    community_result = _compute_community_score(community_data)
    if community_result:
        optional_count += 1

    if optional_count > 0:
        per_optional = remaining_weight / optional_count

        if putcall_result:
            components["putcall"] = {
                "value": putcall_result[0],
                "score": putcall_result[1],
                "weight": per_optional,
            }

        if aaii_result:
            components["aaii"] = {
                "value": aaii_result[0],
                "score": aaii_result[1],
                "weight": per_optional,
            }

        if community_result:
            components["community"] = {
                "value": community_result[0],
                "score": community_result[1],
                "weight": per_optional,
            }
    else:
        # No optional data — redistribute to base components
        components["vix"]["weight"] = 0.40
        components["rsi"]["weight"] = 0.30
        components["momentum"]["weight"] = 0.30

    # === Weighted score ===
    fear_greed = sum(
        c["score"] * c["weight"] for c in components.values()
    )
    fear_greed = round(max(0, min(100, fear_greed)), 1)

    result: dict[str, Any] = {
        "score": fear_greed,
        "level": _score_to_level(fear_greed),
        "components": components,
    }

    # CNN Fear & Greed as reference (not in score calculation)
    if cnn_fear_greed:
        cnn = cnn_fear_greed[0]
        result["cnn_reference"] = {
            "score": cnn.get("score"),
            "level": cnn.get("level"),
            "source": cnn.get("source", "cnn"),
        }

    return result


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
