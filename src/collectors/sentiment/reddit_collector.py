"""Reddit community sentiment collector for US stocks."""

from __future__ import annotations

import re
import time
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors.sentiment.base import BaseSentimentCollector

# Reddit JSON API (no auth required for public subreddits)
_REDDIT_SEARCH_URL = (
    "https://www.reddit.com/r/{subreddit}/search.json"
)
_REDDIT_HOT_URL = (
    "https://www.reddit.com/r/{subreddit}/hot.json"
)

_HEADERS = {
    "User-Agent": "StockRichBot/1.0 (stock sentiment analysis)",
}

# Target subreddits for stock sentiment
_DEFAULT_SUBREDDITS = ["wallstreetbets", "stocks", "investing"]

# Regex to extract tickers from post text ($AAPL, $TSLA, etc.)
_TICKER_PATTERN = re.compile(r"\$([A-Z]{1,5})\b")


def _extract_tickers(text: str) -> list[str]:
    """Extract stock ticker mentions from text.

    Matches cashtag format ($AAPL, $TSLA) commonly used on Reddit.

    Args:
        text: Post title or body text.

    Returns:
        List of unique ticker symbols found.
    """
    return list(set(_TICKER_PATTERN.findall(text)))


def _estimate_sentiment_from_score(
    score: int,
    upvote_ratio: float,
    num_comments: int,
) -> float:
    """Estimate post sentiment from Reddit engagement metrics.

    High upvote ratio + high score = community agrees with the post.
    This is a rough proxy — actual sentiment requires NLP on the text.

    Args:
        score: Net upvotes (upvotes - downvotes).
        upvote_ratio: Proportion of upvotes (0.0-1.0).
        num_comments: Number of comments.

    Returns:
        Engagement score 0.0-1.0 (higher = more positive engagement).
    """
    # Normalize score: log scale to handle viral posts
    import math
    score_norm = min(1.0, math.log1p(max(0, score)) / 10)

    # Upvote ratio directly maps to agreement
    ratio_score = upvote_ratio

    # Comment engagement (more discussion = more interest, not necessarily positive)
    comment_norm = min(1.0, math.log1p(num_comments) / 8)

    # Weighted combination
    return round(score_norm * 0.3 + ratio_score * 0.5 + comment_norm * 0.2, 3)


class RedditSentimentCollector(BaseSentimentCollector):
    """Collect community sentiment from Reddit finance subreddits.

    Uses Reddit's public JSON API (no authentication required).
    Collects recent posts from r/wallstreetbets, r/stocks, r/investing
    and extracts ticker mentions with engagement metrics.
    """

    def __init__(
        self,
        subreddits: list[str] | None = None,
        request_delay_sec: float = 2.0,
    ) -> None:
        """Initialize with configurable subreddits and delay.

        Args:
            subreddits: List of subreddit names to scrape.
            request_delay_sec: Delay between requests (Reddit rate limit).
        """
        super().__init__()
        self._subreddits = subreddits or _DEFAULT_SUBREDDITS
        self._delay = request_delay_sec

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch_subreddit(
        self,
        subreddit: str,
        query: str | None = None,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Fetch posts from a subreddit.

        Args:
            subreddit: Subreddit name (without r/).
            query: Optional search query. If None, fetches hot posts.
            limit: Number of posts to fetch.

        Returns:
            List of post data dicts.

        Raises:
            requests.RequestException: On network errors.
        """
        if query:
            url = _REDDIT_SEARCH_URL.format(subreddit=subreddit)
            params = {
                "q": query,
                "sort": "new",
                "limit": limit,
                "restrict_sr": "true",
                "t": "week",
            }
        else:
            url = _REDDIT_HOT_URL.format(subreddit=subreddit)
            params = {"limit": limit}

        resp = requests.get(
            url, params=params, headers=_HEADERS, timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            posts.append({
                "title": post.get("title", ""),
                "selftext": post.get("selftext", "")[:500],
                "score": post.get("score", 0),
                "upvote_ratio": post.get("upvote_ratio", 0.5),
                "num_comments": post.get("num_comments", 0),
                "subreddit": subreddit,
                "created_utc": post.get("created_utc", 0),
                "permalink": post.get("permalink", ""),
            })

        return posts

    def collect_stock(self, symbol: str) -> dict[str, Any]:
        """Collect Reddit sentiment for a specific stock ticker.

        Searches all configured subreddits for posts mentioning the ticker.

        Args:
            symbol: Stock ticker (e.g., "AAPL").

        Returns:
            Dict with ticker, post count, engagement metrics, and sentiment.
        """
        all_posts: list[dict[str, Any]] = []

        for sub in self._subreddits:
            try:
                posts = self._fetch_subreddit(sub, query=f"${symbol} OR {symbol}")
                all_posts.extend(posts)
                time.sleep(self._delay)
            except Exception as e:
                self._logger.warning(
                    "reddit_fetch_failed",
                    subreddit=sub,
                    symbol=symbol,
                    error=str(e),
                )

        if not all_posts:
            return {
                "symbol": symbol,
                "source": "reddit",
                "posts_count": 0,
                "avg_score": 0,
                "avg_upvote_ratio": 0.5,
                "sentiment_score": 0.5,
                "sentiment": "Unknown",
                "subreddits": self._subreddits,
            }

        # Calculate aggregate sentiment from engagement metrics
        scores = [
            _estimate_sentiment_from_score(
                p["score"], p["upvote_ratio"], p["num_comments"],
            )
            for p in all_posts
        ]
        avg_engagement = sum(scores) / len(scores) if scores else 0.5
        avg_score = sum(p["score"] for p in all_posts) / len(all_posts)
        avg_ratio = sum(p["upvote_ratio"] for p in all_posts) / len(all_posts)

        # Classify
        if avg_engagement >= 0.7:
            sentiment_label = "Very Bullish"
        elif avg_engagement >= 0.55:
            sentiment_label = "Bullish"
        elif avg_engagement >= 0.45:
            sentiment_label = "Neutral"
        elif avg_engagement >= 0.3:
            sentiment_label = "Bearish"
        else:
            sentiment_label = "Very Bearish"

        self._logger.info(
            "reddit_collected",
            symbol=symbol,
            posts=len(all_posts),
            engagement=round(avg_engagement, 3),
            sentiment=sentiment_label,
        )

        return {
            "symbol": symbol,
            "source": "reddit",
            "posts_count": len(all_posts),
            "avg_score": round(avg_score, 1),
            "avg_upvote_ratio": round(avg_ratio, 3),
            "sentiment_score": round(avg_engagement, 3),
            "sentiment": sentiment_label,
            "subreddits": self._subreddits,
        }

    def collect_trending(self, limit: int = 50) -> dict[str, int]:
        """Collect trending ticker mentions across all subreddits.

        Fetches hot posts and counts ticker mentions to find
        what the community is currently discussing most.

        Args:
            limit: Number of hot posts per subreddit.

        Returns:
            Dict of ticker -> mention count, sorted descending.
        """
        ticker_counts: dict[str, int] = {}

        for sub in self._subreddits:
            try:
                posts = self._fetch_subreddit(sub, limit=limit)
                for post in posts:
                    text = f"{post['title']} {post['selftext']}"
                    tickers = _extract_tickers(text)
                    for t in tickers:
                        ticker_counts[t] = ticker_counts.get(t, 0) + 1
                time.sleep(self._delay)
            except Exception as e:
                self._logger.warning(
                    "reddit_trending_failed",
                    subreddit=sub,
                    error=str(e),
                )

        # Sort by count descending
        sorted_tickers = dict(
            sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True),
        )

        self._logger.info(
            "reddit_trending_collected",
            unique_tickers=len(sorted_tickers),
            top_5=list(sorted_tickers.items())[:5],
        )

        return sorted_tickers

    def collect(self) -> list[dict[str, Any]]:
        """Collect Reddit sentiment for configured US watchlist stocks.

        Returns:
            List of per-ticker sentiment dicts.
        """
        us_watchlist = self._config.market.us.watchlist
        results: list[dict[str, Any]] = []

        for item in us_watchlist:
            if item.ticker.startswith("^"):
                continue
            data = self.collect_stock(item.ticker)
            results.append(data)

        return results
