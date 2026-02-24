"""Tests for trading strategies."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.backtesting.strategy.base import Signal, SignalType
from src.backtesting.strategy.sentiment_contrarian import SentimentContrarianStrategy
from src.backtesting.strategy.technical_combo import TechnicalComboStrategy


@pytest.fixture()
def single_ticker_prices() -> dict[str, pd.DataFrame]:
    """Single ticker with known price data."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    # Create a downtrend to trigger RSI oversold
    prices_arr = 100 * np.cumprod(1 + np.random.normal(-0.002, 0.02, len(dates)))

    return {
        "TEST": pd.DataFrame(
            {
                "open": prices_arr * 0.999,
                "high": prices_arr * 1.01,
                "low": prices_arr * 0.99,
                "close": prices_arr,
                "volume": np.random.randint(1_000_000, 10_000_000, len(dates)),
            },
            index=dates,
        ),
    }


class TestSentimentContrarianStrategy:
    """Tests for SentimentContrarianStrategy."""

    def test_extreme_fear_generates_buy(
        self, single_ticker_prices: dict[str, pd.DataFrame],
    ) -> None:
        strategy = SentimentContrarianStrategy(fear_threshold=25)
        signals = strategy.generate_signals(
            "2024-01-02",
            single_ticker_prices,
            {"fear_greed_score": 10},
        )
        assert len(signals) == 1
        assert signals[0].signal_type == SignalType.BUY
        assert "Extreme Fear" in signals[0].reason

    def test_extreme_greed_generates_sell(
        self, single_ticker_prices: dict[str, pd.DataFrame],
    ) -> None:
        strategy = SentimentContrarianStrategy(greed_threshold=75)
        signals = strategy.generate_signals(
            "2024-01-02",
            single_ticker_prices,
            {"fear_greed_score": 90},
        )
        assert len(signals) == 1
        assert signals[0].signal_type == SignalType.SELL
        assert "Extreme Greed" in signals[0].reason

    def test_neutral_no_signal(
        self, single_ticker_prices: dict[str, pd.DataFrame],
    ) -> None:
        strategy = SentimentContrarianStrategy()
        signals = strategy.generate_signals(
            "2024-01-02",
            single_ticker_prices,
            {"fear_greed_score": 50},
        )
        assert len(signals) == 0

    def test_no_context_no_signals(
        self, single_ticker_prices: dict[str, pd.DataFrame],
    ) -> None:
        strategy = SentimentContrarianStrategy()
        signals = strategy.generate_signals("2024-01-02", single_ticker_prices, None)
        assert len(signals) == 0

    def test_putcall_fear_buy(
        self, single_ticker_prices: dict[str, pd.DataFrame],
    ) -> None:
        strategy = SentimentContrarianStrategy(putcall_fear=1.2)
        signals = strategy.generate_signals(
            "2024-01-02",
            single_ticker_prices,
            {"fear_greed_score": 50, "putcall_ratio": 1.5},
        )
        assert len(signals) == 1
        assert signals[0].signal_type == SignalType.BUY

    def test_combined_signals(
        self, single_ticker_prices: dict[str, pd.DataFrame],
    ) -> None:
        strategy = SentimentContrarianStrategy()
        signals = strategy.generate_signals(
            "2024-01-02",
            single_ticker_prices,
            {"fear_greed_score": 10, "putcall_ratio": 1.5},
        )
        assert len(signals) == 1
        assert signals[0].signal_type == SignalType.BUY
        assert "F&G" in signals[0].reason
        assert "P/C" in signals[0].reason

    def test_name_and_description(self) -> None:
        strategy = SentimentContrarianStrategy()
        assert strategy.name == "sentiment_contrarian"
        assert "F&G" in strategy.description


class TestTechnicalComboStrategy:
    """Tests for TechnicalComboStrategy."""

    def test_no_context_no_signals(
        self, single_ticker_prices: dict[str, pd.DataFrame],
    ) -> None:
        strategy = TechnicalComboStrategy()
        signals = strategy.generate_signals("2024-06-01", single_ticker_prices, None)
        assert len(signals) == 0

    def test_insufficient_data(self) -> None:
        strategy = TechnicalComboStrategy(rsi_period=14)
        dates = pd.date_range("2024-01-01", periods=5, freq="B")
        short_data = {
            "TEST": pd.DataFrame(
                {"close": [100, 101, 102, 103, 104]}, index=dates,
            ),
        }
        signals = strategy.generate_signals(
            "2024-01-07",
            short_data,
            {"fear_greed_score": 10},
        )
        assert len(signals) == 0

    def test_name_and_description(self) -> None:
        strategy = TechnicalComboStrategy()
        assert strategy.name == "technical_combo"
        assert "RSI" in strategy.description

    def test_rsi_computation(self) -> None:
        strategy = TechnicalComboStrategy(rsi_period=14)
        # Create a series that goes straight down
        closes = pd.Series([100 - i * 2 for i in range(20)])
        rsi = strategy._compute_rsi(closes)
        assert rsi is not None
        assert rsi < 30  # Should be oversold

    def test_rsi_overbought(self) -> None:
        strategy = TechnicalComboStrategy(rsi_period=14)
        # Create a series that goes straight up
        closes = pd.Series([100 + i * 2 for i in range(20)])
        rsi = strategy._compute_rsi(closes)
        assert rsi is not None
        assert rsi > 70  # Should be overbought
