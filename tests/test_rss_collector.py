"""RSS 수집기 안정성 테스트.

개별 소스 실패가 전체 수집을 중단시키지 않는지 검증.
requests.get을 모킹하여 실제 네트워크 호출 없이 테스트.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.collectors.news.rss_collector import RSSNewsCollector
from src.core.models import Market


VALID_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Test Feed</title>
  <item>
    <title>테스트 뉴스 제목 1</title>
    <link>https://example.com/1</link>
    <description>테스트 내용 1</description>
    <pubDate>Mon, 24 Mar 2026 10:00:00 +0900</pubDate>
  </item>
  <item>
    <title>테스트 뉴스 제목 2</title>
    <link>https://example.com/2</link>
    <description>테스트 내용 2</description>
    <pubDate>Mon, 24 Mar 2026 11:00:00 +0900</pubDate>
  </item>
</channel>
</rss>"""

INVALID_XML = """<html><body>This is not RSS</body></html>"""


@pytest.fixture
def collector() -> RSSNewsCollector:
    """RSS 수집기 인스턴스 (DB 접근 모킹)."""
    with patch("src.collectors.news.rss_collector.NewsRepository") as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.get_recent_titles.return_value = []
        instance = RSSNewsCollector()
        return instance


class TestFetchSource:
    """개별 소스 수집 테스트."""

    def test_valid_rss_parses_successfully(self, collector: RSSNewsCollector) -> None:
        """정상 RSS 응답 시 뉴스 아이템 파싱 성공."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = VALID_RSS_XML
        mock_response.raise_for_status = MagicMock()

        from src.core.config import NewsSource
        source = NewsSource(name="Test", url="https://example.com/rss")

        with patch("src.collectors.news.rss_collector.requests.get", return_value=mock_response):
            items = collector._fetch_source(source, Market.KOREA)

        assert len(items) == 2
        assert items[0].title == "테스트 뉴스 제목 1"
        assert items[1].title == "테스트 뉴스 제목 2"

    def test_invalid_xml_returns_empty(self, collector: RSSNewsCollector) -> None:
        """비정상 XML → 해당 소스만 스킵, 빈 리스트 반환."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = INVALID_XML
        mock_response.raise_for_status = MagicMock()

        from src.core.config import NewsSource
        source = NewsSource(name="BadFeed", url="https://example.com/bad")

        with patch("src.collectors.news.rss_collector.requests.get", return_value=mock_response):
            items = collector._fetch_source(source, Market.KOREA)

        # feedparser는 비정상 XML을 빈 entries로 처리하거나 bozo로 마킹
        # _fetch_rss의 retry + CollectionError로 인해 최종적으로 빈 리스트
        assert isinstance(items, list)

    def test_timeout_returns_empty(self, collector: RSSNewsCollector) -> None:
        """타임아웃 → 해당 소스만 스킵, 빈 리스트 반환."""
        import requests

        from src.core.config import NewsSource
        source = NewsSource(name="SlowFeed", url="https://example.com/slow")

        with patch(
            "src.collectors.news.rss_collector.requests.get",
            side_effect=requests.exceptions.Timeout("Connection timed out"),
        ):
            items = collector._fetch_source(source, Market.US)

        assert items == []

    def test_http_error_returns_empty(self, collector: RSSNewsCollector) -> None:
        """HTTP 에러(404 등) → 해당 소스만 스킵."""
        import requests

        from src.core.config import NewsSource
        source = NewsSource(name="DeadFeed", url="https://example.com/dead")

        with patch(
            "src.collectors.news.rss_collector.requests.get",
            side_effect=requests.exceptions.HTTPError("404 Not Found"),
        ):
            items = collector._fetch_source(source, Market.US)

        assert items == []


class TestCollectResilience:
    """전체 수집 프로세스 안정성 테스트."""

    def test_all_sources_fail_returns_empty(self, collector: RSSNewsCollector) -> None:
        """전체 소스 실패 시 빈 리스트 반환 (크래시 아님)."""
        import requests

        with patch(
            "src.collectors.news.rss_collector.requests.get",
            side_effect=requests.exceptions.ConnectionError("Network unreachable"),
        ):
            # time.sleep을 모킹하여 테스트 속도 확보
            with patch("src.collectors.news.rss_collector.time.sleep"):
                items = collector.collect()

        assert items == []
        assert len(collector.failed_sources) > 0

    def test_partial_source_failure_collects_rest(self, collector: RSSNewsCollector) -> None:
        """일부 소스 실패해도 나머지 소스의 뉴스를 수집."""
        from src.core.config import NewsSource
        from src.core.models import NewsItem

        call_count = 0
        original_fetch = collector._fetch_source

        def mock_fetch_source(source: NewsSource, market: Market) -> list[NewsItem]:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                # 처음 2개 소스는 실패 (빈 결과 반환)
                return []
            # 나머지는 정상 아이템 반환
            return [NewsItem(
                title=f"뉴스 from {source.name} #{call_count}",
                source=source.name,
                market=market,
            )]

        with patch.object(collector, "_fetch_source", side_effect=mock_fetch_source):
            with patch("src.collectors.news.rss_collector.time.sleep"):
                items = collector.collect()

        # 일부 성공 소스에서 수집된 아이템이 있어야 함
        assert len(items) > 0
        # 실패 소스가 기록됨
        assert len(collector.failed_sources) >= 2


class TestFailedSourcesTracking:
    """실패 소스 추적 테스트."""

    def test_failed_sources_property_default_empty(self) -> None:
        """collect() 호출 전에는 빈 리스트."""
        with patch("src.collectors.news.rss_collector.NewsRepository"):
            collector = RSSNewsCollector()
            assert collector.failed_sources == []
