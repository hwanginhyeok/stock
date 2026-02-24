"""Tests for Korea market collector — static methods."""

from __future__ import annotations

import pytest

from src.collectors.market.korea_collector import KoreaMarketCollector
from src.core.models import MarketSentiment


class TestClassifySentiment:
    """Test _classify_sentiment static method for Korea market."""

    def test_very_bullish(self):
        assert KoreaMarketCollector._classify_sentiment(2.5) == MarketSentiment.VERY_BULLISH

    def test_bullish(self):
        assert KoreaMarketCollector._classify_sentiment(1.0) == MarketSentiment.BULLISH

    def test_neutral(self):
        assert KoreaMarketCollector._classify_sentiment(0.2) == MarketSentiment.NEUTRAL

    def test_bearish(self):
        assert KoreaMarketCollector._classify_sentiment(-1.0) == MarketSentiment.BEARISH

    def test_very_bearish(self):
        assert KoreaMarketCollector._classify_sentiment(-2.5) == MarketSentiment.VERY_BEARISH

    def test_boundary_bullish(self):
        assert KoreaMarketCollector._classify_sentiment(2.0) == MarketSentiment.VERY_BULLISH

    def test_boundary_bearish(self):
        assert KoreaMarketCollector._classify_sentiment(-2.0) == MarketSentiment.VERY_BEARISH

    def test_boundary_neutral_positive(self):
        assert KoreaMarketCollector._classify_sentiment(0.5) == MarketSentiment.BULLISH

    def test_boundary_neutral_negative(self):
        assert KoreaMarketCollector._classify_sentiment(-0.5) == MarketSentiment.BEARISH

    def test_exact_zero(self):
        assert KoreaMarketCollector._classify_sentiment(0.0) == MarketSentiment.NEUTRAL
