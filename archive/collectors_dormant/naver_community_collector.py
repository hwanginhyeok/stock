"""Naver Finance discussion board (종목토론실) collector."""

from __future__ import annotations

import time
from typing import Any

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors.sentiment.base import BaseSentimentCollector

# Naver Finance discussion board URL pattern
# stock_code is the 6-digit KOSPI/KOSDAQ code (e.g., "005930" for Samsung)
_DISCUSSION_URL = (
    "https://finance.naver.com/item/board.naver"
    "?code={stock_code}&page={page}"
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://finance.naver.com/",
}


class NaverCommunityCollector(BaseSentimentCollector):
    """Collect community opinions from Naver Finance discussion boards.

    Scrapes the 종목토론실 (stock discussion board) for individual
    Korean stocks. Each post has a title, date, views, and
    upvote/downvote counts.

    Note:
        This collector respects rate limits with configurable delays
        between requests. robots.txt compliance should be verified
        before deployment.
    """

    def __init__(self, request_delay_sec: float = 1.0) -> None:
        """Initialize with configurable request delay.

        Args:
            request_delay_sec: Seconds to wait between HTTP requests.
        """
        super().__init__()
        self._delay = request_delay_sec

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch_page(self, stock_code: str, page: int = 1) -> str:
        """Fetch a single discussion board page.

        Args:
            stock_code: 6-digit Korean stock code.
            page: Page number (1-based).

        Returns:
            Raw HTML string.

        Raises:
            requests.RequestException: On network errors.
        """
        url = _DISCUSSION_URL.format(stock_code=stock_code, page=page)
        resp = requests.get(url, timeout=15, headers=_HEADERS)
        resp.raise_for_status()
        return resp.text

    def _parse_posts(self, html: str) -> list[dict[str, Any]]:
        """Parse discussion board posts from HTML.

        Args:
            html: Raw HTML from Naver Finance discussion page.

        Returns:
            List of post dicts with title, date, views, agree, disagree.
        """
        soup = BeautifulSoup(html, "html.parser")
        posts: list[dict[str, Any]] = []

        table = soup.select_one("table.type2")
        if not table:
            return posts

        rows = table.select("tr")
        for row in rows:
            cells = row.select("td")
            if len(cells) < 6:
                continue

            # Column layout: 날짜 | 제목 | 글쓴이 | 조회 | 공감 | 비공감
            title_cell = cells[1]
            title_link = title_cell.select_one("a.tit")
            if not title_link:
                continue

            title = title_link.get_text(strip=True)
            date_text = cells[0].get_text(strip=True)

            try:
                views = int(cells[3].get_text(strip=True).replace(",", ""))
            except (ValueError, IndexError):
                views = 0

            try:
                agree = int(cells[4].get_text(strip=True).replace(",", ""))
            except (ValueError, IndexError):
                agree = 0

            try:
                disagree = int(cells[5].get_text(strip=True).replace(",", ""))
            except (ValueError, IndexError):
                disagree = 0

            posts.append({
                "title": title,
                "date": date_text,
                "views": views,
                "agree": agree,
                "disagree": disagree,
            })

        return posts

    def collect_stock(
        self,
        stock_code: str,
        stock_name: str = "",
        pages: int = 3,
    ) -> dict[str, Any]:
        """Collect discussion posts for a single stock.

        Args:
            stock_code: 6-digit Korean stock code (e.g., "005930").
            stock_name: Display name (e.g., "삼성전자").
            pages: Number of pages to scrape (default 3, ~60 posts).

        Returns:
            Dict with stock info, posts, and aggregate sentiment metrics.
        """
        all_posts: list[dict[str, Any]] = []

        for page in range(1, pages + 1):
            try:
                html = self._fetch_page(stock_code, page)
                posts = self._parse_posts(html)
                all_posts.extend(posts)
                time.sleep(self._delay)
            except Exception as e:
                self._logger.warning(
                    "naver_page_fetch_failed",
                    stock_code=stock_code,
                    page=page,
                    error=str(e),
                )
                break

        # Aggregate sentiment from agree/disagree votes
        total_agree = sum(p["agree"] for p in all_posts)
        total_disagree = sum(p["disagree"] for p in all_posts)
        total_votes = total_agree + total_disagree

        if total_votes > 0:
            bullish_ratio = total_agree / total_votes
        else:
            bullish_ratio = 0.5

        # Classify
        if bullish_ratio >= 0.7:
            community_sentiment = "Very Bullish"
        elif bullish_ratio >= 0.55:
            community_sentiment = "Bullish"
        elif bullish_ratio >= 0.45:
            community_sentiment = "Neutral"
        elif bullish_ratio >= 0.3:
            community_sentiment = "Bearish"
        else:
            community_sentiment = "Very Bearish"

        self._logger.info(
            "naver_community_collected",
            stock_code=stock_code,
            stock_name=stock_name,
            posts=len(all_posts),
            bullish_ratio=round(bullish_ratio, 3),
            sentiment=community_sentiment,
        )

        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "posts_count": len(all_posts),
            "posts": all_posts,
            "total_agree": total_agree,
            "total_disagree": total_disagree,
            "bullish_ratio": round(bullish_ratio, 3),
            "sentiment": community_sentiment,
        }

    def collect(self) -> list[dict[str, Any]]:
        """Collect community data for configured Korean watchlist stocks.

        Reads stock codes from the Korea market watchlist configuration.

        Returns:
            List of per-stock community sentiment dicts.
        """
        korea_watchlist = self._config.market.korea.watchlist
        results: list[dict[str, Any]] = []

        for item in korea_watchlist:
            # Extract 6-digit code from ticker (e.g., "005930")
            stock_code = item.ticker.replace(".KS", "").replace(".KQ", "")
            if not stock_code.isdigit():
                self._logger.debug(
                    "skipping_non_numeric_ticker",
                    ticker=item.ticker,
                )
                continue

            data = self.collect_stock(
                stock_code=stock_code,
                stock_name=item.name,
                pages=2,
            )
            results.append(data)

        return results
