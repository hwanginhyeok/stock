"""데이터 수집기 단위 테스트.

외부 API 호출 없이 모킹 기반으로 파싱 로직만 검증.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.core.models import Market, NewsItem


# ── 티커 추출기 테스트 ─────────────────────────────────────────


class TestTickerExtractor:
    """TickerExtractor 파싱 로직 테스트."""

    @pytest.fixture
    def extractor(self, mock_config):
        """watchlist를 주입한 TickerExtractor."""
        from src.core.config import WatchlistItem
        mock_config.market.korea.watchlist = [
            WatchlistItem(ticker="005930", name="삼성전자"),
            WatchlistItem(ticker="000660", name="SK하이닉스"),
        ]
        mock_config.market.us.watchlist = [
            WatchlistItem(ticker="AAPL", name="Apple"),
            WatchlistItem(ticker="TSLA", name="Tesla"),
            WatchlistItem(ticker="NVDA", name="NVIDIA"),
            WatchlistItem(ticker="META", name="Meta"),
        ]
        from src.collectors.news.ticker_extractor import TickerExtractor
        return TickerExtractor()

    def test_kr_ticker_from_name(self, extractor) -> None:
        """한글 종목명으로 KR 티커 추출."""
        item = NewsItem(title="삼성전자 4분기 영업이익 급증", market=Market.KOREA)
        assert "005930" in extractor.extract(item)

    def test_us_ticker_from_symbol(self, extractor) -> None:
        """영문 티커 심볼로 US 티커 추출."""
        item = NewsItem(title="TSLA surges 10% after earnings", market=Market.US)
        assert "TSLA" in extractor.extract(item)

    def test_us_ticker_from_company_name(self, extractor) -> None:
        """영문 회사명으로 US 티커 추출."""
        item = NewsItem(title="Apple announces new product line", market=Market.US)
        assert "AAPL" in extractor.extract(item)

    def test_multiple_tickers(self, extractor) -> None:
        """하나의 뉴스에서 여러 티커 추출."""
        item = NewsItem(
            title="삼성전자와 SK하이닉스 동반 상승",
            market=Market.KOREA,
        )
        tickers = extractor.extract(item)
        assert "005930" in tickers
        assert "000660" in tickers

    def test_no_match(self, extractor) -> None:
        """매칭 안 되면 빈 리스트."""
        item = NewsItem(title="오늘 날씨 맑음", market=Market.KOREA)
        assert extractor.extract(item) == []

    def test_empty_text(self, extractor) -> None:
        """빈 제목은 빈 리스트."""
        item = NewsItem(title="", market=Market.US)
        assert extractor.extract(item) == []

    def test_summary_also_scanned(self, extractor) -> None:
        """title + summary 모두 스캔."""
        item = NewsItem(
            title="반도체 시장 전망",
            summary="NVIDIA is leading the AI semiconductor market",
            market=Market.US,
        )
        assert "NVDA" in extractor.extract(item)

    def test_case_insensitive_us(self, extractor) -> None:
        """US 티커는 대소문자 무시."""
        item = NewsItem(title="tesla reports record deliveries", market=Market.US)
        assert "TSLA" in extractor.extract(item)

    def test_partial_match_prevented(self, extractor) -> None:
        """단어 경계 존재 — 부분 매칭 방지."""
        item = NewsItem(title="METADATA processing error", market=Market.US)
        assert "META" not in extractor.extract(item)


# ── 뉴스 파이프라인 테스트 ─────────────────────────────────────


class TestNewsPipeline:
    """NewsPipeline 통합 로직 테스트."""

    @pytest.fixture
    def pipeline(self):
        with patch("src.collectors.news.news_pipeline.RSSNewsCollector") as MockCollector, \
             patch("src.collectors.news.news_pipeline.NewsRepository") as MockRepo:
            mock_collector = MockCollector.return_value
            mock_collector.collect.return_value = [
                NewsItem(title="삼성전자 호실적", source="매일경제", market=Market.KOREA),
                NewsItem(title="Tesla beats estimates", source="CNBC", market=Market.US),
            ]
            mock_collector.collect_by_market.return_value = [
                NewsItem(title="삼성전자 호실적", source="매일경제", market=Market.KOREA),
            ]
            mock_collector.failed_sources = []

            mock_repo = MockRepo.return_value
            mock_repo.get_recent_titles.return_value = []
            mock_repo.create_many.side_effect = lambda items: items

            from src.collectors.news.news_pipeline import NewsPipeline
            return NewsPipeline()

    def test_pipeline_run_returns_result(self, pipeline) -> None:
        """파이프라인 실행 시 PipelineResult 반환."""
        from src.collectors.news.news_pipeline import PipelineResult
        result = pipeline.run()
        assert isinstance(result, PipelineResult)
        assert result.collected == 2
        assert result.stored == 2

    def test_pipeline_assigns_tickers(self, pipeline) -> None:
        """파이프라인이 티커를 자동 매핑."""
        result = pipeline.run()
        assert result.tickers_found > 0

    def test_pipeline_market_filter(self, pipeline) -> None:
        """시장 필터 적용 시 해당 시장만 수집."""
        result = pipeline.run(market=Market.KOREA)
        assert result.collected == 1

    def test_pipeline_handles_empty_collection(self) -> None:
        """수집 결과 0건이면 정상 종료."""
        with patch("src.collectors.news.news_pipeline.RSSNewsCollector") as MockCollector, \
             patch("src.collectors.news.news_pipeline.NewsRepository"):
            mock_collector = MockCollector.return_value
            mock_collector.collect.return_value = []
            mock_collector.failed_sources = []

            from src.collectors.news.news_pipeline import NewsPipeline
            pipeline = NewsPipeline()
            result = pipeline.run()
            assert result.collected == 0
            assert result.stored == 0

    def test_pipeline_handles_collection_exception(self) -> None:
        """수집 중 예외 발생 시 에러 기록 후 정상 종료."""
        with patch("src.collectors.news.news_pipeline.RSSNewsCollector") as MockCollector, \
             patch("src.collectors.news.news_pipeline.NewsRepository"):
            mock_collector = MockCollector.return_value
            mock_collector.collect.side_effect = RuntimeError("Network error")
            mock_collector.failed_sources = []

            from src.collectors.news.news_pipeline import NewsPipeline
            pipeline = NewsPipeline()
            result = pipeline.run()
            assert result.collected == 0
            assert len(result.errors) > 0

    def test_pipeline_dedup_removes_existing(self) -> None:
        """DB에 이미 있는 제목은 중복 제거."""
        with patch("src.collectors.news.news_pipeline.RSSNewsCollector") as MockCollector, \
             patch("src.collectors.news.news_pipeline.NewsRepository") as MockRepo:
            mock_collector = MockCollector.return_value
            mock_collector.collect.return_value = [
                NewsItem(title="이미 있는 뉴스", source="test", market=Market.KOREA),
            ]
            mock_collector.failed_sources = []

            mock_repo = MockRepo.return_value
            mock_repo.get_recent_titles.return_value = ["이미 있는 뉴스"]
            mock_repo.create_many.side_effect = lambda items: items

            from src.collectors.news.news_pipeline import NewsPipeline
            pipeline = NewsPipeline()
            result = pipeline.run()
            assert result.duplicates_removed == 1
            assert result.stored == 0


# ── 브레이킹 뉴스 감지 테스트 ─────────────────────────────────


class TestBreakingDetection:
    """브레이킹 뉴스 감지 로직 테스트."""

    def test_keyword_from_3_sources_triggers_breaking(self) -> None:
        """동일 키워드 3개+ 소스 → HIGH importance."""
        from src.core.models import Importance
        from src.collectors.news.news_pipeline import NewsPipeline

        items = [
            NewsItem(title="하이닉스 실적 발표", source="매일경제", market=Market.KOREA),
            NewsItem(title="하이닉스 영업이익 급증", source="서울경제", market=Market.KOREA),
            NewsItem(title="하이닉스 분기 실적 호조", source="연합뉴스", market=Market.KOREA),
        ]

        with patch("src.collectors.news.news_pipeline.RSSNewsCollector"), \
             patch("src.collectors.news.news_pipeline.NewsRepository"):
            pipeline = NewsPipeline()
            result = pipeline._detect_breaking(items)

        high_items = [i for i in result if i.importance == Importance.HIGH]
        assert len(high_items) == 3

    def test_keyword_from_2_sources_no_breaking(self) -> None:
        """2개 소스만이면 브레이킹 아님."""
        from src.core.models import Importance
        from src.collectors.news.news_pipeline import NewsPipeline

        items = [
            NewsItem(title="하이닉스 실적 발표", source="매일경제", market=Market.KOREA),
            NewsItem(title="하이닉스 영업이익 급증", source="서울경제", market=Market.KOREA),
        ]

        with patch("src.collectors.news.news_pipeline.RSSNewsCollector"), \
             patch("src.collectors.news.news_pipeline.NewsRepository"):
            pipeline = NewsPipeline()
            result = pipeline._detect_breaking(items)

        high_items = [i for i in result if i.importance == Importance.HIGH]
        assert len(high_items) == 0
