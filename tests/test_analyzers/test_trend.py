"""Tests for trend indicator functions (ATR, ADX, Supertrend)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.analyzers.trend import _adx, _atr, _supertrend


class TestATR:
    """Test Average True Range."""

    def test_output_length(self, sample_ohlcv_df):
        result = _atr(sample_ohlcv_df, period=14)
        assert len(result) == len(sample_ohlcv_df)

    def test_positive_values(self, sample_ohlcv_df):
        result = _atr(sample_ohlcv_df, period=14)
        valid = result.dropna()
        assert (valid >= 0).all()

    def test_higher_volatility_higher_atr(self):
        rng = np.random.default_rng(42)
        n = 50

        # Low volatility
        close_low = 100.0 + np.cumsum(rng.normal(0, 0.1, n))
        df_low = pd.DataFrame({
            "High": close_low + 0.2,
            "Low": close_low - 0.2,
            "Close": close_low,
        })

        # High volatility
        close_high = 100.0 + np.cumsum(rng.normal(0, 3.0, n))
        df_high = pd.DataFrame({
            "High": close_high + 5.0,
            "Low": close_high - 5.0,
            "Close": close_high,
        })

        atr_low = _atr(df_low, 14).dropna().iloc[-1]
        atr_high = _atr(df_high, 14).dropna().iloc[-1]
        assert atr_high > atr_low

    def test_custom_period(self, sample_ohlcv_df):
        atr_7 = _atr(sample_ohlcv_df, period=7)
        atr_21 = _atr(sample_ohlcv_df, period=21)
        # Both should produce values
        assert not atr_7.dropna().empty
        assert not atr_21.dropna().empty


class TestADX:
    """Test Average Directional Index."""

    def test_output_columns(self, sample_ohlcv_df):
        result = _adx(sample_ohlcv_df, period=14)
        assert set(result.columns) == {"ADX", "plus_di", "minus_di"}
        assert len(result) == len(sample_ohlcv_df)

    def test_adx_positive(self, sample_ohlcv_df):
        result = _adx(sample_ohlcv_df, period=14)
        valid = result["ADX"].dropna()
        assert (valid >= 0).all()

    def test_strong_trend_high_adx(self, ohlcv_uptrend):
        result = _adx(ohlcv_uptrend, period=14)
        last_adx = result["ADX"].dropna().iloc[-1]
        # Strong uptrend should show moderate-to-high ADX
        assert last_adx > 15

    def test_di_values(self, sample_ohlcv_df):
        result = _adx(sample_ohlcv_df, period=14)
        valid_plus = result["plus_di"].dropna()
        valid_minus = result["minus_di"].dropna()
        assert (valid_plus >= 0).all()
        assert (valid_minus >= 0).all()


class TestSupertrend:
    """Test Supertrend indicator."""

    def test_output_columns(self, sample_ohlcv_df):
        result = _supertrend(sample_ohlcv_df, period=10, multiplier=3.0)
        assert set(result.columns) == {"supertrend", "direction"}

    def test_direction_values(self, sample_ohlcv_df):
        result = _supertrend(sample_ohlcv_df)
        valid_dir = result["direction"].dropna()
        assert set(valid_dir.unique()).issubset({1, -1})

    def test_uptrend_produces_direction(self, ohlcv_uptrend):
        result = _supertrend(ohlcv_uptrend, period=10, multiplier=3.0)
        last_dir = result["direction"].iloc[-1]
        assert last_dir in (1, -1)

    def test_downtrend_produces_direction(self, ohlcv_downtrend):
        result = _supertrend(ohlcv_downtrend, period=10, multiplier=3.0)
        last_dir = result["direction"].iloc[-1]
        assert last_dir in (1, -1)

    def test_custom_params(self, sample_ohlcv_df):
        result = _supertrend(sample_ohlcv_df, period=7, multiplier=2.0)
        assert len(result) == len(sample_ohlcv_df)
