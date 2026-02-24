"""Tests for US market collector — static methods."""

from __future__ import annotations

import pytest

from src.collectors.market.us_collector import USMarketCollector
from src.core.models import MarketSentiment


class TestClassifySentiment:
    """Test _classify_sentiment static method."""

    def test_very_bullish(self):
        assert USMarketCollector._classify_sentiment(2.0) == MarketSentiment.VERY_BULLISH

    def test_bullish(self):
        assert USMarketCollector._classify_sentiment(0.5) == MarketSentiment.BULLISH

    def test_neutral(self):
        assert USMarketCollector._classify_sentiment(0.1) == MarketSentiment.NEUTRAL

    def test_bearish(self):
        assert USMarketCollector._classify_sentiment(-0.5) == MarketSentiment.BEARISH

    def test_very_bearish(self):
        assert USMarketCollector._classify_sentiment(-2.0) == MarketSentiment.VERY_BEARISH

    def test_boundary_bullish(self):
        assert USMarketCollector._classify_sentiment(1.5) == MarketSentiment.VERY_BULLISH

    def test_boundary_bearish(self):
        assert USMarketCollector._classify_sentiment(-1.5) == MarketSentiment.VERY_BEARISH

    def test_exact_zero(self):
        assert USMarketCollector._classify_sentiment(0.0) == MarketSentiment.NEUTRAL


class TestClassifyVixSentiment:
    """Test _classify_vix_sentiment static method."""

    def test_high_vix_very_bearish(self):
        assert USMarketCollector._classify_vix_sentiment(35) == MarketSentiment.VERY_BEARISH

    def test_elevated_vix_bearish(self):
        assert USMarketCollector._classify_vix_sentiment(22) == MarketSentiment.BEARISH

    def test_low_vix_very_bullish(self):
        assert USMarketCollector._classify_vix_sentiment(11) == MarketSentiment.VERY_BULLISH

    def test_slightly_low_vix_bullish(self):
        assert USMarketCollector._classify_vix_sentiment(14) == MarketSentiment.BULLISH

    def test_neutral_vix(self):
        assert USMarketCollector._classify_vix_sentiment(17) == MarketSentiment.NEUTRAL


class TestDaysToPeriod:
    """Test _days_to_period static method."""

    def test_5_days(self):
        assert USMarketCollector._days_to_period(5) == "5d"

    def test_7_days(self):
        assert USMarketCollector._days_to_period(7) == "5d"

    def test_30_days(self):
        assert USMarketCollector._days_to_period(30) == "1mo"

    def test_90_days(self):
        assert USMarketCollector._days_to_period(90) == "3mo"

    def test_120_days(self):
        assert USMarketCollector._days_to_period(120) == "6mo"

    def test_180_days(self):
        assert USMarketCollector._days_to_period(180) == "6mo"

    def test_365_days(self):
        assert USMarketCollector._days_to_period(365) == "1y"
