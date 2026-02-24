"""Tests for Google Trends collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch, PropertyMock

import pandas as pd
import numpy as np
import pytest

from src.collectors.sentiment.google_trends_collector import GoogleTrendsCollector


def _make_trends_df(keyword: str, n: int = 7, base: int = 50) -> pd.DataFrame:
    """Create a synthetic Google Trends DataFrame."""
    dates = pd.date_range("2026-02-17", periods=n, freq="D")
    values = [base + i * 5 for i in range(n)]
    return pd.DataFrame({keyword: values, "isPartial": [False] * n}, index=dates)


class TestGoogleTrendsCollector:
    """Test Google Trends collector with mocked pytrends."""

    @patch("src.collectors.sentiment.google_trends_collector.GoogleTrendsCollector._get_client")
    def test_collect_stock_success(self, mock_client_method: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.interest_over_time.return_value = _make_trends_df("NVDA")
        mock_client_method.return_value = mock_client

        collector = GoogleTrendsCollector(request_delay_sec=0)
        result = collector.collect_stock("NVDA", geo="US")

        assert result["keyword"] == "NVDA"
        assert result["geo"] == "US"
        assert result["current_interest"] > 0
        assert result["average_interest"] > 0
        assert result["trend_direction"] in [
            "Surging", "Rising", "Stable", "Falling", "Declining", "N/A",
        ]
        assert result["spike_ratio"] > 0
        assert "sentiment_score" in result
        assert "error" not in result

    @patch("src.collectors.sentiment.google_trends_collector.GoogleTrendsCollector._get_client")
    def test_collect_stock_rising_trend(self, mock_client_method: MagicMock) -> None:
        """Test that steeply rising values produce Rising/Surging direction."""
        mock_client = MagicMock()
        # Create sharply rising data: 10, 20, 30, 40, 50, 80, 100
        dates = pd.date_range("2026-02-17", periods=7, freq="D")
        values = [10, 20, 30, 40, 50, 80, 100]
        df = pd.DataFrame({"TSLA": values, "isPartial": [False] * 7}, index=dates)
        mock_client.interest_over_time.return_value = df
        mock_client_method.return_value = mock_client

        collector = GoogleTrendsCollector(request_delay_sec=0)
        result = collector.collect_stock("TSLA")

        assert result["trend_direction"] in ("Surging", "Rising")
        assert result["spike_ratio"] > 1.0

    @patch("src.collectors.sentiment.google_trends_collector.GoogleTrendsCollector._get_client")
    def test_collect_stock_empty_data(self, mock_client_method: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.interest_over_time.return_value = pd.DataFrame()
        mock_client_method.return_value = mock_client

        collector = GoogleTrendsCollector(request_delay_sec=0)
        result = collector.collect_stock("UNKNOWN")

        assert result["current_interest"] == 0
        assert result["trend_direction"] == "N/A"

    @patch("src.collectors.sentiment.google_trends_collector.GoogleTrendsCollector._get_client")
    def test_collect_stock_api_error(self, mock_client_method: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.interest_over_time.side_effect = Exception("429 Too Many Requests")
        mock_client_method.return_value = mock_client

        collector = GoogleTrendsCollector(request_delay_sec=0)
        result = collector.collect_stock("AAPL")

        assert result["sentiment"] == "Unknown"
        assert "error" in result

    def test_collect_stock_no_pytrends(self) -> None:
        """Test graceful handling when pytrends is not installed."""
        collector = GoogleTrendsCollector(request_delay_sec=0)

        with patch.object(
            collector, "_get_client", side_effect=ImportError("No module named 'pytrends'"),
        ):
            result = collector.collect_stock("AAPL")

        assert result["sentiment"] == "Unknown"
        assert "error" in result

    @patch("src.collectors.sentiment.google_trends_collector.GoogleTrendsCollector._get_client")
    def test_collect_comparison(self, mock_client_method: MagicMock) -> None:
        mock_client = MagicMock()
        dates = pd.date_range("2026-02-17", periods=7, freq="D")
        df = pd.DataFrame(
            {
                "AAPL": [50, 55, 60, 58, 62, 65, 70],
                "MSFT": [30, 35, 32, 38, 40, 42, 45],
                "isPartial": [False] * 7,
            },
            index=dates,
        )
        mock_client.interest_over_time.return_value = df
        mock_client_method.return_value = mock_client

        collector = GoogleTrendsCollector(request_delay_sec=0)
        results = collector.collect_comparison(["AAPL", "MSFT"], geo="US")

        assert len(results) == 2
        assert results[0]["keyword"] == "AAPL"
        assert results[1]["keyword"] == "MSFT"
        # AAPL should have higher interest than MSFT
        assert results[0]["current_interest"] > results[1]["current_interest"]
