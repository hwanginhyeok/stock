"""Integrated news pipeline: collect → dedup → ticker extract → sentiment → store."""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from src.analyzers.sentiment import SentimentAnalyzer
from src.collectors.news.dedup import TitleDeduplicator
from src.collectors.news.rss_collector import RSSNewsCollector
from src.collectors.news.ticker_extractor import TickerExtractor
from src.core.config import get_config
from src.core.logger import get_logger
from src.core.models import Importance, Market, NewsItem
from src.storage import NewsRepository

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    """Summary of a single pipeline execution.

    Attributes:
        collected: Total items fetched from RSS sources.
        duplicates_removed: Items dropped by deduplication.
        stored: Items persisted to the database.
        breaking_count: Items promoted to HIGH importance.
        tickers_found: Total ticker associations made.
        sentiment_analyzed: Items scored by sentiment analyzer.
        elapsed_sec: Wall-clock time for the pipeline run.
        errors: Non-fatal errors encountered during the run.
    """

    collected: int = 0
    duplicates_removed: int = 0
    stored: int = 0
    breaking_count: int = 0
    tickers_found: int = 0
    sentiment_analyzed: int = 0
    elapsed_sec: float = 0.0
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """Return a one-line human-readable summary."""
        parts = [
            f"수집 {self.collected}",
            f"중복제거 -{self.duplicates_removed}",
            f"저장 {self.stored}",
        ]
        if self.breaking_count:
            parts.append(f"브레이킹 {self.breaking_count}")
        if self.tickers_found:
            parts.append(f"티커매핑 {self.tickers_found}")
        if self.sentiment_analyzed:
            parts.append(f"감성분석 {self.sentiment_analyzed}")
        parts.append(f"{self.elapsed_sec:.1f}초")
        return " | ".join(parts)


# 브레이킹 뉴스 감지를 위한 키워드 추출 최소 길이
_MIN_KEYWORD_LEN = 4
# 동일 키워드가 이 수 이상의 소스에서 등장하면 브레이킹으로 판정
_BREAKING_SOURCE_THRESHOLD = 3
# 브레이킹 감지 시간 윈도우 (분)
_BREAKING_WINDOW_MIN = 60


class NewsPipeline:
    """End-to-end news collection pipeline.

    Orchestrates: RSS collection → deduplication → ticker extraction
    → optional sentiment analysis → DB persistence.

    Example::

        pipeline = NewsPipeline()
        result = pipeline.run(market=Market.US, analyze_sentiment=False)
        print(result.summary())
    """

    def __init__(self) -> None:
        self._config = get_config()
        self._collector = RSSNewsCollector()
        self._ticker_extractor = TickerExtractor()
        self._sentiment_analyzer: SentimentAnalyzer | None = None  # lazy init
        self._repo = NewsRepository()
        logger.info("news_pipeline_initialized")

    def run(
        self,
        market: Market | None = None,
        analyze_sentiment: bool = False,
    ) -> PipelineResult:
        """Execute the full pipeline.

        Args:
            market: Collect only for this market (None = both).
            analyze_sentiment: Run Claude sentiment scoring (costs API tokens).

        Returns:
            PipelineResult with execution metrics.
        """
        start = time.monotonic()
        result = PipelineResult()

        # Step 1: Collect
        try:
            if market:
                items = self._collector.collect_by_market(market)
            else:
                items = self._collector.collect()
            result.collected = len(items)
        except Exception as e:
            logger.error("pipeline_collection_failed", error=str(e))
            result.errors.append(f"수집 실패: {e}")
            result.elapsed_sec = round(time.monotonic() - start, 2)
            return result

        if not items:
            logger.info("pipeline_no_items_collected")
            result.elapsed_sec = round(time.monotonic() - start, 2)
            return result

        # Step 2: Dedup against DB (RSSNewsCollector.collect() handles internal dedup,
        # but collect_by_market() does not dedup against DB — do it here)
        existing_titles = self._repo.get_recent_titles(hours=24)
        if existing_titles:
            dedup = TitleDeduplicator(
                threshold=self._config.news_sources.collection.dedup_similarity_threshold,
            )
            before = len(items)
            items = [
                item for item in items
                if not dedup.is_duplicate(item.title, existing_titles)
            ]
            result.duplicates_removed = before - len(items)

        if not items:
            logger.info("pipeline_all_duplicates", removed=result.duplicates_removed)
            result.elapsed_sec = round(time.monotonic() - start, 2)
            return result

        # Step 3: Ticker extraction
        items = self._extract_and_assign_tickers(items)
        result.tickers_found = sum(len(i.related_tickers) for i in items)

        # Step 4: Breaking news detection
        items = self._detect_breaking(items)
        result.breaking_count = sum(
            1 for i in items if i.importance == Importance.HIGH
        )

        # Step 5: Optional sentiment analysis
        if analyze_sentiment:
            items = self._run_sentiment(items)
            result.sentiment_analyzed = len(items)

        # Step 6: Store to DB
        try:
            stored = self._repo.create_many(items)
            result.stored = len(stored)
        except Exception as e:
            logger.error("pipeline_storage_failed", error=str(e))
            result.errors.append(f"저장 실패: {e}")

        result.elapsed_sec = round(time.monotonic() - start, 2)

        logger.info(
            "pipeline_complete",
            summary=result.summary(),
            errors=len(result.errors),
        )
        return result

    def _extract_and_assign_tickers(
        self,
        items: list[NewsItem],
    ) -> list[NewsItem]:
        """Assign related_tickers to each item via keyword matching.

        Args:
            items: News items to process.

        Returns:
            Same items with related_tickers populated.
        """
        for item in items:
            tickers = self._ticker_extractor.extract(item)
            if tickers:
                item.related_tickers = tickers
        return items

    def _detect_breaking(self, items: list[NewsItem]) -> list[NewsItem]:
        """Detect breaking news by cross-source keyword frequency.

        If the same significant keyword appears in items from 3+ different
        sources within the current batch, promote those items to HIGH importance.

        Args:
            items: News items from this collection cycle.

        Returns:
            Items with importance potentially upgraded.
        """
        if len(items) < _BREAKING_SOURCE_THRESHOLD:
            return items

        # Build keyword → set of sources mapping
        keyword_sources: dict[str, set[str]] = {}
        keyword_items: dict[str, list[int]] = {}  # keyword → item indices

        for idx, item in enumerate(items):
            words = self._extract_keywords(item.title)
            for word in words:
                if word not in keyword_sources:
                    keyword_sources[word] = set()
                    keyword_items[word] = []
                keyword_sources[word].add(item.source)
                keyword_items[word].append(idx)

        # Find breaking keywords (3+ distinct sources)
        breaking_indices: set[int] = set()
        for word, sources in keyword_sources.items():
            if len(sources) >= _BREAKING_SOURCE_THRESHOLD:
                logger.info(
                    "breaking_keyword_detected",
                    keyword=word,
                    source_count=len(sources),
                    sources=list(sources),
                )
                for idx in keyword_items[word]:
                    breaking_indices.add(idx)

        # Promote matching items
        for idx in breaking_indices:
            items[idx].importance = Importance.HIGH

        return items

    @staticmethod
    def _extract_keywords(title: str) -> list[str]:
        """Extract significant keywords from a title for breaking detection.

        Filters out common stop words and short words.

        Args:
            title: News title string.

        Returns:
            List of significant keywords (lowercased).
        """
        # 한국어 + 영어 불용어
        stop_words = {
            # 한국어
            "오늘", "내일", "어제", "이번", "지난", "올해", "전년", "관련",
            "대비", "기준", "이후", "이전", "현재", "최근", "뉴스",
            # 영어
            "the", "and", "for", "are", "but", "not", "you", "all",
            "can", "had", "her", "was", "one", "our", "out", "has",
            "its", "this", "that", "with", "from", "they", "been",
            "have", "more", "will", "into", "over", "than", "also",
            "after", "before", "while", "about", "could", "would",
            "their", "which", "there", "other", "should", "stock",
            "market", "says", "report", "news",
        }

        import re
        # 한글 2글자 이상 또는 영어 3글자 이상 단어 추출
        words = re.findall(r"[가-힣]{2,}|[a-zA-Z]{3,}", title)
        return [
            w.lower() for w in words
            if len(w) >= _MIN_KEYWORD_LEN and w.lower() not in stop_words
        ]

    def _run_sentiment(self, items: list[NewsItem]) -> list[NewsItem]:
        """Run sentiment analysis on all items.

        Args:
            items: News items to analyze.

        Returns:
            Items with sentiment_score updated.
        """
        if self._sentiment_analyzer is None:
            self._sentiment_analyzer = SentimentAnalyzer()

        for item in items:
            try:
                score = self._sentiment_analyzer.analyze_single(item)
                item.sentiment_score = score
            except Exception as e:
                logger.warning(
                    "sentiment_analysis_item_failed",
                    title=item.title[:60],
                    error=str(e),
                )
        return items
