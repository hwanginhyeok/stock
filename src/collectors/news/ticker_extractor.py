"""Ticker extraction from news text using watchlist keyword matching."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.core.config import get_config
from src.core.logger import get_logger
from src.core.models import Market, NewsItem

logger = get_logger(__name__)


@dataclass(frozen=True)
class _TickerPattern:
    """Pre-compiled regex pattern mapped to a ticker symbol."""

    ticker: str
    pattern: re.Pattern[str]
    market: Market


class TickerExtractor:
    """Extract related tickers from news item text.

    Builds regex patterns from the watchlist in market_config.yaml.
    Supports both Korean company names and English ticker symbols.

    Example::

        extractor = TickerExtractor()
        tickers = extractor.extract(news_item)
        # ["005930"] for "삼성전자 실적 호조"
        # ["TSLA", "AAPL"] for "Tesla and Apple beat estimates"
    """

    def __init__(self) -> None:
        config = get_config()
        self._patterns: list[_TickerPattern] = []
        self._build_patterns(config.market.korea.watchlist, Market.KOREA)
        self._build_patterns(config.market.us.watchlist, Market.US)
        logger.info(
            "ticker_extractor_initialized",
            pattern_count=len(self._patterns),
        )

    def _build_patterns(
        self,
        watchlist: list,
        market: Market,
    ) -> None:
        """Build regex patterns from a watchlist.

        Args:
            watchlist: List of WatchlistItem(ticker, name).
            market: Market enum for the watchlist.
        """
        for item in watchlist:
            ticker = item.ticker
            name = item.name

            if market == Market.KOREA:
                # KR: 한글 종목명으로 매칭 (단어 경계 불필요 — 한글은 자체 경계)
                if name:
                    pat = re.compile(re.escape(name))
                    self._patterns.append(_TickerPattern(ticker, pat, market))
                # 숫자 티커도 매칭 (뉴스에 종목코드가 나오는 경우)
                pat = re.compile(rf"\b{re.escape(ticker)}\b")
                self._patterns.append(_TickerPattern(ticker, pat, market))
            else:
                # US: 티커 심볼 매칭 (대문자 단어 경계)
                pat = re.compile(rf"\b{re.escape(ticker)}\b", re.IGNORECASE)
                self._patterns.append(_TickerPattern(ticker, pat, market))
                # 영문 회사명 매칭
                if name:
                    pat = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
                    self._patterns.append(_TickerPattern(ticker, pat, market))

    def extract(self, news_item: NewsItem) -> list[str]:
        """Extract ticker symbols from a news item's title and summary.

        Args:
            news_item: NewsItem to analyze.

        Returns:
            Deduplicated list of ticker strings found in the text.
        """
        text = f"{news_item.title} {news_item.summary}"
        return self.extract_from_text(text)

    def extract_from_text(self, text: str) -> list[str]:
        """Extract ticker symbols from arbitrary text.

        Args:
            text: Text to scan for ticker mentions.

        Returns:
            Deduplicated list of ticker strings.
        """
        if not text:
            return []

        found: dict[str, None] = {}  # ordered set
        for tp in self._patterns:
            if tp.pattern.search(text):
                found[tp.ticker] = None

        return list(found.keys())

    def extract_batch(self, items: list[NewsItem]) -> dict[str, list[str]]:
        """Extract tickers for a batch of news items.

        Args:
            items: List of NewsItem to process.

        Returns:
            Dict mapping news item ID to list of found tickers.
        """
        results: dict[str, list[str]] = {}
        for item in items:
            tickers = self.extract(item)
            results[item.id] = tickers
        return results
