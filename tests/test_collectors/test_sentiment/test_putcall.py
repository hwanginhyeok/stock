"""Tests for CBOE Put/Call Ratio collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.collectors.sentiment.putcall_collector import (
    PutCallRatioCollector,
    _classify_putcall,
)


class TestClassifyPutCall:
    """Test put/call ratio sentiment classification."""

    @pytest.mark.parametrize(
        "ratio, expected",
        [
            (1.3, "Extreme Fear"),
            (1.1, "Fear"),
            (0.8, "Neutral"),
            (0.6, "Greed"),
            (0.4, "Extreme Greed"),
        ],
    )
    def test_classification(self, ratio: float, expected: str) -> None:
        assert _classify_putcall(ratio) == expected


class TestPutCallRatioCollector:
    """Test Put/Call collector with mocked HTTP."""

    @patch("src.collectors.sentiment.putcall_collector.requests.get")
    def test_collect_success(self, mock_get: MagicMock) -> None:
        csv_content = (
            "HEADER LINE 1\n"
            "HEADER LINE 2\n"
            "DATE,CALLS,PUTS,TOTAL,P/C Ratio\n"
            "02/20/2026,1500000,1200000,2700000,0.80\n"
            "02/21/2026,1600000,1100000,2700000,0.69\n"
        )

        mock_resp = MagicMock()
        mock_resp.text = csv_content
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        collector = PutCallRatioCollector()
        results = collector.collect()

        # Should have 3 results (total, equity, index) but all use same mock
        assert len(results) == 3
        for r in results:
            assert "pc_ratio" in r
            assert "sentiment" in r
            assert r["pc_ratio"] == 0.69

    @patch("src.collectors.sentiment.putcall_collector.requests.get")
    def test_collect_all_failure(self, mock_get: MagicMock) -> None:
        """All URLs fail — should return empty list."""
        mock_get.side_effect = Exception("Connection error")

        collector = PutCallRatioCollector()
        results = collector.collect()

        assert len(results) == 0
