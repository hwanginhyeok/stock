"""Analyzer test fixtures — sample OHLCV DataFrames."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_ohlcv_df() -> pd.DataFrame:
    """120-day OHLCV DataFrame using a seeded random walk."""
    rng = np.random.default_rng(seed=42)
    n = 120
    close = 100.0 + np.cumsum(rng.normal(0, 1.5, n))
    close = np.maximum(close, 10.0)  # keep positive
    high = close + rng.uniform(0.5, 3.0, n)
    low = close - rng.uniform(0.5, 3.0, n)
    low = np.maximum(low, 1.0)
    opn = low + (high - low) * rng.uniform(0.2, 0.8, n)
    volume = rng.integers(1_000_000, 50_000_000, n)

    dates = pd.bdate_range(end="2026-02-20", periods=n)
    return pd.DataFrame(
        {"Open": opn, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


@pytest.fixture
def ohlcv_uptrend() -> pd.DataFrame:
    """60-day steady uptrend OHLCV."""
    n = 60
    base = np.linspace(100, 140, n)
    rng = np.random.default_rng(seed=7)
    noise = rng.normal(0, 0.3, n)
    close = base + noise
    high = close + 1.5
    low = close - 1.5
    opn = close - 0.5
    volume = np.full(n, 10_000_000)

    dates = pd.bdate_range(end="2026-02-20", periods=n)
    return pd.DataFrame(
        {"Open": opn, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


@pytest.fixture
def ohlcv_downtrend() -> pd.DataFrame:
    """60-day steady downtrend OHLCV."""
    n = 60
    base = np.linspace(140, 100, n)
    rng = np.random.default_rng(seed=11)
    noise = rng.normal(0, 0.3, n)
    close = base + noise
    high = close + 1.5
    low = close - 1.5
    opn = close + 0.5
    volume = np.full(n, 10_000_000)

    dates = pd.bdate_range(end="2026-02-20", periods=n)
    return pd.DataFrame(
        {"Open": opn, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


@pytest.fixture
def short_ohlcv_df() -> pd.DataFrame:
    """15-day OHLCV (below 30-day minimum for TechnicalAnalyzer)."""
    rng = np.random.default_rng(seed=99)
    n = 15
    close = 50.0 + np.cumsum(rng.normal(0, 0.5, n))
    high = close + 1.0
    low = close - 1.0
    opn = close
    volume = rng.integers(1_000_000, 10_000_000, n)

    dates = pd.bdate_range(end="2026-02-20", periods=n)
    return pd.DataFrame(
        {"Open": opn, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )
