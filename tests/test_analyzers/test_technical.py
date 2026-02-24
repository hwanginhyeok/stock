"""Tests for technical analysis pure functions and TechnicalAnalyzer."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.analyzers.technical import (
    TechnicalAnalyzer,
    _bbands,
    _ema,
    _macd,
    _rsi,
    _sma,
)


# ============================================================
# Pure function tests
# ============================================================


class TestSMA:
    """Test Simple Moving Average."""

    def test_basic(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = _sma(s, 3)
        assert result.iloc[-1] == pytest.approx(4.0)  # (3+4+5)/3
        assert result.iloc[2] == pytest.approx(2.0)   # (1+2+3)/3

    def test_nan_for_insufficient_data(self):
        s = pd.Series([1.0, 2.0])
        result = _sma(s, 5)
        assert result.isna().all()

    def test_length_1(self):
        s = pd.Series([10.0, 20.0, 30.0])
        result = _sma(s, 1)
        assert result.iloc[0] == pytest.approx(10.0)
        assert result.iloc[2] == pytest.approx(30.0)

    def test_on_ohlcv(self, sample_ohlcv_df):
        result = _sma(sample_ohlcv_df["Close"], 20)
        assert not result.iloc[-1:].isna().any()
        assert result.iloc[:19].isna().all()


class TestEMA:
    """Test Exponential Moving Average."""

    def test_basic(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = _ema(s, 3)
        assert len(result) == 5
        assert not result.isna().any()

    def test_follows_trend(self):
        s = pd.Series(range(1, 11), dtype=float)
        result = _ema(s, 3)
        # EMA should follow rising trend
        assert result.iloc[-1] > result.iloc[-3]

    def test_on_ohlcv(self, sample_ohlcv_df):
        result = _ema(sample_ohlcv_df["Close"], 12)
        assert not result.isna().any()


class TestRSI:
    """Test Relative Strength Index."""

    def test_steady_up(self):
        rng = np.random.default_rng(42)
        s = pd.Series(np.linspace(100, 200, 100) + rng.normal(0, 0.5, 100))
        result = _rsi(s, 14)
        last = result.dropna().iloc[-1]
        assert last > 70  # should be overbought

    def test_steady_down(self):
        rng = np.random.default_rng(42)
        s = pd.Series(np.linspace(200, 100, 100) + rng.normal(0, 0.5, 100))
        result = _rsi(s, 14)
        last = result.dropna().iloc[-1]
        assert last < 30  # should be oversold

    def test_range(self, sample_ohlcv_df):
        result = _rsi(sample_ohlcv_df["Close"], 14)
        valid = result.dropna()
        assert (valid >= 0).all()
        assert (valid <= 100).all()

    def test_flat_series(self):
        s = pd.Series([100.0] * 30)
        result = _rsi(s, 14)
        # When no change, RSI is undefined (NaN due to 0/0)
        # Just verify it doesn't crash
        assert len(result) == 30


class TestMACD:
    """Test MACD computation."""

    def test_output_columns(self, sample_ohlcv_df):
        result = _macd(sample_ohlcv_df["Close"])
        assert set(result.columns) == {"macd", "histogram", "signal"}
        assert len(result) == len(sample_ohlcv_df)

    def test_histogram_is_diff(self, sample_ohlcv_df):
        result = _macd(sample_ohlcv_df["Close"])
        diff = result["macd"] - result["signal"]
        pd.testing.assert_series_equal(result["histogram"], diff, check_names=False)

    def test_custom_params(self):
        s = pd.Series(np.random.default_rng(1).normal(100, 5, 60))
        result = _macd(s, fast=5, slow=10, signal=3)
        assert len(result) == 60


class TestBBands:
    """Test Bollinger Bands."""

    def test_output_columns(self, sample_ohlcv_df):
        result = _bbands(sample_ohlcv_df["Close"])
        assert set(result.columns) == {"lower", "mid", "upper"}

    def test_upper_above_lower(self, sample_ohlcv_df):
        result = _bbands(sample_ohlcv_df["Close"])
        valid = result.dropna()
        assert (valid["upper"] >= valid["lower"]).all()

    def test_mid_is_sma(self, sample_ohlcv_df):
        result = _bbands(sample_ohlcv_df["Close"], length=20)
        sma = _sma(sample_ohlcv_df["Close"], 20)
        pd.testing.assert_series_equal(result["mid"], sma, check_names=False)


# ============================================================
# TechnicalAnalyzer class tests
# ============================================================


class TestTechnicalAnalyzer:
    """Test TechnicalAnalyzer.analyze() method."""

    def test_analyze_returns_score_and_signals(self, sample_ohlcv_df):
        analyzer = TechnicalAnalyzer()
        result = analyzer.analyze("TEST", ohlcv=sample_ohlcv_df)
        assert "score" in result
        assert "signals" in result
        assert "indicators" in result
        assert 0 <= result["score"] <= 100

    def test_analyze_empty_raises(self):
        analyzer = TechnicalAnalyzer()
        with pytest.raises(Exception):
            analyzer.analyze("TEST", ohlcv=pd.DataFrame())

    def test_analyze_none_raises(self):
        analyzer = TechnicalAnalyzer()
        with pytest.raises(Exception):
            analyzer.analyze("TEST", ohlcv=None)

    def test_insufficient_data_returns_50(self, short_ohlcv_df):
        analyzer = TechnicalAnalyzer()
        result = analyzer.analyze("TEST", ohlcv=short_ohlcv_df)
        assert result["score"] == 50.0
        assert "insufficient_data" in result["signals"]

    def test_indicators_populated(self, sample_ohlcv_df):
        analyzer = TechnicalAnalyzer()
        result = analyzer.analyze("TEST", ohlcv=sample_ohlcv_df)
        ind = result["indicators"]
        assert "rsi" in ind
        assert "macd" in ind
        assert "sma_20" in ind
        assert "bb_upper" in ind

    def test_raw_data_present(self, sample_ohlcv_df):
        analyzer = TechnicalAnalyzer()
        result = analyzer.analyze("TEST", ohlcv=sample_ohlcv_df)
        assert "raw" in result
        assert "close" in result["raw"]
        assert "data_points" in result["raw"]

    def test_uptrend_and_downtrend_produce_valid_scores(self, ohlcv_uptrend, ohlcv_downtrend):
        analyzer = TechnicalAnalyzer()
        up = analyzer.analyze("UP", ohlcv=ohlcv_uptrend)
        down = analyzer.analyze("DOWN", ohlcv=ohlcv_downtrend)
        # Both should produce valid 0-100 scores
        assert 0 <= up["score"] <= 100
        assert 0 <= down["score"] <= 100
        assert len(up["signals"]) >= 0
        assert len(down["signals"]) >= 0

    def test_last_value_helper(self):
        s = pd.Series([1.0, 2.0, float("nan"), 3.0])
        assert TechnicalAnalyzer._last_value(s) == 3.0

    def test_last_value_all_nan(self):
        s = pd.Series([float("nan"), float("nan")])
        assert TechnicalAnalyzer._last_value(s) is None
