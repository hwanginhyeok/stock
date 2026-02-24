"""Tests for StockScreener — recommendation + mocked sub-analyzers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.analyzers.screener import StockScreener


class TestClassifyRecommendation:
    """Test _classify_recommendation static method."""

    def test_strong_positive(self):
        assert StockScreener._classify_recommendation(85) == "strong_positive"

    def test_positive(self):
        assert StockScreener._classify_recommendation(65) == "positive"

    def test_neutral(self):
        assert StockScreener._classify_recommendation(45) == "neutral"

    def test_negative(self):
        assert StockScreener._classify_recommendation(30) == "negative"

    def test_boundary_80(self):
        assert StockScreener._classify_recommendation(80) == "strong_positive"

    def test_boundary_60(self):
        assert StockScreener._classify_recommendation(60) == "positive"

    def test_boundary_40(self):
        assert StockScreener._classify_recommendation(40) == "neutral"


class TestScreenerAnalyze:
    """Test analyze() with mocked sub-analyzers."""

    def _make_ohlcv(self, n: int = 60) -> pd.DataFrame:
        rng = np.random.default_rng(42)
        close = 100 + np.cumsum(rng.normal(0, 1, n))
        return pd.DataFrame({
            "Open": close, "High": close + 1, "Low": close - 1,
            "Close": close, "Volume": [1e7] * n,
        })

    def test_analyze_composite_score(self):
        screener = StockScreener()
        screener._technical.analyze = MagicMock(return_value={
            "score": 70.0, "signals": ["MACD bullish"], "indicators": {},
        })
        screener._fundamental.analyze = MagicMock(return_value={
            "score": 80.0, "data": {},
        })
        result = screener.analyze("AAPL", ohlcv=self._make_ohlcv())
        assert result["score"] == pytest.approx(75.0)  # 70*0.5 + 80*0.5
        assert result["recommendation"] == "positive"

    def test_analyze_no_ohlcv(self):
        screener = StockScreener()
        screener._fundamental.analyze = MagicMock(return_value={"score": 60.0, "data": {}})
        result = screener.analyze("AAPL", ohlcv=None)
        assert result["technical_score"] == 50.0  # fallback

    def test_analyze_tech_failure(self):
        screener = StockScreener()
        screener._technical.analyze = MagicMock(side_effect=Exception("crash"))
        screener._fundamental.analyze = MagicMock(return_value={"score": 60.0, "data": {}})
        result = screener.analyze("AAPL", ohlcv=self._make_ohlcv())
        assert result["technical_score"] == 50.0  # fallback
