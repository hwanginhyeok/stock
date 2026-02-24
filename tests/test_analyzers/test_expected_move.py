"""Tests for expected move analyzer."""

from __future__ import annotations

import math

import pytest

from src.analyzers.expected_move import (
    ExpectedMoveAnalyzer,
    _classify_expected_move,
    _iv_to_expected_move,
)


# ---------------------------------------------------------------------------
# _iv_to_expected_move
# ---------------------------------------------------------------------------

class TestIVToExpectedMove:
    """Test IV to expected move conversion."""

    def test_basic_calculation(self) -> None:
        # price=100, iv=0.20 (20%), 30 days
        result = _iv_to_expected_move(100.0, 0.20, 30)
        expected = 100 * 0.20 * math.sqrt(30 / 365)
        assert result == pytest.approx(expected, rel=1e-6)

    def test_higher_iv_means_bigger_move(self) -> None:
        low = _iv_to_expected_move(100.0, 0.15, 30)
        high = _iv_to_expected_move(100.0, 0.40, 30)
        assert high > low

    def test_longer_dte_means_bigger_move(self) -> None:
        short = _iv_to_expected_move(100.0, 0.25, 7)
        long = _iv_to_expected_move(100.0, 0.25, 90)
        assert long > short

    def test_zero_iv_returns_zero(self) -> None:
        assert _iv_to_expected_move(100.0, 0.0, 30) == 0.0

    def test_one_day(self) -> None:
        result = _iv_to_expected_move(5000.0, 0.18, 1)
        expected = 5000 * 0.18 * math.sqrt(1 / 365)
        assert result == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# _classify_expected_move
# ---------------------------------------------------------------------------

class TestClassifyExpectedMove:
    """Test expected move magnitude classification."""

    @pytest.mark.parametrize(
        "pct, expected",
        [
            (12.0, "Extreme"),
            (6.0, "Very High"),
            (4.0, "High"),
            (2.0, "Moderate"),
            (0.8, "Low"),
        ],
    )
    def test_classification(self, pct: float, expected: str) -> None:
        assert _classify_expected_move(pct) == expected


# ---------------------------------------------------------------------------
# ExpectedMoveAnalyzer
# ---------------------------------------------------------------------------

def _make_options_data(
    ticker: str = "AAPL",
    price: float = 150.0,
    atm_iv: float = 0.25,
    dte: int = 14,
    iv_rank: float | None = 55.0,
    skew: float = 0.08,
    oi_pc_ratio: float = 0.85,
) -> dict:
    """Build mock OptionsIVCollector output."""
    em = price * atm_iv * math.sqrt(dte / 365)
    return {
        "ticker": ticker,
        "current_price": price,
        "iv_rank": iv_rank,
        "iv_level": "Normal",
        "skew_sentiment": "Neutral",
        "expirations_available": 3,
        "expected_moves": [
            {
                "expiration": "2026-03-10",
                "dte": dte,
                "atm_iv": atm_iv,
                "atm_iv_pct": atm_iv * 100,
                "expected_move": round(em, 2),
                "expected_move_pct": round(em / price * 100, 2),
                "sigma_1": {
                    "upper": round(price + em, 2),
                    "lower": round(price - em, 2),
                    "probability": 68.2,
                },
                "sigma_2": {
                    "upper": round(price + em * 2, 2),
                    "lower": round(price - em * 2, 2),
                    "probability": 95.4,
                },
                "iv_skew": {
                    "otm_put_iv": 0.30,
                    "otm_call_iv": 0.30 - skew,
                    "skew": skew,
                },
                "oi_pc_ratio": oi_pc_ratio,
                "volume_pc_ratio": 0.90,
            },
        ],
    }


class TestExpectedMoveAnalyzer:
    """Test ExpectedMoveAnalyzer."""

    def test_basic_analysis(self) -> None:
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=_make_options_data())

        assert result["status"] == "ok"
        assert result["ticker"] == "AAPL"
        assert result["current_price"] == 150.0
        assert "price_ranges" in result
        assert "sigma_0_5" in result["price_ranges"]
        assert "sigma_1" in result["price_ranges"]
        assert "sigma_1_5" in result["price_ranges"]
        assert "sigma_2" in result["price_ranges"]

    def test_sigma_ordering(self) -> None:
        """Price ranges should widen: 0.5σ < 1σ < 1.5σ < 2σ."""
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=_make_options_data())
        ranges = result["price_ranges"]

        assert ranges["sigma_0_5"]["upper"] < ranges["sigma_1"]["upper"]
        assert ranges["sigma_1"]["upper"] < ranges["sigma_1_5"]["upper"]
        assert ranges["sigma_1_5"]["upper"] < ranges["sigma_2"]["upper"]

        assert ranges["sigma_0_5"]["lower"] > ranges["sigma_1"]["lower"]
        assert ranges["sigma_1"]["lower"] > ranges["sigma_1_5"]["lower"]
        assert ranges["sigma_1_5"]["lower"] > ranges["sigma_2"]["lower"]

    def test_no_data_returns_error(self) -> None:
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("NODATA", options_data={})
        assert result["status"] == "no_data"

    def test_error_in_data(self) -> None:
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("ERR", options_data={"error": "No options"})
        assert result["status"] == "no_data"

    def test_signals_high_iv(self) -> None:
        data = _make_options_data(iv_rank=85.0)
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=data)

        signal_types = [s["type"] for s in result["signals"]]
        assert "iv_high" in signal_types

    def test_signals_low_iv(self) -> None:
        data = _make_options_data(iv_rank=15.0)
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=data)

        signal_types = [s["type"] for s in result["signals"]]
        assert "iv_low" in signal_types

    def test_signals_skew_fear(self) -> None:
        data = _make_options_data(skew=0.12)
        data["skew_sentiment"] = "High Fear (put premium)"
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=data)

        signal_types = [s["type"] for s in result["signals"]]
        assert "skew_fear" in signal_types

    def test_signals_put_heavy(self) -> None:
        data = _make_options_data(oi_pc_ratio=1.8)
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=data)

        signal_types = [s["type"] for s in result["signals"]]
        assert "put_heavy" in signal_types

    def test_signals_call_heavy(self) -> None:
        data = _make_options_data(oi_pc_ratio=0.3)
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=data)

        signal_types = [s["type"] for s in result["signals"]]
        assert "call_heavy" in signal_types


class TestExpectedMoveBatch:
    """Test batch analysis."""

    def test_batch_summary(self) -> None:
        analyzer = ExpectedMoveAnalyzer()
        data_list = [
            _make_options_data("AAPL", atm_iv=0.25),
            _make_options_data("TSLA", price=200.0, atm_iv=0.55),
            _make_options_data("MSFT", atm_iv=0.20),
        ]
        result = analyzer.analyze_batch(data_list)

        assert result["summary"]["total_tickers"] == 3
        assert result["summary"]["analyzed"] == 3
        assert result["summary"]["highest_iv_ticker"] == "TSLA"
        assert result["summary"]["lowest_iv_ticker"] == "MSFT"

    def test_batch_with_error(self) -> None:
        analyzer = ExpectedMoveAnalyzer()
        data_list = [
            _make_options_data("AAPL"),
            {"ticker": "BAD", "error": "No data"},
        ]
        result = analyzer.analyze_batch(data_list)

        assert result["summary"]["total_tickers"] == 2
        assert result["summary"]["analyzed"] == 1


class TestTermStructure:
    """Test IV term structure analysis."""

    def _make_multi_expiry_data(
        self,
        near_iv: float = 0.30,
        far_iv: float = 0.25,
    ) -> dict:
        """Create options data with 2 expirations."""
        price = 150.0
        moves = []
        for iv, dte, exp in [(near_iv, 14, "2026-03-10"), (far_iv, 45, "2026-04-10")]:
            em = price * iv * math.sqrt(dte / 365)
            moves.append({
                "expiration": exp,
                "dte": dte,
                "atm_iv": iv,
                "atm_iv_pct": iv * 100,
                "expected_move": round(em, 2),
                "expected_move_pct": round(em / price * 100, 2),
                "sigma_1": {"upper": round(price + em, 2), "lower": round(price - em, 2), "probability": 68.2},
                "sigma_2": {"upper": round(price + em * 2, 2), "lower": round(price - em * 2, 2), "probability": 95.4},
                "iv_skew": {"otm_put_iv": None, "otm_call_iv": None, "skew": None},
                "oi_pc_ratio": 0.9,
                "volume_pc_ratio": 0.8,
            })

        return {
            "ticker": "AAPL",
            "current_price": price,
            "iv_rank": 50.0,
            "iv_level": "Normal",
            "skew_sentiment": "Neutral",
            "expirations_available": 5,
            "expected_moves": moves,
        }

    def test_inverted_term_structure(self) -> None:
        """Near IV > Far IV → inverted (stress signal)."""
        data = self._make_multi_expiry_data(near_iv=0.35, far_iv=0.22)
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=data)

        assert "term_structure" in result
        assert result["term_structure"]["shape"].startswith("Inverted")
        assert result["term_structure"]["near_far_ratio"] > 1.0

    def test_normal_term_structure(self) -> None:
        """Near IV ≈ Far IV → normal."""
        data = self._make_multi_expiry_data(near_iv=0.25, far_iv=0.26)
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=data)

        assert result["term_structure"]["shape"].startswith("Normal")

    def test_steep_contango(self) -> None:
        """Far IV >> Near IV → steep contango."""
        data = self._make_multi_expiry_data(near_iv=0.18, far_iv=0.35)
        analyzer = ExpectedMoveAnalyzer()
        result = analyzer.analyze("AAPL", options_data=data)

        assert "Contango" in result["term_structure"]["shape"]
