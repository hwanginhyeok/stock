"""모닝 이메일 Graceful Degradation 테스트.

수집기 부분 실패 시에도 이메일이 발송되고,
전체 실패 시에만 발송이 스킵되는지 검증.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.publishers.email_publisher import EmailPublisher


@pytest.fixture
def publisher() -> EmailPublisher:
    """EmailPublisher 인스턴스 (SMTP는 모킹으로 대체)."""
    with patch.object(EmailPublisher, "__init__", lambda self: None):
        pub = EmailPublisher.__new__(EmailPublisher)
        pub._config = MagicMock()
        pub._email_cfg = MagicMock()
        pub._email_cfg.sender_name = "테스트"
        pub._email_cfg.attach_excel = False
        pub._email_cfg.smtp_host = "smtp.test.com"
        pub._email_cfg.smtp_port = 587
        pub._sender = "test@test.com"
        pub._password = "testpass"

        # Jinja 템플릿 대신 단순 문자열 반환
        pub._jinja = MagicMock()
        template_mock = MagicMock()
        template_mock.render = MagicMock(return_value="<html>test</html>")
        pub._jinja.get_template.return_value = template_mock

        # Recipients 설정
        recipient = MagicMock()
        recipient.name = "테스트"
        recipient.address = "recipient@test.com"
        pub._email_cfg.recipients = [recipient]

        return pub


@pytest.fixture
def sample_fred() -> dict:
    return {"net_liquidity_b": 5800.0, "net_liquidity_wow": 50.0, "walcl_b": 7000}


@pytest.fixture
def sample_fx() -> dict:
    return {"currencies": {"DXY": {"last": 104.5}}, "destinations": {}, "sectors": {}}


class TestSubjectPrefix:
    """이메일 제목에 [일부 누락] 접두사 테스트."""

    def test_no_failure_no_prefix(
        self, publisher: EmailPublisher, sample_fred: dict, sample_fx: dict,
    ) -> None:
        """실패 없으면 제목에 접두사 없음."""
        with patch.object(publisher, "_smtp_send"):
            publisher.send_morning_report(
                fred_data=sample_fred, fx_data=sample_fx, failed_sections=[],
            )
            call_args = publisher._smtp_send.call_args
            msg = call_args[0][0]
            assert "[일부 누락]" not in msg["Subject"]

    def test_failure_adds_prefix(
        self, publisher: EmailPublisher, sample_fred: dict, sample_fx: dict,
    ) -> None:
        """실패 있으면 제목에 [일부 누락] 접두사."""
        with patch.object(publisher, "_smtp_send"):
            publisher.send_morning_report(
                fred_data=sample_fred, fx_data=sample_fx,
                failed_sections=["FRED"],
            )
            call_args = publisher._smtp_send.call_args
            msg = call_args[0][0]
            assert msg["Subject"].startswith("[일부 누락]")

    def test_none_failed_sections_no_prefix(
        self, publisher: EmailPublisher, sample_fred: dict, sample_fx: dict,
    ) -> None:
        """failed_sections=None이면 접두사 없음 (하위 호환)."""
        with patch.object(publisher, "_smtp_send"):
            publisher.send_morning_report(
                fred_data=sample_fred, fx_data=sample_fx,
                failed_sections=None,
            )
            call_args = publisher._smtp_send.call_args
            msg = call_args[0][0]
            assert "[일부 누락]" not in msg["Subject"]


class TestPartialFailure:
    """부분 실패 시 이메일 발송 테스트."""

    def test_fred_only_failure_still_sends(
        self, publisher: EmailPublisher, sample_fx: dict,
    ) -> None:
        """FRED만 실패해도 이메일 발송됨."""
        with patch.object(publisher, "_smtp_send"):
            result = publisher.send_morning_report(
                fred_data={}, fx_data=sample_fx,
                failed_sections=["FRED"],
            )
            assert result is True
            publisher._smtp_send.assert_called_once()

    def test_fx_only_failure_still_sends(
        self, publisher: EmailPublisher, sample_fred: dict,
    ) -> None:
        """FX만 실패해도 이메일 발송됨."""
        with patch.object(publisher, "_smtp_send"):
            result = publisher.send_morning_report(
                fred_data=sample_fred, fx_data={},
                failed_sections=["FX"],
            )
            assert result is True
            publisher._smtp_send.assert_called_once()


class TestTemplateRendering:
    """failed_sections가 템플릿에 전달되는지 테스트."""

    def test_failed_sections_passed_to_template(
        self, publisher: EmailPublisher, sample_fred: dict, sample_fx: dict,
    ) -> None:
        """failed_sections가 _render_html을 통해 템플릿에 전달됨."""
        with patch.object(publisher, "_smtp_send"):
            publisher.send_morning_report(
                fred_data=sample_fred, fx_data=sample_fx,
                failed_sections=["FRED", "Crypto"],
            )
            template = publisher._jinja.get_template.return_value
            render_kwargs = template.render.call_args[1]
            assert render_kwargs["failed_sections"] == ["FRED", "Crypto"]

    def test_empty_failed_sections_passed_as_empty_list(
        self, publisher: EmailPublisher, sample_fred: dict, sample_fx: dict,
    ) -> None:
        """실패 없으면 빈 리스트 전달."""
        with patch.object(publisher, "_smtp_send"):
            publisher.send_morning_report(
                fred_data=sample_fred, fx_data=sample_fx,
                failed_sections=[],
            )
            template = publisher._jinja.get_template.return_value
            render_kwargs = template.render.call_args[1]
            assert render_kwargs["failed_sections"] == []
