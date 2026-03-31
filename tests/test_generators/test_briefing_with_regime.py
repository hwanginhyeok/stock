"""Tests for generate_briefing() / _build_standup_section() with regime_result injection."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.analyzers.regime import RegimeResult
from src.generators.briefing_generator import (
    _build_standup_section,
    generate_briefing,
)


# ============================================================
# 공통 fixture
# ============================================================


def _make_regime_result(regime: str, confidence: float) -> RegimeResult:
    """테스트용 RegimeResult."""
    return RegimeResult(
        regime=regime,
        confidence=confidence,
        drivers=["BTC — MACD 히스토그램 하향", "ETH — ADX 32 (하락 추세)"],
        sizing={"TSLA": 0.25, "BTC": 0.15, "ETH": 0.10},
        raw_score=0.42,
    )


@pytest.fixture
def mock_db():
    """DB 접근을 patch — news_facts 테이블 없어도 테스트 가능."""
    empty_repo = MagicMock()
    empty_repo.get_recent_by_market.return_value = []
    with patch("src.generators.briefing_generator.NewsFactRepository",
               return_value=empty_repo):
        yield empty_repo


# ============================================================
# _build_standup_section — 포맷 검증 (I/O 없음)
# ============================================================


class TestBuildStandupSection:
    def test_risk_on_contains_regime(self):
        text = _build_standup_section(_make_regime_result("RISK_ON", 0.75))
        assert "RISK_ON" in text

    def test_risk_off_contains_regime(self):
        text = _build_standup_section(_make_regime_result("RISK_OFF", 0.65))
        assert "RISK_OFF" in text

    def test_confidence_percentage(self):
        text = _build_standup_section(_make_regime_result("NEUTRAL", 0.50))
        assert "50%" in text

    def test_sizing_all_tickers(self):
        text = _build_standup_section(_make_regime_result("RISK_ON", 0.8))
        assert "TSLA" in text
        assert "BTC" in text
        assert "ETH" in text

    def test_drivers_listed(self):
        text = _build_standup_section(_make_regime_result("RISK_ON", 0.8))
        assert "집중할 것" in text


# ============================================================
# generate_briefing() — DB mock 필요
# ============================================================


class TestGenerateBriefingWithRegime:
    def test_no_regime_no_standup(self, mock_db):
        """regime_result=None → 스탠드업 없음."""
        text = generate_briefing(
            schedule="morning",
            hours=1,
            fetch_market=False,
            regime_result=None,
        )
        assert "RISK_ON" not in text
        assert "RISK_OFF" not in text

    def test_with_regime_has_standup(self, mock_db):
        """regime_result 주입 → 스탠드업 포함."""
        regime = _make_regime_result("RISK_ON", 0.75)
        text = generate_briefing(
            schedule="morning",
            hours=1,
            fetch_market=False,
            regime_result=regime,
        )
        assert "RISK_ON" in text
        assert "TSLA" in text

    def test_briefing_body_still_present(self, mock_db):
        """스탠드업 추가 후에도 브리핑 본문 유지."""
        regime = _make_regime_result("NEUTRAL", 0.4)
        text = generate_briefing(
            schedule="morning",
            hours=1,
            fetch_market=False,
            regime_result=regime,
        )
        assert "시황 브리핑" in text or "브리핑" in text
