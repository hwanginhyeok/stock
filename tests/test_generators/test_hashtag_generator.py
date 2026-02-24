"""Tests for HashtagGenerator — parsing, normalization, ticker tags."""

from __future__ import annotations

import pytest

from src.generators.hashtag import HashtagGenerator


class TestParseHashtags:
    """Test _parse_hashtags static method."""

    def test_basic(self):
        raw = "#AI반도체 #금리인하 #실적발표"
        result = HashtagGenerator._parse_hashtags(raw)
        assert len(result) == 3
        assert "#AI반도체" in result

    def test_mixed_content(self):
        raw = "핵심 토픽: #테슬라 주가가 올랐습니다 #전기차"
        result = HashtagGenerator._parse_hashtags(raw)
        assert "#테슬라" in result
        assert "#전기차" in result

    def test_no_hashtags(self):
        raw = "No hashtags here at all"
        result = HashtagGenerator._parse_hashtags(raw)
        assert result == []

    def test_english_hashtags(self):
        raw = "#Apple #NVIDIA #semiconductor"
        result = HashtagGenerator._parse_hashtags(raw)
        assert len(result) == 3


class TestNormalizeHashtags:
    """Test _normalize_hashtags static method."""

    def test_add_hash_prefix(self):
        result = HashtagGenerator._normalize_hashtags(["주식", "투자"])
        assert all(t.startswith("#") for t in result)

    def test_deduplicate(self):
        result = HashtagGenerator._normalize_hashtags(["#주식", "#주식", "#투자"])
        assert len(result) == 2

    def test_case_insensitive_dedup(self):
        result = HashtagGenerator._normalize_hashtags(["#Apple", "#apple"])
        assert len(result) == 1

    def test_remove_empty(self):
        result = HashtagGenerator._normalize_hashtags(["#valid", "", "  ", "#ok"])
        assert len(result) == 2

    def test_strip_whitespace(self):
        result = HashtagGenerator._normalize_hashtags(["  #주식  ", "#투자  "])
        assert "#주식" in result

    def test_single_char_removed(self):
        result = HashtagGenerator._normalize_hashtags(["#"])
        assert result == []


class TestGenerateTickerHashtags:
    """Test _generate_ticker_hashtags static method."""

    def test_basic(self):
        result = HashtagGenerator._generate_ticker_hashtags(["AAPL", "TSLA"])
        assert "#AAPL" in result
        assert "#TSLA" in result

    def test_empty_tickers(self):
        result = HashtagGenerator._generate_ticker_hashtags([])
        assert result == []

    def test_whitespace_ticker(self):
        result = HashtagGenerator._generate_ticker_hashtags(["  AAPL  "])
        assert "#AAPL" in result

    def test_blank_ticker_skipped(self):
        result = HashtagGenerator._generate_ticker_hashtags(["AAPL", "", "  "])
        assert len(result) == 1
