"""Gmail SMTP email publisher for daily market reports.

Sends HTML emails with optional Excel attachment to a configurable
list of recipients. Recipients are managed in settings.yaml so
adding new subscribers requires no code changes.

Usage::

    publisher = EmailPublisher()
    publisher.send_morning_report(
        fred_data=fred_data,
        fx_data=fx_data,
        excel_path=Path("data/processed/dashboards/Signal_Report_20260301.xlsx"),
    )
"""

from __future__ import annotations

import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from src.core.config import get_config
from src.core.logger import get_logger

logger = get_logger(__name__)


class EmailPublisher:
    """Sends HTML market report emails via Gmail SMTP.

    Credentials are loaded from .env (GMAIL_ADDRESS, GMAIL_APP_PASSWORD).
    Recipients are loaded from config/settings.yaml under email.recipients.

    To add a new subscriber, add an entry to settings.yaml:
        - name: "홍길동"
          address: "hong@example.com"
    """

    def __init__(self) -> None:
        self._config = get_config()
        self._email_cfg = self._config.email
        self._sender = self._config.gmail_address
        self._password = self._config.gmail_app_password

        from src.core.config import PROJECT_ROOT
        template_dir = PROJECT_ROOT / "templates" / "email"
        self._jinja = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
        )

    # ── Public API ────────────────────────────────────────────────────────

    def send_morning_report(
        self,
        fred_data: dict[str, Any],
        fx_data: dict[str, Any],
        excel_path: Path | None = None,
        charts: dict[str, str] | None = None,
        crypto_data: dict[str, Any] | None = None,
        ecosystem_data: dict[str, Any] | None = None,
        failed_sections: list[str] | None = None,
    ) -> bool:
        """Build and send the morning liquidity + market report.

        Args:
            fred_data: Output from FREDCollector.collect().
            fx_data: Output from FXCollector.collect().
            excel_path: Optional path to Excel file to attach.
            charts: Base64-encoded chart PNGs from build_all_charts() and build_crypto_charts().
            crypto_data: Output from CryptoCollector.collect().
            ecosystem_data: Output from CryptoCollector.collect_ecosystem().
            failed_sections: List of section names that failed to collect.

        Returns:
            True if all recipients received the email, False otherwise.
        """
        now = datetime.now()
        subject = (
            f"[주식부자] 모닝 리포트 — {now.strftime('%Y-%m-%d')} "
            f"| Net Liq ${fred_data.get('net_liquidity_b', '?'):.0f}B"
            if fred_data.get("net_liquidity_b") is not None
            else f"[주식부자] 모닝 리포트 — {now.strftime('%Y-%m-%d')}"
        )
        if failed_sections:
            subject = f"[일부 누락] {subject}"

        html_body = self._render_html(
            fred_data, fx_data, now, charts=charts, crypto_data=crypto_data,
            ecosystem_data=ecosystem_data,
            failed_sections=failed_sections or [],
        )
        recipients = self._active_recipients()

        if not recipients:
            logger.warning("email_no_recipients")
            return False

        if not self._sender or not self._password:
            logger.error(
                "email_credentials_missing",
                hint="Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env",
            )
            return False

        success_count = 0
        for recipient in recipients:
            try:
                msg = self._build_message(
                    to_name=recipient.name,
                    to_address=recipient.address,
                    subject=subject,
                    html_body=html_body,
                    excel_path=excel_path if self._email_cfg.attach_excel else None,
                )
                self._smtp_send(msg, recipient.address)
                logger.info("email_sent", recipient=recipient.address)
                success_count += 1
            except Exception as e:
                logger.error("email_send_failed", recipient=recipient.address, error=str(e))

        logger.info("email_batch_done", sent=success_count, total=len(recipients))
        return success_count == len(recipients)

    # ── Internals ─────────────────────────────────────────────────────────

    def _active_recipients(self) -> list:
        """Return recipients that have a non-empty address."""
        return [r for r in self._email_cfg.recipients if r.address]

    def _render_html(
        self,
        fred_data: dict[str, Any],
        fx_data: dict[str, Any],
        now: datetime,
        charts: dict[str, str] | None = None,
        crypto_data: dict[str, Any] | None = None,
        ecosystem_data: dict[str, Any] | None = None,
        failed_sections: list[str] | None = None,
    ) -> str:
        """Render Jinja2 HTML template with report data.

        Args:
            fred_data: FRED supply-side data.
            fx_data: FX and destination asset data.
            now: Report generation datetime.
            charts: Base64-encoded chart PNGs (liquidity, mmf, currencies,
                    destinations, sectors, crypto_price, eth_tvl).
            crypto_data: Output from CryptoCollector.collect().
            ecosystem_data: Output from CryptoCollector.collect_ecosystem().
            failed_sections: List of data sections that failed to collect.

        Returns:
            Rendered HTML string.
        """
        template = self._jinja.get_template("morning_report.html.j2")
        return template.render(
            report_date=now.strftime("%Y년 %m월 %d일"),
            report_time=now.strftime("%H:%M"),
            fred=fred_data,
            net_liquidity=fred_data.get("net_liquidity_b"),
            net_liquidity_wow=fred_data.get("net_liquidity_wow"),
            currencies=fx_data.get("currencies", {}),
            destinations=fx_data.get("destinations", {}),
            sectors=fx_data.get("sectors", {}),
            charts=charts or {},
            crypto=crypto_data or {},
            ecosystem=ecosystem_data or {},
            failed_sections=failed_sections or [],
        )

    def _build_message(
        self,
        to_name: str,
        to_address: str,
        subject: str,
        html_body: str,
        excel_path: Path | None,
    ) -> MIMEMultipart:
        """Construct a MIME multipart email message.

        Args:
            to_name: Recipient display name.
            to_address: Recipient email address.
            subject: Email subject line.
            html_body: Rendered HTML content.
            excel_path: Path to Excel file, or None to skip attachment.

        Returns:
            Fully constructed MIMEMultipart message.
        """
        msg = MIMEMultipart("mixed")
        msg["From"]    = f"{self._email_cfg.sender_name} <{self._sender}>"
        msg["To"]      = f"{to_name} <{to_address}>" if to_name else to_address
        msg["Subject"] = subject

        # HTML body
        body_part = MIMEMultipart("alternative")
        body_part.attach(MIMEText(html_body, "html", "utf-8"))
        msg.attach(body_part)

        # Excel attachment
        if excel_path and Path(excel_path).exists():
            with open(excel_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{Path(excel_path).name}"',
            )
            msg.attach(part)
            logger.debug("excel_attached", path=str(excel_path))

        return msg

    def _smtp_send(self, msg: MIMEMultipart, to_address: str) -> None:
        """Send a message via Gmail SMTP with TLS.

        Args:
            msg: Fully constructed MIME message.
            to_address: Destination email address.

        Raises:
            smtplib.SMTPException: On SMTP-level errors.
        """
        with smtplib.SMTP(self._email_cfg.smtp_host, self._email_cfg.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self._sender, self._password)
            server.sendmail(self._sender, to_address, msg.as_string())
