"""Tests for Naver Finance community collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.collectors.sentiment.naver_community_collector import NaverCommunityCollector

_SAMPLE_HTML = """
<table class="type2">
<tr>
    <td>2026.02.24</td>
    <td><a class="tit">삼성전자 반등 기대</a></td>
    <td>user1</td>
    <td>1,234</td>
    <td>50</td>
    <td>10</td>
</tr>
<tr>
    <td>2026.02.24</td>
    <td><a class="tit">오늘 하락 예상</a></td>
    <td>user2</td>
    <td>567</td>
    <td>5</td>
    <td>30</td>
</tr>
<tr>
    <td>2026.02.23</td>
    <td><a class="tit">장기 보유 중</a></td>
    <td>user3</td>
    <td>890</td>
    <td>20</td>
    <td>20</td>
</tr>
</table>
"""


class TestNaverCommunityCollector:
    """Test Naver community collector with mocked HTTP."""

    def test_parse_posts(self) -> None:
        collector = NaverCommunityCollector()
        posts = collector._parse_posts(_SAMPLE_HTML)

        assert len(posts) == 3
        assert posts[0]["title"] == "삼성전자 반등 기대"
        assert posts[0]["views"] == 1234
        assert posts[0]["agree"] == 50
        assert posts[0]["disagree"] == 10
        assert posts[1]["agree"] == 5
        assert posts[1]["disagree"] == 30

    @patch("src.collectors.sentiment.naver_community_collector.requests.get")
    def test_collect_stock(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.text = _SAMPLE_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        collector = NaverCommunityCollector(request_delay_sec=0)
        result = collector.collect_stock("005930", "삼성전자", pages=1)

        assert result["stock_code"] == "005930"
        assert result["stock_name"] == "삼성전자"
        assert result["posts_count"] == 3
        # agree: 50+5+20=75, disagree: 10+30+20=60, ratio=75/135≈0.556
        assert result["bullish_ratio"] == 0.556
        assert result["sentiment"] == "Bullish"

    @patch("src.collectors.sentiment.naver_community_collector.requests.get")
    def test_collect_stock_empty_page(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.text = "<html><body><p>No data</p></body></html>"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        collector = NaverCommunityCollector(request_delay_sec=0)
        result = collector.collect_stock("000000", "테스트", pages=1)

        assert result["posts_count"] == 0
        assert result["bullish_ratio"] == 0.5
        assert result["sentiment"] == "Neutral"

    @patch("src.collectors.sentiment.naver_community_collector.requests.get")
    def test_collect_stock_network_error(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = Exception("Connection refused")

        collector = NaverCommunityCollector(request_delay_sec=0)
        result = collector.collect_stock("005930", "삼성전자", pages=2)

        assert result["posts_count"] == 0
