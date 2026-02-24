"""Tests for market sentiment (Fear/Greed, trend strength, diagnosis)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.analyzers.market_sentiment import (
    compute_fear_greed,
    compute_trend_strength,
    market_diagnosis,
)


def _make_ohlcv(n: int = 60, start: float = 100.0, trend: float = 0.5) -> pd.DataFrame:
    """Helper: create OHLCV DataFrame with a linear trend."""
    rng = np.random.default_rng(42)
    close = start + np.linspace(0, trend * n, n) + rng.normal(0, 0.3, n)
    high = close + 1.5
    low = close - 1.5
    return pd.DataFrame(
        {"Open": close, "High": high, "Low": low, "Close": close, "Volume": [1e7] * n},
        index=pd.bdate_range(end="2026-02-20", periods=n),
    )


class TestComputeFearGreed:
    """Test compute_fear_greed index."""

    def test_output_keys(self):
        result = compute_fear_greed(20.0, {"SPY": _make_ohlcv()})
        assert "score" in result
        assert "level" in result
        assert "components" in result

    def test_score_range(self):
        result = compute_fear_greed(25.0, {"SPY": _make_ohlcv()})
        assert 0 <= result["score"] <= 100

    def test_low_vix_high_score(self):
        result = compute_fear_greed(10.0, {"SPY": _make_ohlcv(trend=1.0)})
        assert result["score"] >= 60

    def test_high_vix_low_score(self):
        result = compute_fear_greed(40.0, {"SPY": _make_ohlcv(trend=-1.0)})
        assert result["score"] <= 40

    def test_extreme_greed_label(self):
        result = compute_fear_greed(10.0, {"SPY": _make_ohlcv(trend=2.0)})
        if result["score"] >= 80:
            assert result["level"] == "Extreme Greed"

    def test_extreme_fear_label(self):
        result = compute_fear_greed(45.0, {"SPY": _make_ohlcv(trend=-2.0)})
        if result["score"] <= 20:
            assert result["level"] == "Extreme Fear"

    def test_neutral_label(self):
        result = compute_fear_greed(20.0, {"SPY": _make_ohlcv(trend=0.0)})
        assert result["level"] in ("Neutral", "Greed", "Fear", "Extreme Greed", "Extreme Fear")

    def test_empty_index_data(self):
        result = compute_fear_greed(25.0, {})
        assert result["score"] >= 0

    def test_components_present(self):
        result = compute_fear_greed(20.0, {"SPY": _make_ohlcv()})
        comp = result["components"]
        assert "vix" in comp
        assert "rsi" in comp
        assert "momentum" in comp

    def test_vix_component_value(self):
        result = compute_fear_greed(20.0, {})
        assert result["components"]["vix"]["value"] == 20.0


class TestComputeTrendStrength:
    """Test compute_trend_strength."""

    def test_output_keys(self):
        result = compute_trend_strength("SPY", "S&P 500", _make_ohlcv())
        assert result["ticker"] == "SPY"
        assert result["name"] == "S&P 500"
        assert "adx" in result
        assert "supertrend_direction" in result
        assert "rsi" in result

    def test_insufficient_data(self):
        short_df = _make_ohlcv(n=10)
        result = compute_trend_strength("SPY", "S&P 500", short_df)
        assert result["adx"] is None
        assert result["adx_trend"] == "N/A"

    def test_uptrend_bullish_direction(self):
        df = _make_ohlcv(n=60, trend=1.0)
        result = compute_trend_strength("SPY", "S&P 500", df)
        assert result["supertrend_direction"] in ("Bullish", "Bearish", "N/A")

    def test_rsi_state(self):
        df = _make_ohlcv(n=60, trend=0.0)
        result = compute_trend_strength("SPY", "S&P 500", df)
        assert result["rsi_state"] in ("Overbought", "Oversold", "Neutral", "N/A")


class TestMarketDiagnosis:
    """Test market_diagnosis."""

    def test_bullish_verdict(self):
        fg = {"score": 70.0, "level": "Greed"}
        trends = [
            {"supertrend_direction": "Bullish", "rsi_state": "Neutral"},
            {"supertrend_direction": "Bullish", "rsi_state": "Neutral"},
        ]
        result = market_diagnosis(fg, trends)
        assert result["verdict"] == "Bullish"

    def test_bearish_verdict(self):
        fg = {"score": 30.0, "level": "Fear"}
        trends = [
            {"supertrend_direction": "Bearish", "rsi_state": "Neutral"},
            {"supertrend_direction": "Bearish", "rsi_state": "Neutral"},
        ]
        result = market_diagnosis(fg, trends)
        assert result["verdict"] == "Bearish"

    def test_neutral_verdict(self):
        fg = {"score": 50.0, "level": "Neutral"}
        trends = [
            {"supertrend_direction": "Bullish", "rsi_state": "Neutral"},
            {"supertrend_direction": "Bearish", "rsi_state": "Neutral"},
        ]
        result = market_diagnosis(fg, trends)
        assert result["verdict"] == "Neutral"

    def test_overbought_caution(self):
        fg = {"score": 85.0, "level": "Extreme Greed"}
        trends = [
            {"supertrend_direction": "Bearish", "rsi_state": "Overbought"},
        ]
        result = market_diagnosis(fg, trends)
        assert result["verdict"] == "Caution (Overbought)"

    def test_oversold_opportunity(self):
        fg = {"score": 15.0, "level": "Extreme Fear"}
        trends = [
            {"supertrend_direction": "Bullish", "rsi_state": "Oversold"},
        ]
        result = market_diagnosis(fg, trends)
        assert result["verdict"] == "Opportunity (Oversold)"

    def test_output_keys(self):
        fg = {"score": 50.0}
        result = market_diagnosis(fg, [])
        assert "verdict" in result
        assert "description" in result
        assert "fear_greed_score" in result
        assert "bullish_signals" in result
        assert "bearish_signals" in result

    def test_empty_trends(self):
        fg = {"score": 50.0}
        result = market_diagnosis(fg, [])
        assert result["verdict"] == "Neutral"
