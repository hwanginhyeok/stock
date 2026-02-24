"""Tests for BaseGenerator utility methods."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.core.config import ArticleTypeConfig


class TestCheckProhibited:
    """Test _check_prohibited method."""

    def _make_generator(self):
        """Create a concrete generator for testing."""
        with patch("src.generators.base.ClaudeClient"):
            from src.generators.base import BaseGenerator

            class ConcreteGen(BaseGenerator):
                def generate(self, **kwargs):
                    return None

            return ConcreteGen()

    def test_no_prohibited(self):
        gen = self._make_generator()
        result = gen._check_prohibited("이 기사는 시장 분석입니다.")
        assert result == []

    def test_single_prohibited(self):
        gen = self._make_generator()
        result = gen._check_prohibited("이 종목을 꼭 사세요!")
        assert "꼭 사세요" in result

    def test_multiple_prohibited(self):
        gen = self._make_generator()
        text = "꼭 사세요! 지금 당장 매수하면 무조건 수익!"
        result = gen._check_prohibited(text)
        assert len(result) >= 2


class TestAppendDisclaimer:
    """Test _append_disclaimer method."""

    def _make_generator(self):
        with patch("src.generators.base.ClaudeClient"):
            from src.generators.base import BaseGenerator

            class ConcreteGen(BaseGenerator):
                def generate(self, **kwargs):
                    return None

            return ConcreteGen()

    def test_appends_ko_disclaimer(self):
        gen = self._make_generator()
        content = "오늘의 시장 분석 내용입니다."
        result = gen._append_disclaimer(content, lang="ko")
        assert "투자 참고용" in result
        assert "---" in result

    def test_no_double_append(self):
        gen = self._make_generator()
        content = "내용\n\n---\n※ 본 콘텐츠는 투자 참고용이며, 투자 판단의 책임은 본인에게 있습니다.\n"
        result = gen._append_disclaimer(content, lang="ko")
        # Should not add another disclaimer
        assert result.count("투자 참고용") == 1

    def test_english_disclaimer(self):
        gen = self._make_generator()
        content = "Market analysis content."
        result = gen._append_disclaimer(content, lang="en")
        assert "Disclaimer" in result


class TestComputeQualityScore:
    """Test _compute_quality_score method."""

    def _make_generator(self):
        with patch("src.generators.base.ClaudeClient"):
            from src.generators.base import BaseGenerator

            class ConcreteGen(BaseGenerator):
                def generate(self, **kwargs):
                    return None

            return ConcreteGen()

    def _make_config(self, min_len=800, max_len=1200):
        return ArticleTypeConfig(
            display_name="Test",
            min_length=min_len,
            max_length=max_len,
        )

    def test_perfect_length(self):
        gen = self._make_generator()
        config = self._make_config(100, 200)
        content = "x" * 150  # within range
        score = gen._compute_quality_score(content, config)
        assert score > 0

    def test_too_short_penalized(self):
        gen = self._make_generator()
        config = self._make_config(100, 200)
        content = "x" * 30
        score = gen._compute_quality_score(content, config)
        assert score < 50

    def test_structured_content_higher(self):
        gen = self._make_generator()
        config = self._make_config(50, 5000)
        structured = (
            "# 제목\n\n"
            "첫 번째 단락입니다.\n\n"
            "두 번째 단락입니다.\n\n"
            "세 번째 단락입니다.\n\n"
            "- 항목 1\n"
            "- 항목 2\n\n"
            "마무리입니다.\n\n"
            "---\n"
            "※ 본 콘텐츠는 투자 참고용이며, 투자 판단의 책임은 본인에게 있습니다.\n"
        )
        plain = "짧은 내용"
        score_structured = gen._compute_quality_score(structured, config)
        score_plain = gen._compute_quality_score(plain, config)
        assert score_structured > score_plain

    def test_score_range(self):
        gen = self._make_generator()
        config = self._make_config(100, 1000)
        score = gen._compute_quality_score("Some content here.", config)
        assert 0 <= score <= 100


class TestJinjaFilters:
    """Test custom Jinja2 filters."""

    def _make_generator(self):
        with patch("src.generators.base.ClaudeClient"):
            from src.generators.base import BaseGenerator

            class ConcreteGen(BaseGenerator):
                def generate(self, **kwargs):
                    return None

            return ConcreteGen()

    def test_format_number_int(self):
        from src.generators.base import BaseGenerator
        assert BaseGenerator._filter_format_number(1234567) == "1,234,567"

    def test_format_number_float(self):
        from src.generators.base import BaseGenerator
        assert BaseGenerator._filter_format_number(1234.5678, 2) == "1,234.57"

    def test_truncate_text_short(self):
        from src.generators.base import BaseGenerator
        assert BaseGenerator._filter_truncate_text("Hello", 100) == "Hello"

    def test_truncate_text_long(self):
        from src.generators.base import BaseGenerator
        result = BaseGenerator._filter_truncate_text("A" * 200, 100)
        assert len(result) == 100
        assert result.endswith("...")

    def test_sign_positive(self):
        from src.generators.base import BaseGenerator
        assert BaseGenerator._filter_sign(3.14) == "+3.14"

    def test_sign_negative(self):
        from src.generators.base import BaseGenerator
        assert BaseGenerator._filter_sign(-2.5) == "-2.5"

    def test_sign_zero(self):
        from src.generators.base import BaseGenerator
        assert BaseGenerator._filter_sign(0.0) == "0.0"
