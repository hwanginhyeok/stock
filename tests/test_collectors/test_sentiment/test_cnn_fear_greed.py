"""Tests for CNN Fear & Greed collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.collectors.sentiment.cnn_fear_greed_collector import (
    CNNFearGreedCollector,
    _score_to_level,
)


class TestScoreToLevel:
    """Test fear/greed level classification."""

    @pytest.mark.parametrize(
        "score, expected",
        [
            (5, "Extreme Fear"),
            (15, "Extreme Fear"),
            (25, "Fear"),
            (35, "Fear"),
            (45, "Neutral"),
            (50, "Neutral"),
            (55, "Greed"),
            (65, "Greed"),
            (75, "Extreme Greed"),
            (90, "Extreme Greed"),
        ],
    )
    def test_level_mapping(self, score: float, expected: str) -> None:
        assert _score_to_level(score) == expected


class TestCNNFearGreedCollector:
    """Test CNN Fear & Greed collector with mocked HTTP."""

    @patch("src.collectors.sentiment.cnn_fear_greed_collector.requests.get")
    def test_collect_from_api_success(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "fear_and_greed": {
                "score": 45.5,
                "timestamp": "2026-02-24",
                "previous_close": 44.0,
                "previous_1_week": 40.0,
                "previous_1_month": 50.0,
                "previous_1_year": 55.0,
            },
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        collector = CNNFearGreedCollector()
        results = collector.collect()

        assert len(results) == 1
        assert results[0]["score"] == 45.5
        assert results[0]["level"] == "Neutral"
        assert results[0]["source"] == "cnn_api"

    @patch("src.collectors.sentiment.cnn_fear_greed_collector.requests.get")
    def test_collect_api_failure_falls_back_to_package(
        self, mock_get: MagicMock,
    ) -> None:
        mock_get.side_effect = Exception("API blocked")

        with patch(
            "src.collectors.sentiment.cnn_fear_greed_collector.CNNFearGreedCollector._fetch_from_package",
        ) as mock_pkg:
            mock_pkg.return_value = {
                "source": "fear_and_greed_package",
                "score": 30.0,
                "level": "Fear",
                "timestamp": "2026-02-24T00:00:00",
            }

            collector = CNNFearGreedCollector()
            results = collector.collect()

            assert len(results) == 1
            assert results[0]["source"] == "fear_and_greed_package"

    @patch("src.collectors.sentiment.cnn_fear_greed_collector.requests.get")
    def test_collect_total_failure(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = Exception("API blocked")

        with patch(
            "src.collectors.sentiment.cnn_fear_greed_collector.CNNFearGreedCollector._fetch_from_package",
        ) as mock_pkg:
            mock_pkg.return_value = {}

            collector = CNNFearGreedCollector()
            results = collector.collect()

            assert results == []
