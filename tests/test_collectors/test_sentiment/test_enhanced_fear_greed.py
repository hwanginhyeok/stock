"""Tests for enhanced compute_fear_greed with optional components."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.analyzers.market_sentiment import compute_fear_greed, _score_to_level


def _make_ohlcv(n: int = 30, base: float = 100.0) -> pd.DataFrame:
    """Create a synthetic OHLCV DataFrame for testing."""
    dates = pd.date_range("2026-01-01", periods=n, freq="B")
    close = base + np.cumsum(np.random.randn(n) * 0.5)
    return pd.DataFrame(
        {
            "Open": close - 0.5,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": np.random.randint(1000, 10000, n),
        },
        index=dates,
    )


class TestScoreToLevel:
    """Test level label mapping."""

    @pytest.mark.parametrize(
        "score, expected",
        [
            (0, "Extreme Fear"),
            (19, "Extreme Fear"),
            (20, "Fear"),
            (39, "Fear"),
            (40, "Neutral"),
            (59, "Neutral"),
            (60, "Greed"),
            (79, "Greed"),
            (80, "Extreme Greed"),
            (100, "Extreme Greed"),
        ],
    )
    def test_level(self, score: float, expected: str) -> None:
        assert _score_to_level(score) == expected


class TestComputeFearGreedBase:
    """Test base components (no optional data)."""

    def test_basic_computation(self) -> None:
        index_data = {"SPX": _make_ohlcv(30)}
        result = compute_fear_greed(20.0, index_data)

        assert "score" in result
        assert "level" in result
        assert "components" in result
        assert 0 <= result["score"] <= 100
        assert result["level"] in [
            "Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed",
        ]

        # Only base components when no optional data
        assert "vix" in result["components"]
        assert "rsi" in result["components"]
        assert "momentum" in result["components"]
        # Weights should sum to ~1.0 (base only: 0.4+0.3+0.3)
        total_weight = sum(c["weight"] for c in result["components"].values())
        assert abs(total_weight - 1.0) < 0.01

    def test_extreme_fear_vix(self) -> None:
        """High VIX should push score toward fear."""
        index_data = {"SPX": _make_ohlcv(30)}
        result = compute_fear_greed(40.0, index_data)
        assert result["components"]["vix"]["score"] < 20

    def test_extreme_greed_vix(self) -> None:
        """Low VIX should push score toward greed."""
        index_data = {"SPX": _make_ohlcv(30)}
        result = compute_fear_greed(10.0, index_data)
        assert result["components"]["vix"]["score"] > 80


class TestComputeFearGreedWithOptional:
    """Test with optional components."""

    def test_with_putcall(self) -> None:
        index_data = {"SPX": _make_ohlcv(30)}
        putcall = [{"type": "equity", "pc_ratio": 0.8}]

        result = compute_fear_greed(20.0, index_data, putcall_data=putcall)

        assert "putcall" in result["components"]
        total_weight = sum(c["weight"] for c in result["components"].values())
        assert abs(total_weight - 1.0) < 0.01

    def test_with_aaii(self) -> None:
        index_data = {"SPX": _make_ohlcv(30)}
        aaii = [{"bull_bear_spread": 15.0}]

        result = compute_fear_greed(20.0, index_data, aaii_data=aaii)

        assert "aaii" in result["components"]
        assert result["components"]["aaii"]["score"] > 50  # bullish spread

    def test_with_community(self) -> None:
        index_data = {"SPX": _make_ohlcv(30)}
        community = [
            {"bullish_ratio": 0.7},
            {"bullish_ratio": 0.8},
        ]

        result = compute_fear_greed(
            20.0, index_data, community_data=community,
        )

        assert "community" in result["components"]
        assert result["components"]["community"]["score"] > 50

    def test_with_all_optional(self) -> None:
        index_data = {"SPX": _make_ohlcv(30)}
        putcall = [{"type": "equity", "pc_ratio": 0.7}]
        aaii = [{"bull_bear_spread": 10.0}]
        community = [{"sentiment_score": 0.6}]
        cnn = [{"score": 55.0, "level": "Greed", "source": "cnn_api"}]

        result = compute_fear_greed(
            20.0,
            index_data,
            putcall_data=putcall,
            aaii_data=aaii,
            community_data=community,
            cnn_fear_greed=cnn,
        )

        assert "putcall" in result["components"]
        assert "aaii" in result["components"]
        assert "community" in result["components"]
        assert "cnn_reference" in result
        assert result["cnn_reference"]["score"] == 55.0

        # CNN should NOT be in components (reference only)
        assert "cnn" not in result["components"]

        total_weight = sum(c["weight"] for c in result["components"].values())
        assert abs(total_weight - 1.0) < 0.01

    def test_cnn_reference_only(self) -> None:
        """CNN data should be reference, not affect score."""
        index_data = {"SPX": _make_ohlcv(30)}

        result_no_cnn = compute_fear_greed(20.0, index_data)
        result_with_cnn = compute_fear_greed(
            20.0,
            index_data,
            cnn_fear_greed=[{"score": 99, "level": "Extreme Greed"}],
        )

        # Score should be identical (CNN is reference only)
        assert result_no_cnn["score"] == result_with_cnn["score"]
