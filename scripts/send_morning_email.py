"""모닝 유동성 + 시장 리포트 이메일 발송 스크립트.

FRED 유동성 데이터 + FX/도착지 데이터를 수집하여
HTML 이메일(+ Excel 첨부)로 발송한다.

Usage::

    python scripts/send_morning_email.py                        # 오늘 최신 Signal Report 첨부
    python scripts/send_morning_email.py --no-excel             # 이메일 본문만
    python scripts/send_morning_email.py --dry-run              # 발송 없이 HTML 미리보기만
    python scripts/send_morning_email.py --excel path/to/file   # 특정 파일 첨부
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import certifi as _certifi

# Fix non-ASCII path issue for yfinance's curl_cffi
_cert_src = Path(_certifi.where())
try:
    str(_cert_src).encode("ascii")
except (UnicodeEncodeError, UnicodeDecodeError):
    _cert_dst = Path(os.environ.get("TEMP", "/tmp")) / "yf_certs" / "cacert.pem"
    if not _cert_dst.exists() or _cert_dst.stat().st_size != _cert_src.stat().st_size:
        _cert_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_cert_src, _cert_dst)
    os.environ.setdefault("CURL_CA_BUNDLE", str(_cert_dst))

from src.collectors.crypto.crypto_collector import CryptoCollector
from src.collectors.macro.fred_collector import FREDCollector
from src.collectors.macro.fx_collector import FXCollector
from src.core.config import PROJECT_ROOT, get_config
from src.core.logger import get_logger
from src.generators.crypto_chart import build_crypto_charts
from src.generators.liquidity_chart import build_all_charts
from src.publishers.email_publisher import EmailPublisher

logger = get_logger("send_morning_email")

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "dashboards"


def _latest_signal_report() -> Path | None:
    """Find the most recently modified Signal_Report_*.xlsx file."""
    files = sorted(
        OUTPUT_DIR.glob("Signal_Report_*.xlsx"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def _print_summary(fred_data: dict, fx_data: dict) -> None:
    """Print a concise terminal summary of collected data."""
    sep = "─" * 56
    print(f"\n{sep}")
    print("  유동성 공급 측 (FRED)")
    print(sep)
    print(f"  Fed 자산:      ${fred_data.get('walcl_b', 0):>8,.0f}B"
          f"  (WoW {fred_data.get('walcl_wow', 0):>+.0f}B)")
    print(f"  TGA:           ${fred_data.get('tga_b', 0):>8,.0f}B"
          f"  (WoW {fred_data.get('tga_wow', 0):>+.0f}B)")
    print(f"  RRP:           ${fred_data.get('rrp_b', 0):>8,.1f}B"
          f"  (WoW {fred_data.get('rrp_wow', 0):>+.1f}B)")
    print(f"  MMF 잔고:      ${fred_data.get('mmf_weekly_b', 0):>8,.0f}B"
          f"  (순유출입 {fred_data.get('mmf_flow_b', 0):>+.1f}B)")
    print(f"  MMF 전체(분기):${fred_data.get('mmf_total_b', 0):>8,.0f}B")
    nl = fred_data.get("net_liquidity_b")
    nl_wow = fred_data.get("net_liquidity_wow")
    if nl is not None:
        print(f"  ★ Net Liquidity: ${nl:>,.0f}B  (WoW {nl_wow:>+.0f}B)" if nl_wow else
              f"  ★ Net Liquidity: ${nl:>,.0f}B")
    print(f"\n  2s10s: {fred_data.get('yield_2s10s_b', 0):>+.2f}%"
          f"  |  HY Spread: {fred_data.get('hy_spread_b', 0):>.2f}%"
          f"  |  10Y: {fred_data.get('dgs10_b', 0):>.2f}%")

    print(f"\n{sep}")
    print("  흐름 신호 (통화)")
    print(sep)
    for name, d in fx_data.get("currencies", {}).items():
        if "error" not in d:
            print(f"  {name:<10} {d['last']:>10.4g}"
                  f"  1d {d.get('pct_1d', 0):>+.2f}%"
                  f"  1w {d.get('pct_1w', 0):>+.2f}%")

    print(f"\n{sep}")
    print("  도착지 신호")
    print(sep)
    for name, d in fx_data.get("destinations", {}).items():
        if "error" not in d:
            print(f"  {name:<12} {d['last']:>10.4g}"
                  f"  1d {d.get('pct_1d', 0):>+.2f}%"
                  f"  1w {d.get('pct_1w', 0):>+.2f}%")
    print(f"{sep}\n")

    sectors = fx_data.get("sectors", {})
    if sectors:
        print(f"{sep}")
        print("  섹터 순환 (S&P 500 GICS)")
        print(sep)
        for name, d in sectors.items():
            if "error" not in d:
                pct_1w = d.get("pct_1w") or 0
                pct_1m = d.get("pct_1m") or 0
                pct_3m = d.get("pct_3m") or 0
                pct_1y = d.get("pct_1y") or 0
                print(f"  {name:<20}"
                      f"  1w {pct_1w:>+.1f}%"
                      f"  1m {pct_1m:>+.1f}%"
                      f"  3m {pct_3m:>+.1f}%"
                      f"  1y {pct_1y:>+.1f}%")
        print(f"{sep}\n")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="모닝 유동성 리포트 이메일 발송")
    parser.add_argument("--no-excel",   action="store_true", help="Excel 첨부 없이 발송")
    parser.add_argument("--no-charts",  action="store_true", help="차트 생성 생략 (빠르게)")
    parser.add_argument("--no-crypto",  action="store_true", help="크립토 수집 생략")
    parser.add_argument("--dry-run",    action="store_true", help="발송 없이 데이터 수집 + HTML 출력만")
    parser.add_argument("--excel",      default=None,        help="특정 Excel 파일 경로")
    args = parser.parse_args()

    print("=" * 56)
    print("  Morning Liquidity Report — Email Sender")
    print("=" * 56)

    # 수집 실패 섹션 추적
    failed_sections: list[str] = []

    # ── Step 1: FRED 수집 ──────────────────────────────────────
    print("\n[1/3] FRED 유동성 데이터 수집 중...")
    fred_data: dict = {}
    try:
        fred_data = FREDCollector().collect()
        print("  OK")
    except Exception as e:
        logger.error("fred_collection_failed", error=str(e))
        print(f"  ✗ FRED 수집 실패: {e}")
        failed_sections.append("FRED")

    # ── Step 2: FX + 도착지 수집 ───────────────────────────────
    print("[2/3] FX / 도착지 데이터 수집 중...")
    fx_collector = FXCollector()
    fx_data: dict = {}
    try:
        fx_data = fx_collector.collect()
        print("  OK")
    except Exception as e:
        logger.error("fx_collection_failed", error=str(e))
        print(f"  ✗ FX 수집 실패: {e}")
        failed_sections.append("FX")

    if fred_data and fx_data:
        _print_summary(fred_data, fx_data)

    # ── Step 2.5: 크립토 수집 ──────────────────────────────────
    crypto_data: dict = {}
    crypto_collector: CryptoCollector | None = None
    if not args.no_crypto:
        print("[2.5] 크립토 데이터 수집 중 (BTC / ETH + DeFiLlama TVL)...")
        try:
            crypto_collector = CryptoCollector()
            crypto_data = crypto_collector.collect()
            btc_price = crypto_data.get("btc", {}).get("price", "?")
            eth_price = crypto_data.get("eth", {}).get("price", "?")
            eth_tvl   = crypto_data.get("eth_tvl_b", "?")
            print(f"  OK  BTC ${btc_price:,.0f}  ETH ${eth_price:,.0f}  ETH-DeFi TVL ${eth_tvl}B")
        except Exception as e:
            logger.error("crypto_collection_failed", error=str(e))
            print(f"  ✗ 크립토 수집 실패: {e}")
            failed_sections.append("Crypto")
    else:
        print("[2.5] 크립토 생략 (--no-crypto)")

    # ── Step 2.7: 차트 생성 ────────────────────────────────────
    charts: dict = {}
    if not args.no_charts:
        print("[2.7] 차트 생성 중 (FRED 2년 + FX 1년 + 크립토 1년)...")
        try:
            import matplotlib
            matplotlib.use("Agg")  # headless backend (no display needed)
            fred_series   = FREDCollector().collect_series(lookback_years=2)
            fx_series     = fx_collector.collect_series(period="1y")
            charts        = build_all_charts(fred_series, fx_series)
            if not args.no_crypto and crypto_collector is not None:
                crypto_series = crypto_collector.collect_series(period="1y")
                charts.update(build_crypto_charts(crypto_series))
            print(f"  OK ({len(charts)}개 차트)")
        except Exception as e:
            logger.error("chart_generation_failed", error=str(e))
            print(f"  ✗ 차트 생성 실패: {e}")
            failed_sections.append("Charts")
    else:
        print("[2.7] 차트 생략 (--no-charts)")

    # ── 전체 실패 시 조기 종료 ────────────────────────────────
    if not fred_data and not fx_data:
        print("\n  ✗ 핵심 데이터(FRED + FX) 모두 수집 실패 — 이메일 발송 스킵")
        logger.error("morning_email_skipped_all_failed", failed=failed_sections)
        sys.exit(1)

    # ── Dry-run: HTML 파일로 저장 후 종료 ─────────────────────
    if args.dry_run:
        publisher = EmailPublisher()
        from datetime import datetime
        html = publisher._render_html(
            fred_data, fx_data, datetime.now(),
            charts=charts, crypto_data=crypto_data or None,
        )
        preview_path = OUTPUT_DIR / "email_preview.html"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        preview_path.write_text(html, encoding="utf-8")
        print(f"[dry-run] HTML 미리보기 저장: {preview_path}")
        print("  Windows에서 열려면: start " + str(preview_path).replace("/home/gint_pcd", r"\\wsl$\Ubuntu\home\gint_pcd"))
        return

    # ── Step 3: Excel 파일 결정 ────────────────────────────────
    excel_path: Path | None = None
    if not args.no_excel:
        if args.excel:
            excel_path = Path(args.excel)
        else:
            excel_path = _latest_signal_report()
        if excel_path:
            print(f"[3/3] Excel 첨부: {excel_path.name}")
        else:
            print("[3/3] Signal Report 없음 — 이메일 본문만 발송")

    # ── Step 4: 이메일 발송 ────────────────────────────────────
    print("\n이메일 발송 중...")
    config = get_config()
    recipients = [r for r in config.email.recipients if r.address]
    if not recipients:
        print("  ERROR: 수신자 없음. settings.yaml 또는 .env의 GMAIL_ADDRESS 확인")
        sys.exit(1)

    print(f"  수신자: {', '.join(r.address for r in recipients)}")
    if failed_sections:
        print(f"  ⚠️  누락 섹션: {', '.join(failed_sections)}")
    publisher = EmailPublisher()
    ok = publisher.send_morning_report(
        fred_data=fred_data,
        fx_data=fx_data,
        excel_path=excel_path,
        charts=charts if charts else None,
        crypto_data=crypto_data if crypto_data else None,
        failed_sections=failed_sections,
    )

    if ok:
        print(f"  ✓ 발송 완료 ({len(recipients)}명)")
    else:
        print("  ✗ 일부 발송 실패 — 로그 확인")
        sys.exit(1)


if __name__ == "__main__":
    main()
