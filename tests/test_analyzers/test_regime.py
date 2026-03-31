"""Tests for MarketRegimeEngine — normalization functions & fallback behavior."""

from __future__ import annotations

import pytest

from src.analyzers.regime import (
    MarketRegimeEngine,
    RegimeResult,
    _normalize_adx,
    _normalize_dxy,
    _normalize_fred_liquidity,
    _normalize_macd_histogram,
    _normalize_rsi,
    _normalize_supertrend,
)


# ============================================================
# Normalization functions
# ============================================================


class TestNormalizeRsi:
    # RSI 정규화는 역방향(매수 기회 관점):
    #   과매도(< 35) → +1 (추가 매수 신호), 과매수(> 70) → -1 (위험 신호)
    def test_extreme_high_is_negative(self):
        """RSI 80(과매수) → -1 (위험 신호)."""
        assert _normalize_rsi(80.0) == pytest.approx(-1.0)

    def test_extreme_low_is_positive(self):
        """RSI 20(과매도) → +1 (매수 기회)."""
        assert _normalize_rsi(20.0) == pytest.approx(1.0)

    def test_neutral_range(self):
        """RSI 52.5 → 0 근방."""
        result = _normalize_rsi(52.5)
        assert -0.1 < result < 0.1

    def test_output_clipped_low(self):
        """RSI 0 → +1 (과매도 최극단)."""
        assert _normalize_rsi(0.0) == pytest.approx(1.0)

    def test_output_clipped_high(self):
        """RSI 100 → -1 (과매수 최극단)."""
        assert _normalize_rsi(100.0) == pytest.approx(-1.0)


class TestNormalizeMacdHistogram:
    def test_positive_large(self):
        assert _normalize_macd_histogram(2000.0) == pytest.approx(1.0)

    def test_negative_large(self):
        assert _normalize_macd_histogram(-2000.0) == pytest.approx(-1.0)

    def test_zero(self):
        assert _normalize_macd_histogram(0.0) == pytest.approx(0.0)


class TestNormalizeAdx:
    def test_strong_trend(self):
        # ADX > 40 → magnitude near 1.0 (direction from stub)
        result = _normalize_adx(50.0, True)
        assert result == pytest.approx(1.0)

    def test_strong_downtrend(self):
        result = _normalize_adx(50.0, False)
        assert result == pytest.approx(-1.0)

    def test_weak_trend(self):
        result = _normalize_adx(10.0, True)
        assert -0.3 < result < 0.3


class TestNormalizeSupertrend:
    def test_bullish(self):
        assert _normalize_supertrend(True) == pytest.approx(1.0)

    def test_bearish(self):
        assert _normalize_supertrend(False) == pytest.approx(-1.0)


class TestNormalizeFredLiquidity:
    # WoW 변화량: > 0 → 1.0, < 0 → -1.0, 0 → 0.0 (이진 분류)
    def test_positive_change(self):
        """유동성 증가 → +1."""
        assert _normalize_fred_liquidity(300.0) == pytest.approx(1.0)

    def test_negative_change(self):
        """유동성 감소 → -1."""
        assert _normalize_fred_liquidity(-300.0) == pytest.approx(-1.0)

    def test_zero(self):
        """변화 없음 → 0."""
        assert _normalize_fred_liquidity(0.0) == pytest.approx(0.0)

    def test_none(self):
        """None → 0 (fallback)."""
        assert _normalize_fred_liquidity(None) == pytest.approx(0.0)


class TestNormalizeDxy:
    # _normalize_dxy는 DXY 절댓값이 아닌 5일 모멘텀(%)를 입력받음
    def test_strong_dollar_momentum(self):
        """달러 강세(+1%) → -1 (위험자산 역풍)."""
        result = _normalize_dxy(1.0)
        assert result <= -1.0

    def test_weak_dollar_momentum(self):
        """달러 약세(-1%) → +1 (위험자산 순풍)."""
        result = _normalize_dxy(-1.0)
        assert result >= 1.0

    def test_neutral_range(self):
        """±0.5% 이내 → 0."""
        result = _normalize_dxy(0.3)
        assert result == pytest.approx(0.0)


# ============================================================
# RegimeResult dataclass
# ============================================================


class TestRegimeResult:
    def test_fields_present(self):
        result = RegimeResult(
            regime="RISK_ON",
            confidence=0.8,
            drivers={"technical": 0.5},
            sizing={"TSLA": 0.25},
            raw_score=0.45,
        )
        assert result.regime == "RISK_ON"
        assert result.confidence == 0.8
        assert result.raw_score == pytest.approx(0.45)


# ============================================================
# MarketRegimeEngine.compute() — fallback behavior
# ============================================================


class TestMarketRegimeEngineCompute:
    """All external I/O is mocked so tests run without network/DB."""

    _DEFAULT_CONFIG = {
        "weights": {
            "technical": 0.40,
            "fred_liquidity": 0.25,
            "fx": 0.20,
            "news_sentiment": 0.15,
        },
        "thresholds": {"risk_on": 0.3, "risk_off": -0.3},
        "positions": {
            "RISK_ON": {"TSLA": 0.25, "BTC": 0.15, "ETH": 0.10},
            "NEUTRAL": {"TSLA": 0.15, "BTC": 0.10, "ETH": 0.07},
            "RISK_OFF": {"TSLA": 0.08, "BTC": 0.05, "ETH": 0.03},
        },
    }

    def test_risk_on_threshold(self, monkeypatch):
        """모든 factor가 +1 → 합산 1.0 > 0.3 → RISK_ON."""
        engine = MarketRegimeEngine()
        monkeypatch.setattr(engine, "_compute_technical_score", lambda: (1.0, []))
        monkeypatch.setattr(engine, "_compute_fred_score", lambda: (1.0, ""))
        monkeypatch.setattr(engine, "_compute_fx_score", lambda: (1.0, ""))
        monkeypatch.setattr(engine, "_compute_sentiment_score", lambda: (1.0, ""))
        result = engine.compute()
        assert result is not None
        assert result.regime == "RISK_ON"

    def test_risk_off_threshold(self, monkeypatch):
        """모든 factor가 -1 → 합산 -1.0 < -0.3 → RISK_OFF."""
        engine = MarketRegimeEngine()
        monkeypatch.setattr(engine, "_compute_technical_score", lambda: (-1.0, []))
        monkeypatch.setattr(engine, "_compute_fred_score", lambda: (-1.0, ""))
        monkeypatch.setattr(engine, "_compute_fx_score", lambda: (-1.0, ""))
        monkeypatch.setattr(engine, "_compute_sentiment_score", lambda: (-1.0, ""))
        result = engine.compute()
        assert result is not None
        assert result.regime == "RISK_OFF"

    def test_neutral_threshold(self, monkeypatch):
        """모든 factor가 0 → 합산 0.0 → NEUTRAL."""
        engine = MarketRegimeEngine()
        monkeypatch.setattr(engine, "_compute_technical_score", lambda: (0.0, []))
        monkeypatch.setattr(engine, "_compute_fred_score", lambda: (0.0, ""))
        monkeypatch.setattr(engine, "_compute_fx_score", lambda: (0.0, ""))
        monkeypatch.setattr(engine, "_compute_sentiment_score", lambda: (0.0, ""))
        result = engine.compute()
        assert result is not None
        assert result.regime == "NEUTRAL"

    def test_compute_returns_none_on_crash(self, monkeypatch):
        """compute() 내부 전체 예외 → None 반환."""
        engine = MarketRegimeEngine()

        def _crash():
            raise RuntimeError("total crash")

        # 모든 factor가 동시에 예외를 던져도 compute()는 None 반환해야 함
        # 현재 구현은 factor별 fallback이 아닌 전체 try/except라 모두 실패시 None
        monkeypatch.setattr(engine, "_compute_technical_score", _crash)
        monkeypatch.setattr(engine, "_compute_fred_score", lambda: (0.0, ""))
        monkeypatch.setattr(engine, "_compute_fx_score", lambda: (0.0, ""))
        monkeypatch.setattr(engine, "_compute_sentiment_score", lambda: (0.0, ""))

        result = engine.compute()
        assert result is None

    def test_result_has_sizing(self, monkeypatch):
        """RISK_ON 시 sizing에 TSLA/BTC/ETH 포함."""
        engine = MarketRegimeEngine()
        monkeypatch.setattr(engine, "_compute_technical_score", lambda: (1.0, []))
        monkeypatch.setattr(engine, "_compute_fred_score", lambda: (1.0, ""))
        monkeypatch.setattr(engine, "_compute_fx_score", lambda: (1.0, ""))
        monkeypatch.setattr(engine, "_compute_sentiment_score", lambda: (1.0, ""))
        result = engine.compute()
        assert result is not None
        assert "TSLA" in result.sizing
        assert "BTC" in result.sizing
        assert "ETH" in result.sizing
