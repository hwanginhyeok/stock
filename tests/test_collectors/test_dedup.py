"""Tests for title-based deduplication."""

from __future__ import annotations

import pytest

from src.collectors.news.dedup import TitleDeduplicator
from src.core.models import NewsItem


class TestTitleDeduplicator:
    """Test TitleDeduplicator fuzzy matching."""

    def test_exact_duplicate(self):
        dedup = TitleDeduplicator(threshold=0.85)
        assert dedup.is_duplicate("삼성전자 실적 발표", ["삼성전자 실적 발표"])

    def test_near_duplicate(self):
        dedup = TitleDeduplicator(threshold=0.85)
        assert dedup.is_duplicate(
            "삼성전자 2분기 실적 발표",
            ["삼성전자 2분기 실적 발표했다"],
        )

    def test_not_duplicate(self):
        dedup = TitleDeduplicator(threshold=0.85)
        assert not dedup.is_duplicate(
            "삼성전자 반도체 투자",
            ["애플 아이폰 출시"],
        )

    def test_case_insensitive(self):
        dedup = TitleDeduplicator(threshold=0.85)
        assert dedup.is_duplicate("Apple EARNINGS Report", ["apple earnings report"])

    def test_whitespace_normalization(self):
        dedup = TitleDeduplicator(threshold=0.85)
        assert dedup.is_duplicate("  Some Title  ", ["some title"])

    def test_empty_existing(self):
        dedup = TitleDeduplicator(threshold=0.85)
        assert not dedup.is_duplicate("Any Title", [])

    def test_custom_threshold_low(self):
        dedup = TitleDeduplicator(threshold=0.5)
        # Even loosely similar titles should match with low threshold
        assert dedup.is_duplicate("반도체 시장 전망", ["반도체 시장 분석 전망"])

    def test_custom_threshold_high(self):
        dedup = TitleDeduplicator(threshold=0.99)
        # Nearly identical needed
        assert not dedup.is_duplicate("반도체 시장 전망", ["반도체 시장 분석"])


class TestDeduplicateList:
    """Test deduplicate() method on list of NewsItem."""

    def test_removes_duplicates(self):
        dedup = TitleDeduplicator(threshold=0.85)
        items = [
            NewsItem(title="삼성전자 실적 호조"),
            NewsItem(title="삼성전자 실적 호조 발표"),
            NewsItem(title="애플 신제품 출시"),
        ]
        result = dedup.deduplicate(items)
        assert len(result) == 2

    def test_keeps_first_occurrence(self):
        dedup = TitleDeduplicator(threshold=0.85)
        items = [
            NewsItem(title="First version of news"),
            NewsItem(title="First version of news!"),
        ]
        result = dedup.deduplicate(items)
        assert result[0].title == "First version of news"

    def test_all_unique(self):
        dedup = TitleDeduplicator(threshold=0.85)
        items = [
            NewsItem(title="뉴스 A"),
            NewsItem(title="뉴스 B"),
            NewsItem(title="뉴스 C"),
        ]
        result = dedup.deduplicate(items)
        assert len(result) == 3

    def test_empty_list(self):
        dedup = TitleDeduplicator(threshold=0.85)
        assert dedup.deduplicate([]) == []

    def test_single_item(self):
        dedup = TitleDeduplicator(threshold=0.85)
        items = [NewsItem(title="Only one")]
        result = dedup.deduplicate(items)
        assert len(result) == 1
