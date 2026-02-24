"""Tests for sentiment analyzer — _parse_score and mocked analysis."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.analyzers.sentiment import SentimentAnalyzer
from src.core.models import NewsItem


class TestParseScore:
    """Test _parse_score static method."""

    def test_clean_number(self):
        assert SentimentAnalyzer._parse_score("0.75") == pytest.approx(0.75)

    def test_negative(self):
        assert SentimentAnalyzer._parse_score("-0.5") == pytest.approx(-0.5)

    def test_clamped_high(self):
        assert SentimentAnalyzer._parse_score("1.5") == pytest.approx(1.0)

    def test_clamped_low(self):
        assert SentimentAnalyzer._parse_score("-2.0") == pytest.approx(-1.0)

    def test_with_whitespace(self):
        assert SentimentAnalyzer._parse_score("  0.3  ") == pytest.approx(0.3)

    def test_embedded_number(self):
        assert SentimentAnalyzer._parse_score("Score: 0.6") == pytest.approx(0.6)

    def test_no_number(self):
        assert SentimentAnalyzer._parse_score("positive") == pytest.approx(0.0)

    def test_zero(self):
        assert SentimentAnalyzer._parse_score("0") == pytest.approx(0.0)


class TestSentimentAnalyzerMocked:
    """Test SentimentAnalyzer with mocked ClaudeClient."""

    def _make_analyzer(self):
        """Create SentimentAnalyzer with ClaudeClient mocked."""
        with patch("src.analyzers.sentiment.ClaudeClient"):
            return SentimentAnalyzer()

    def test_analyze_single(self):
        analyzer = self._make_analyzer()
        mock_response = SimpleNamespace(content="0.7")
        analyzer._client = MagicMock()
        analyzer._client.generate.return_value = mock_response

        item = NewsItem(title="Great earnings report", summary="Revenue up 50%")
        score = analyzer.analyze_single(item)
        assert score == pytest.approx(0.7)

    def test_analyze_single_failure(self):
        analyzer = self._make_analyzer()
        analyzer._client = MagicMock()
        analyzer._client.generate.side_effect = Exception("API error")

        item = NewsItem(title="Test")
        score = analyzer.analyze_single(item)
        assert score == 0.0

    def test_analyze_batch(self):
        analyzer = self._make_analyzer()
        mock_response = SimpleNamespace(content="0.5")
        analyzer._client = MagicMock()
        analyzer._client.generate.return_value = mock_response

        items = [NewsItem(title=f"News {i}") for i in range(3)]
        results = analyzer.analyze_batch(items)
        assert len(results) == 3
        assert all(s == pytest.approx(0.5) for _, s in results)

    def test_analyze_empty_items(self):
        analyzer = self._make_analyzer()
        result = analyzer.analyze("AAPL", news_items=[])
        assert result["average_sentiment"] == 0.0
        assert result["items"] == []
