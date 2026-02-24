"""Tests for RSS collector internal parsing methods."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from src.collectors.news.rss_collector import RSSNewsCollector


class TestExtractText:
    """Test _extract_text static method (HTML → plain text)."""

    def test_simple_html(self):
        html = "<p>Hello <b>World</b></p>"
        assert RSSNewsCollector._extract_text(html) == "Hello World"

    def test_nested_tags(self):
        html = "<div><p>Paragraph <a href='#'>link</a></p></div>"
        assert RSSNewsCollector._extract_text(html) == "Paragraph link"

    def test_whitespace_normalization(self):
        html = "<p>Hello    World</p>"
        assert RSSNewsCollector._extract_text(html) == "Hello World"

    def test_empty_string(self):
        assert RSSNewsCollector._extract_text("") == ""

    def test_plain_text(self):
        assert RSSNewsCollector._extract_text("No HTML here") == "No HTML here"

    def test_special_entities(self):
        html = "<p>Price &gt; $100 &amp; rising</p>"
        result = RSSNewsCollector._extract_text(html)
        assert ">" in result
        assert "&" in result

    def test_multiline_html(self):
        html = "<p>Line1</p>\n<p>Line2</p>"
        result = RSSNewsCollector._extract_text(html)
        assert "Line1" in result
        assert "Line2" in result


class TestParseDate:
    """Test _parse_date static method."""

    def test_valid_parsed_time(self):
        entry = SimpleNamespace(
            published_parsed=(2026, 2, 22, 10, 30, 0, 0, 0, 0),
        )
        result = RSSNewsCollector._parse_date(entry)
        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 2
        assert result.tzinfo == timezone.utc

    def test_no_parsed_time(self):
        entry = SimpleNamespace()
        assert RSSNewsCollector._parse_date(entry) is None

    def test_none_parsed(self):
        entry = SimpleNamespace(published_parsed=None)
        assert RSSNewsCollector._parse_date(entry) is None

    def test_invalid_parsed(self):
        entry = SimpleNamespace(published_parsed="not a tuple")
        # Should not crash
        result = RSSNewsCollector._parse_date(entry)
        assert result is None or isinstance(result, datetime)
