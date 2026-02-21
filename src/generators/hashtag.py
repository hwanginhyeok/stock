"""Hashtag generator combining config defaults, ticker tags, and AI topic tags."""

from __future__ import annotations

import re
from typing import Any

from src.core.models import ClaudeTask, Market
from src.generators.base import BaseGenerator

_TOPIC_SYSTEM_PROMPT = (
    "당신은 SNS 해시태그 전문가입니다. "
    "주어진 금융 콘텐츠에서 핵심 토픽을 추출하여 해시태그로 만들어 주세요. "
    "해시태그만 공백으로 구분하여 반환하세요 (예: #AI반도체 #금리인하 #실적발표). "
    "투자 권유성 해시태그는 사용하지 마세요."
)


class HashtagGenerator(BaseGenerator):
    """Generate hashtags from three sources.

    Combines:
    1. Default tags from SNS config.
    2. Ticker-based tags (stock symbol/name).
    3. AI-generated topic tags via Claude Haiku.
    """

    def generate(self, **kwargs: Any) -> list[str]:
        """Generate hashtags.

        Args:
            **kwargs: Must include ``content`` (str). Optional:
                ``article_type`` (str), ``market`` (str), ``tickers`` (list),
                ``max_count`` (int).

        Returns:
            List of hashtag strings.
        """
        return self.generate_hashtags(
            content=kwargs["content"],
            article_type=kwargs.get("article_type", ""),
            market=kwargs.get("market", "korea"),
            tickers=kwargs.get("tickers", []),
            max_count=kwargs.get("max_count", 30),
        )

    def generate_hashtags(
        self,
        content: str,
        article_type: str = "",
        market: str = "korea",
        tickers: list[str] | None = None,
        max_count: int = 30,
    ) -> list[str]:
        """Generate combined hashtags from all sources.

        Args:
            content: Article content for topic extraction.
            article_type: Article type string (for context).
            market: Market identifier ("korea" or "us").
            tickers: List of stock ticker symbols.
            max_count: Maximum number of hashtags to return.

        Returns:
            Deduplicated, normalized list of hashtags.
        """
        tickers = tickers or []
        all_tags: list[str] = []

        # 1. Default hashtags from config
        all_tags.extend(self._get_default_hashtags())

        # 2. Ticker-based hashtags
        all_tags.extend(self._generate_ticker_hashtags(tickers, market))

        # 3. AI-generated topic hashtags
        topic_count = max(3, max_count - len(all_tags))
        all_tags.extend(self._generate_topic_hashtags(content, count=topic_count))

        # Normalize and deduplicate
        normalized = self._normalize_hashtags(all_tags)

        return normalized[:max_count]

    def _get_default_hashtags(self) -> list[str]:
        """Get default hashtags from SNS config.

        Returns:
            List of default hashtag strings.
        """
        # Try Instagram config first (has more tags), then X
        ig_tags = self._config.sns.instagram.hashtag.default_tags
        if ig_tags:
            return list(ig_tags)
        x_tags = self._config.sns.x.hashtag.default_tags
        return list(x_tags)

    @staticmethod
    def _generate_ticker_hashtags(
        tickers: list[str],
        market: str = "korea",
    ) -> list[str]:
        """Generate hashtags from stock tickers.

        Args:
            tickers: List of ticker symbols.
            market: Market for formatting context.

        Returns:
            List of ticker-based hashtags.
        """
        tags: list[str] = []
        for ticker in tickers:
            # Clean ticker symbol
            clean = ticker.strip().replace(" ", "")
            if not clean:
                continue
            tags.append(f"#{clean}")
        return tags

    def _generate_topic_hashtags(
        self,
        content: str,
        count: int = 5,
    ) -> list[str]:
        """Extract topic hashtags from content using Claude Haiku.

        Args:
            content: Article content.
            count: Number of topic hashtags to generate.

        Returns:
            List of AI-generated topic hashtags. Empty on failure.
        """
        if not content.strip():
            return []

        # Truncate very long content
        truncated = content[:2000] if len(content) > 2000 else content
        user_message = (
            f"다음 금융 콘텐츠에서 핵심 토픽 {count}개를 추출하여 "
            f"한국어 해시태그로 만들어 주세요. "
            f"해시태그만 공백으로 구분하여 반환하세요.\n\n{truncated}"
        )

        try:
            raw = self._generate_content(
                ClaudeTask.SUMMARY,
                user_message,
                _TOPIC_SYSTEM_PROMPT,
            )
            return self._parse_hashtags(raw)
        except Exception as e:
            self._logger.warning(
                "topic_hashtag_generation_failed",
                error=str(e),
            )
            return []

    @staticmethod
    def _parse_hashtags(raw: str) -> list[str]:
        """Parse hashtags from raw AI output.

        Args:
            raw: Raw model output string.

        Returns:
            List of parsed hashtag strings.
        """
        # Find all hashtag patterns
        tags = re.findall(r"#[\w가-힣]+", raw)
        return tags

    @staticmethod
    def _normalize_hashtags(tags: list[str]) -> list[str]:
        """Normalize and deduplicate hashtags.

        Ensures each tag starts with ``#``, removes duplicates while
        preserving order.

        Args:
            tags: Raw hashtag list.

        Returns:
            Normalized, deduplicated list.
        """
        seen: set[str] = set()
        normalized: list[str] = []
        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue
            if not tag.startswith("#"):
                tag = f"#{tag}"
            # Remove special characters except Korean, alphanumeric, underscore
            tag = re.sub(r"[^\w가-힣#]", "", tag)
            lower_tag = tag.lower()
            if lower_tag not in seen and len(tag) > 1:
                seen.add(lower_tag)
                normalized.append(tag)
        return normalized
