"""Tests for ArticleGenerator — title extraction, ticker collection."""

from __future__ import annotations

import pytest

from src.core.models import Market, NewsItem, StockAnalysis
from src.generators.article import ArticleContext, ArticleGenerator


class TestExtractTitle:
    """Test _extract_title static method."""

    def test_heading_format(self):
        content = "# 오늘의 모닝브리핑\n\n본문 내용입니다."
        title, body = ArticleGenerator._extract_title(content)
        assert title == "오늘의 모닝브리핑"
        assert "본문 내용" in body
        assert "# " not in body

    def test_no_heading(self):
        content = "첫 번째 문장입니다. 두 번째 문장."
        title, body = ArticleGenerator._extract_title(content)
        assert title == "첫 번째 문장입니다."
        assert body == content

    def test_empty_content(self):
        title, body = ArticleGenerator._extract_title("")
        # Empty string → strip().split("\n") gives [''], first_line is ''
        assert title == ""

    def test_no_punctuation(self):
        content = "A title without punctuation\nSome body"
        title, body = ArticleGenerator._extract_title(content)
        # Should use first 80 chars as fallback
        assert len(title) <= 80

    def test_period_takes_precedence(self):
        # _extract_title checks ".", "!", "?" in order
        content = "Breaking News! Market surges.\nDetails follow."
        title, body = ArticleGenerator._extract_title(content)
        # "." is found first at end of "surges."
        assert "Breaking News" in title

    def test_exclamation_only(self):
        content = "Breaking News!\nDetails follow."
        title, body = ArticleGenerator._extract_title(content)
        # First line: "Breaking News!" — "." not found, "!" found at idx 14
        assert title == "Breaking News!"

    def test_question_only(self):
        content = "Will markets rally?\nAnalysis below."
        title, body = ArticleGenerator._extract_title(content)
        # First line has no ".", "!" found fails, "?" found
        assert title == "Will markets rally?"

    def test_multiline_heading(self):
        content = "# 주간 리뷰: 2026년 2월 셋째 주\n\n이번 주 시장은..."
        title, body = ArticleGenerator._extract_title(content)
        assert "주간 리뷰" in title


class TestCollectTickers:
    """Test _collect_tickers static method."""

    def test_from_analyses(self):
        ctx = ArticleContext(
            stock_analyses=[
                StockAnalysis(ticker="AAPL", name="Apple"),
                StockAnalysis(ticker="MSFT", name="Microsoft"),
            ],
        )
        tickers = ArticleGenerator._collect_tickers(ctx)
        assert "AAPL" in tickers
        assert "MSFT" in tickers

    def test_from_news(self):
        ctx = ArticleContext(
            news_items=[
                NewsItem(title="Test", related_tickers=["TSLA", "NVDA"]),
            ],
        )
        tickers = ArticleGenerator._collect_tickers(ctx)
        assert "TSLA" in tickers
        assert "NVDA" in tickers

    def test_deduplication(self):
        ctx = ArticleContext(
            stock_analyses=[StockAnalysis(ticker="AAPL", name="Apple")],
            news_items=[NewsItem(title="Test", related_tickers=["AAPL", "MSFT"])],
        )
        tickers = ArticleGenerator._collect_tickers(ctx)
        assert tickers.count("AAPL") == 1

    def test_sorted_output(self):
        ctx = ArticleContext(
            stock_analyses=[
                StockAnalysis(ticker="TSLA", name="Tesla"),
                StockAnalysis(ticker="AAPL", name="Apple"),
            ],
        )
        tickers = ArticleGenerator._collect_tickers(ctx)
        assert tickers == sorted(tickers)

    def test_empty_context(self):
        ctx = ArticleContext()
        assert ArticleGenerator._collect_tickers(ctx) == []


class TestResolveClaudeTask:
    """Test _resolve_claude_task static method."""

    def test_general(self):
        from src.core.models import ClaudeTask
        assert ArticleGenerator._resolve_claude_task("general") == ClaudeTask.GENERAL

    def test_deep_analysis(self):
        from src.core.models import ClaudeTask
        assert ArticleGenerator._resolve_claude_task("deep_analysis") == ClaudeTask.DEEP_ANALYSIS

    def test_unknown_defaults_general(self):
        from src.core.models import ClaudeTask
        assert ArticleGenerator._resolve_claude_task("unknown") == ClaudeTask.GENERAL
