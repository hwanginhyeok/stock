"""Tests for Options IV collector."""

from __future__ import annotations

import math
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.collectors.sentiment.options_iv_collector import (
    OptionsIVCollector,
    _classify_iv_level,
    _compute_iv_skew,
    _find_atm_iv,
)


# ---------------------------------------------------------------------------
# Helper: build a mock options chain DataFrame
# ---------------------------------------------------------------------------

def _make_chain(
    strikes: list[float],
    ivs: list[float],
    volumes: list[int] | None = None,
    ois: list[int] | None = None,
) -> pd.DataFrame:
    """Create a minimal options chain DataFrame."""
    n = len(strikes)
    return pd.DataFrame({
        "strike": strikes,
        "impliedVolatility": ivs,
        "volume": volumes or [100] * n,
        "openInterest": ois or [500] * n,
        "lastPrice": [5.0] * n,
    })


# ---------------------------------------------------------------------------
# _find_atm_iv
# ---------------------------------------------------------------------------

class TestFindAtmIV:
    """Test ATM IV extraction from options chain."""

    def test_exact_strike_match(self) -> None:
        chain = _make_chain([90, 95, 100, 105, 110], [0.30, 0.28, 0.25, 0.27, 0.32])
        result = _find_atm_iv(chain, current_price=100.0)
        assert result["strike"] == 100.0
        assert result["iv"] == 0.25

    def test_closest_strike(self) -> None:
        chain = _make_chain([90, 95, 105, 110], [0.30, 0.28, 0.27, 0.32])
        result = _find_atm_iv(chain, current_price=100.0)
        assert result["strike"] in (95.0, 105.0)
        assert result["iv"] is not None

    def test_empty_chain(self) -> None:
        chain = pd.DataFrame()
        result = _find_atm_iv(chain, current_price=100.0)
        assert result["iv"] is None

    def test_nan_iv_handled(self) -> None:
        chain = _make_chain([100], [float("nan")])
        result = _find_atm_iv(chain, current_price=100.0)
        assert result["iv"] is None


# ---------------------------------------------------------------------------
# _compute_iv_skew
# ---------------------------------------------------------------------------

class TestComputeIVSkew:
    """Test IV skew computation."""

    def test_positive_skew(self) -> None:
        """OTM put IV > OTM call IV → positive skew (fear)."""
        # Price = 100, OTM put ~95 strike, OTM call ~105 strike
        chain = _make_chain(
            [90, 95, 100, 105, 110],
            [0.40, 0.35, 0.25, 0.22, 0.20],
        )
        result = _compute_iv_skew(chain, current_price=100.0)
        assert result["skew"] is not None
        assert result["skew"] > 0  # put IV > call IV

    def test_negative_skew(self) -> None:
        """OTM call IV > OTM put IV → negative skew."""
        chain = _make_chain(
            [90, 95, 100, 105, 110],
            [0.20, 0.22, 0.25, 0.35, 0.40],
        )
        result = _compute_iv_skew(chain, current_price=100.0)
        assert result["skew"] is not None
        assert result["skew"] < 0

    def test_empty_chain(self) -> None:
        result = _compute_iv_skew(pd.DataFrame(), current_price=100.0)
        assert result["skew"] is None


# ---------------------------------------------------------------------------
# _classify_iv_level
# ---------------------------------------------------------------------------

class TestClassifyIVLevel:
    """Test IV level classification."""

    @pytest.mark.parametrize(
        "iv, percentile, expected",
        [
            (0.30, 90.0, "Very High"),
            (0.30, 65.0, "High"),
            (0.30, 50.0, "Normal"),
            (0.30, 25.0, "Low"),
            (0.30, 10.0, "Very Low"),
        ],
    )
    def test_with_percentile(self, iv: float, percentile: float, expected: str) -> None:
        assert _classify_iv_level(iv, percentile) == expected

    @pytest.mark.parametrize(
        "iv, expected",
        [
            (0.70, "Very High"),
            (0.45, "High"),
            (0.25, "Normal"),
            (0.15, "Low"),
            (0.05, "Very Low"),
        ],
    )
    def test_without_percentile(self, iv: float, expected: str) -> None:
        assert _classify_iv_level(iv, None) == expected


# ---------------------------------------------------------------------------
# OptionsIVCollector.collect_stock
# ---------------------------------------------------------------------------

class TestOptionsIVCollector:
    """Test OptionsIVCollector with mocked yfinance."""

    def _make_mock_ticker(self) -> MagicMock:
        """Build a mock yfinance Ticker with options data."""
        mock_ticker = MagicMock()

        # Price history
        hist = pd.DataFrame(
            {"Close": [145.0, 146.0, 148.0, 149.0, 150.0]},
            index=pd.bdate_range(end="2026-02-24", periods=5),
        )
        mock_ticker.history.return_value = hist

        # Options expirations
        mock_ticker.options = ("2026-03-07", "2026-03-21", "2026-04-18")

        # Option chain data
        calls = _make_chain(
            strikes=[140, 145, 150, 155, 160],
            ivs=[0.32, 0.28, 0.25, 0.27, 0.30],
            volumes=[200, 500, 1000, 400, 150],
            ois=[3000, 5000, 8000, 4000, 2000],
        )
        puts = _make_chain(
            strikes=[140, 145, 150, 155, 160],
            ivs=[0.35, 0.30, 0.26, 0.24, 0.22],
            volumes=[300, 600, 800, 300, 100],
            ois=[4000, 6000, 7000, 3000, 1500],
        )
        mock_chain = MagicMock()
        mock_chain.calls = calls
        mock_chain.puts = puts
        mock_ticker.option_chain.return_value = mock_chain

        return mock_ticker

    @patch("src.collectors.sentiment.options_iv_collector.yf.Ticker")
    def test_collect_stock_success(self, mock_yf_ticker: MagicMock) -> None:
        mock_yf_ticker.return_value = self._make_mock_ticker()

        collector = OptionsIVCollector()
        result = collector.collect_stock("AAPL")

        assert result["ticker"] == "AAPL"
        assert result["current_price"] == 150.0
        assert "expected_moves" in result
        assert len(result["expected_moves"]) > 0

        # Check first expected move entry
        em = result["expected_moves"][0]
        assert "sigma_1" in em
        assert "sigma_2" in em
        assert em["sigma_1"]["upper"] > 150.0
        assert em["sigma_1"]["lower"] < 150.0
        assert em["sigma_2"]["upper"] > em["sigma_1"]["upper"]
        assert em["sigma_2"]["lower"] < em["sigma_1"]["lower"]

    @patch("src.collectors.sentiment.options_iv_collector.yf.Ticker")
    def test_collect_stock_no_options(self, mock_yf_ticker: MagicMock) -> None:
        mock_ticker = MagicMock()
        hist = pd.DataFrame(
            {"Close": [150.0]},
            index=pd.bdate_range(end="2026-02-24", periods=1),
        )
        mock_ticker.history.return_value = hist
        mock_ticker.options = ()
        mock_yf_ticker.return_value = mock_ticker

        collector = OptionsIVCollector()
        result = collector.collect_stock("NOOPT")

        assert "error" in result

    @patch("src.collectors.sentiment.options_iv_collector.yf.Ticker")
    def test_atm_iv_is_average_of_call_put(self, mock_yf_ticker: MagicMock) -> None:
        mock_yf_ticker.return_value = self._make_mock_ticker()

        collector = OptionsIVCollector()
        result = collector.collect_stock("AAPL")

        em = result["expected_moves"][0]
        # ATM IV should be average of call IV (0.25) and put IV (0.26)
        assert em["atm_iv"] == pytest.approx(0.255, abs=0.001)

    @patch("src.collectors.sentiment.options_iv_collector.yf.Ticker")
    def test_expected_move_math(self, mock_yf_ticker: MagicMock) -> None:
        """Verify the expected move formula: price × IV × √(DTE/365)."""
        mock_yf_ticker.return_value = self._make_mock_ticker()

        collector = OptionsIVCollector()
        result = collector.collect_stock("AAPL")

        em = result["expected_moves"][0]
        price = result["current_price"]
        iv = em["atm_iv"]
        dte = em["dte"]

        expected = price * iv * math.sqrt(dte / 365)
        assert em["expected_move"] == pytest.approx(expected, abs=0.01)

    @patch("src.collectors.sentiment.options_iv_collector.yf.Ticker")
    def test_sigma_2_is_double_sigma_1(self, mock_yf_ticker: MagicMock) -> None:
        mock_yf_ticker.return_value = self._make_mock_ticker()

        collector = OptionsIVCollector()
        result = collector.collect_stock("AAPL")

        em = result["expected_moves"][0]
        price = result["current_price"]
        s1_move = em["sigma_1"]["upper"] - price
        s2_move = em["sigma_2"]["upper"] - price
        assert s2_move == pytest.approx(s1_move * 2, abs=0.02)

    @patch("src.collectors.sentiment.options_iv_collector.yf.Ticker")
    def test_iv_skew_included(self, mock_yf_ticker: MagicMock) -> None:
        mock_yf_ticker.return_value = self._make_mock_ticker()

        collector = OptionsIVCollector()
        result = collector.collect_stock("AAPL")

        em = result["expected_moves"][0]
        assert "iv_skew" in em
        assert em["iv_skew"]["skew"] is not None

    @patch("src.collectors.sentiment.options_iv_collector.yf.Ticker")
    def test_oi_pc_ratio(self, mock_yf_ticker: MagicMock) -> None:
        mock_yf_ticker.return_value = self._make_mock_ticker()

        collector = OptionsIVCollector()
        result = collector.collect_stock("AAPL")

        em = result["expected_moves"][0]
        assert em["oi_pc_ratio"] is not None
        # puts OI = 21500, calls OI = 22000 → ratio < 1.0
        assert em["oi_pc_ratio"] == pytest.approx(21500 / 22000, abs=0.01)
