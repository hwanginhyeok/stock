"""Tests for fundamental analysis — pure functions + yfinance mock."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.analyzers.fundamental import FundamentalAnalyzer
from src.core.models import Market


class TestResolvYfTicker:
    """Test _resolve_yf_ticker static method."""

    def test_us_ticker_unchanged(self):
        assert FundamentalAnalyzer._resolve_yf_ticker("AAPL", Market.US) == "AAPL"

    def test_korea_numeric_ticker(self):
        assert FundamentalAnalyzer._resolve_yf_ticker("005930", Market.KOREA) == "005930.KS"

    def test_korea_non_numeric(self):
        assert FundamentalAnalyzer._resolve_yf_ticker("SAMSUNG", Market.KOREA) == "SAMSUNG"


class TestExtractMetrics:
    """Test _extract_metrics static method."""

    def test_full_info(self):
        info = {
            "trailingPE": 15.5,
            "priceToBook": 3.2,
            "returnOnEquity": 0.25,
            "operatingMargins": 0.15,
            "revenueGrowth": 0.12,
            "earningsGrowth": 0.08,
            "marketCap": 2.5e12,
        }
        metrics = FundamentalAnalyzer._extract_metrics(info)
        assert metrics["per"] == pytest.approx(15.5)
        assert metrics["pbr"] == pytest.approx(3.2)
        assert metrics["roe"] == pytest.approx(0.25)

    def test_missing_fields(self):
        metrics = FundamentalAnalyzer._extract_metrics({})
        assert metrics["per"] is None
        assert metrics["roe"] is None

    def test_forward_pe_fallback(self):
        info = {"forwardPE": 20.0}
        metrics = FundamentalAnalyzer._extract_metrics(info)
        assert metrics["per"] == pytest.approx(20.0)


class TestComputeScore:
    """Test fundamental score computation (requires config mock)."""

    def test_good_fundamentals_high_score(self):
        analyzer = FundamentalAnalyzer()
        metrics = {
            "per": 10.0,
            "pbr": 1.5,
            "roe": 0.20,
            "operating_margin": 0.18,
            "revenue_growth": 0.15,
            "earnings_growth": 0.20,
        }
        score = analyzer._compute_score(metrics)
        assert score >= 60

    def test_poor_fundamentals_low_score(self):
        analyzer = FundamentalAnalyzer()
        metrics = {
            "per": 50.0,
            "pbr": 8.0,
            "roe": 0.02,
            "operating_margin": 0.02,
            "revenue_growth": -0.10,
            "earnings_growth": -0.20,
        }
        score = analyzer._compute_score(metrics)
        assert score <= 40

    def test_neutral_returns_near_50(self):
        analyzer = FundamentalAnalyzer()
        metrics = {
            "per": None,
            "pbr": None,
            "roe": None,
            "operating_margin": None,
            "revenue_growth": None,
            "earnings_growth": None,
        }
        score = analyzer._compute_score(metrics)
        assert 40 <= score <= 60

    def test_score_range(self):
        analyzer = FundamentalAnalyzer()
        metrics = {"per": 15, "pbr": 2, "roe": 0.15,
                    "operating_margin": 0.1, "revenue_growth": 0.05,
                    "earnings_growth": 0.1}
        score = analyzer._compute_score(metrics)
        assert 0 <= score <= 100


class TestFundamentalAnalyze:
    """Test analyze() with mocked yfinance."""

    def test_analyze_with_mock(self):
        analyzer = FundamentalAnalyzer()
        mock_info = {
            "trailingPE": 20.0,
            "priceToBook": 3.0,
            "returnOnEquity": 0.15,
            "operatingMargins": 0.12,
            "revenueGrowth": 0.08,
            "earningsGrowth": 0.10,
        }
        with patch.object(analyzer, "_fetch_info", return_value=mock_info):
            result = analyzer.analyze("AAPL", market=Market.US)
        assert "score" in result
        assert "data" in result
        assert 0 <= result["score"] <= 100

    def test_analyze_no_data(self):
        analyzer = FundamentalAnalyzer()
        with patch.object(analyzer, "_fetch_info", return_value={}):
            result = analyzer.analyze("BAD", market=Market.US)
        assert result["score"] == 50.0
