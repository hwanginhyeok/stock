"""Tests for Reddit sentiment collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.collectors.sentiment.reddit_collector import (
    RedditSentimentCollector,
    _estimate_sentiment_from_score,
    _extract_tickers,
)


class TestExtractTickers:
    """Test ticker extraction from text."""

    def test_basic_cashtags(self) -> None:
        text = "I'm buying $AAPL and $TSLA today"
        assert sorted(_extract_tickers(text)) == ["AAPL", "TSLA"]

    def test_no_tickers(self) -> None:
        assert _extract_tickers("No stocks mentioned here") == []

    def test_duplicate_removal(self) -> None:
        text = "$NVDA is great, $NVDA will moon"
        assert _extract_tickers(text) == ["NVDA"]

    def test_ignores_lowercase(self) -> None:
        text = "$aapl is not matched"
        assert _extract_tickers(text) == []

    def test_max_5_chars(self) -> None:
        text = "$GOOGL is fine but $TOOLONG is not"
        result = _extract_tickers(text)
        assert "GOOGL" in result
        assert "TOOLONG" not in result


class TestEstimateSentiment:
    """Test engagement-based sentiment estimation."""

    def test_high_engagement(self) -> None:
        score = _estimate_sentiment_from_score(
            score=5000, upvote_ratio=0.95, num_comments=500,
        )
        assert score > 0.7

    def test_low_engagement(self) -> None:
        score = _estimate_sentiment_from_score(
            score=1, upvote_ratio=0.3, num_comments=0,
        )
        assert score < 0.3

    def test_neutral_engagement(self) -> None:
        score = _estimate_sentiment_from_score(
            score=50, upvote_ratio=0.5, num_comments=10,
        )
        assert 0.3 <= score <= 0.7

    def test_zero_score(self) -> None:
        score = _estimate_sentiment_from_score(
            score=0, upvote_ratio=0.5, num_comments=0,
        )
        assert 0 <= score <= 1


class TestRedditSentimentCollector:
    """Test Reddit collector with mocked HTTP."""

    @patch("src.collectors.sentiment.reddit_collector.requests.get")
    def test_collect_stock_success(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "$AAPL to the moon!",
                            "selftext": "Very bullish on Apple",
                            "score": 500,
                            "upvote_ratio": 0.9,
                            "num_comments": 120,
                            "subreddit": "wallstreetbets",
                            "created_utc": 1700000000,
                            "permalink": "/r/wallstreetbets/post1",
                        },
                    },
                    {
                        "data": {
                            "title": "AAPL earnings report",
                            "selftext": "",
                            "score": 100,
                            "upvote_ratio": 0.75,
                            "num_comments": 30,
                            "subreddit": "wallstreetbets",
                            "created_utc": 1700001000,
                            "permalink": "/r/wallstreetbets/post2",
                        },
                    },
                ],
            },
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        collector = RedditSentimentCollector(
            subreddits=["wallstreetbets"],
            request_delay_sec=0,
        )
        result = collector.collect_stock("AAPL")

        assert result["symbol"] == "AAPL"
        assert result["source"] == "reddit"
        assert result["posts_count"] == 2
        assert result["avg_upvote_ratio"] > 0.5
        assert result["sentiment_score"] > 0

    @patch("src.collectors.sentiment.reddit_collector.requests.get")
    def test_collect_stock_api_error(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = Exception("Rate limited")

        collector = RedditSentimentCollector(
            subreddits=["wallstreetbets"],
            request_delay_sec=0,
        )
        result = collector.collect_stock("AAPL")

        assert result["posts_count"] == 0
        assert result["sentiment"] == "Unknown"

    @patch("src.collectors.sentiment.reddit_collector.requests.get")
    def test_collect_trending(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "$NVDA and $TSLA are moving",
                            "selftext": "Also $NVDA will keep running",
                            "score": 200,
                            "upvote_ratio": 0.85,
                            "num_comments": 50,
                            "subreddit": "stocks",
                            "created_utc": 1700000000,
                            "permalink": "/r/stocks/post1",
                        },
                    },
                    {
                        "data": {
                            "title": "$AAPL new product launch",
                            "selftext": "",
                            "score": 300,
                            "upvote_ratio": 0.9,
                            "num_comments": 80,
                            "subreddit": "stocks",
                            "created_utc": 1700001000,
                            "permalink": "/r/stocks/post2",
                        },
                    },
                ],
            },
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        collector = RedditSentimentCollector(
            subreddits=["stocks"],
            request_delay_sec=0,
        )
        trending = collector.collect_trending(limit=10)

        assert "NVDA" in trending
        assert "TSLA" in trending
        assert "AAPL" in trending
        assert trending["NVDA"] == 1  # deduped per post, 1 post mentions it
