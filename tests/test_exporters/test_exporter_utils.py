"""Tests for Excel exporter utility functions."""

from __future__ import annotations

from openpyxl.styles import PatternFill

from src.exporters.base import format_market_cap, pct_color_font, score_fill


class TestScoreFill:
    """Test score_fill() color mapping."""

    def test_high_score_green(self):
        fill = score_fill(85)
        assert isinstance(fill, PatternFill)
        assert fill.start_color.rgb == "00C6EFCE"

    def test_medium_high_blue(self):
        fill = score_fill(65)
        assert fill.start_color.rgb == "00D6E4F0"

    def test_medium_low_yellow(self):
        fill = score_fill(45)
        assert fill.start_color.rgb == "00FFF2CC"

    def test_low_score_red(self):
        fill = score_fill(30)
        assert fill.start_color.rgb == "00FFC7CE"

    def test_boundary_80(self):
        fill = score_fill(80)
        assert fill.start_color.rgb == "00C6EFCE"

    def test_boundary_60(self):
        fill = score_fill(60)
        assert fill.start_color.rgb == "00D6E4F0"

    def test_boundary_40(self):
        fill = score_fill(40)
        assert fill.start_color.rgb == "00FFF2CC"

    def test_zero(self):
        fill = score_fill(0)
        assert fill.start_color.rgb == "00FFC7CE"


class TestFormatMarketCap:
    """Test format_market_cap() number formatting."""

    def test_trillion(self):
        assert format_market_cap(3.45e12) == "$3.45T"

    def test_billion(self):
        assert format_market_cap(890e9) == "$890.0B"

    def test_million(self):
        assert format_market_cap(50e6) == "$50M"

    def test_small(self):
        assert format_market_cap(123456) == "$123,456"

    def test_none(self):
        assert format_market_cap(None) == "N/A"

    def test_zero(self):
        assert format_market_cap(0) == "N/A"

    def test_one_trillion(self):
        assert format_market_cap(1e12) == "$1.00T"

    def test_one_billion(self):
        assert format_market_cap(1e9) == "$1.0B"


class TestPctColorFont:
    """Test pct_color_font() color based on sign."""

    def test_positive_green(self):
        font = pct_color_font(1.5)
        assert font.color.rgb == "00548235"

    def test_negative_red(self):
        font = pct_color_font(-2.0)
        assert font.color.rgb == "00C00000"

    def test_zero_gray(self):
        font = pct_color_font(0.0)
        assert font.color.rgb == "00808080"

    def test_bold(self):
        font = pct_color_font(1.0, bold=True)
        assert font.bold is True
