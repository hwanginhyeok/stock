"""Fixtures for backtesting tests."""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture()
def sample_prices() -> dict[str, pd.DataFrame]:
    """Generate sample OHLCV data for testing."""
    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    base_price = 100.0

    # Simulate a simple price series with trend
    import numpy as np

    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.02, len(dates))
    prices_arr = base_price * np.cumprod(1 + returns)

    data = {
        "open": prices_arr * 0.999,
        "high": prices_arr * 1.01,
        "low": prices_arr * 0.99,
        "close": prices_arr,
        "volume": np.random.randint(1_000_000, 10_000_000, len(dates)),
        "adjusted_close": prices_arr,
    }
    df = pd.DataFrame(data, index=dates)
    return {"TEST": df}


@pytest.fixture()
def multi_ticker_prices() -> dict[str, pd.DataFrame]:
    """Generate sample data for multiple tickers."""
    import numpy as np

    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=252, freq="B")

    result = {}
    for ticker, base in [("AAPL", 150), ("MSFT", 200), ("NVDA", 50)]:
        returns = np.random.normal(0.001, 0.025, len(dates))
        prices_arr = base * np.cumprod(1 + returns)
        df = pd.DataFrame(
            {
                "open": prices_arr * 0.999,
                "high": prices_arr * 1.01,
                "low": prices_arr * 0.99,
                "close": prices_arr,
                "volume": np.random.randint(1_000_000, 10_000_000, len(dates)),
                "adjusted_close": prices_arr,
            },
            index=dates,
        )
        result[ticker] = df
    return result
