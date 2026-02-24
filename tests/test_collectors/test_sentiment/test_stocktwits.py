"""Tests for StockTwits sentiment collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.collectors.sentiment.stocktwits_collector import StockTwitsCollector


class TestStockTwitsCollector:
    """Test StockTwits collector with mocked HTTP."""

    @patch("src.collectors.sentiment.stocktwits_collector.requests.get")
    def test_collect_stock_success(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "messages": [
                {"entities": {"sentiment": {"basic": "Bullish"}}},
                {"entities": {"sentiment": {"basic": "Bullish"}}},
                {"entities": {"sentiment": {"basic": "Bearish"}}},
                {"entities": {"sentiment": None}},
                {"entities": {}},
            ],
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        collector = StockTwitsCollector()
        result = collector.collect_stock("AAPL")

        assert result["symbol"] == "AAPL"
        assert result["bullish"] == 2
        assert result["bearish"] == 1
        assert result["neutral"] == 2
        assert result["messages_count"] == 5
        # 2 bullish / (2+1) tagged = 0.667
        assert result["sentiment_score"] == 0.667
        assert result["sentiment"] == "Bullish"

    @patch("src.collectors.sentiment.stocktwits_collector.requests.get")
    def test_collect_stock_all_bearish(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "messages": [
                {"entities": {"sentiment": {"basic": "Bearish"}}},
                {"entities": {"sentiment": {"basic": "Bearish"}}},
            ],
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        collector = StockTwitsCollector()
        result = collector.collect_stock("TSLA")

        assert result["sentiment_score"] == 0.0
        assert result["sentiment"] == "Very Bearish"

    @patch("src.collectors.sentiment.stocktwits_collector.requests.get")
    def test_collect_stock_no_sentiment_tags(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "messages": [
                {"entities": {}},
                {"entities": {}},
            ],
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        collector = StockTwitsCollector()
        result = collector.collect_stock("NVDA")

        assert result["sentiment_score"] == 0.5
        assert result["sentiment"] == "Neutral"

    @patch("src.collectors.sentiment.stocktwits_collector.requests.get")
    def test_collect_stock_api_error(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = Exception("Rate limited")

        collector = StockTwitsCollector()
        result = collector.collect_stock("AAPL")

        assert result["messages_count"] == 0
        assert "error" in result
