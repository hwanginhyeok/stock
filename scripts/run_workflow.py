"""CLI runner and scheduler for workflow orchestration.

Usage:
    python scripts/run_workflow.py morning
    python scripts/run_workflow.py closing
    python scripts/run_workflow.py weekly
    python scripts/run_workflow.py breaking --topic "NVDA 실적" --tickers NVDA
    python scripts/run_workflow.py research --type stock --subject NVDA
    python scripts/run_workflow.py ohlcv-update                    # 전체 OHLCV 갱신
    python scripts/run_workflow.py ohlcv-update --index sp500      # S&P 500만
    python scripts/run_workflow.py schedule
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

from src.core.config import get_config
from src.core.database import init_db
from src.core.logger import get_logger, setup_logging
from src.core.models import ResearchType
from src.workflows import (
    BreakingNewsWorkflow,
    BreakingNewsTrigger,
    ClosingReviewWorkflow,
    MorningBriefingWorkflow,
    ResearchRequest,
    ResearchWorkflow,
    WeeklyReviewWorkflow,
    WorkflowResult,
)

logger = get_logger(__name__)


def _print_result(result: WorkflowResult) -> None:
    """Print workflow result summary to stdout.

    Args:
        result: WorkflowResult to display.
    """
    status = "SUCCESS" if result.success else "FAILED"
    print(f"\n{'=' * 60}")
    print(f"  Workflow: {result.workflow_name}")
    print(f"  Status:   {status}")
    print(f"  Elapsed:  {result.elapsed_sec}s")
    print(f"  Articles: {result.articles_generated}")
    print(f"  Images:   {result.images_generated}")
    print(f"  News:     {result.news_collected}")
    print(f"  Snapshots:{result.snapshots_collected}")
    print(f"  Analyses: {result.analyses_produced}")
    if result.errors:
        print(f"  Errors:   {len(result.errors)}")
        for err in result.errors:
            print(f"    - [{err.get('step', '?')}] {err.get('error', '?')}")
    if result.data:
        for key, value in result.data.items():
            if isinstance(value, list) and len(value) > 3:
                print(f"  {key}: [{len(value)} items]")
            else:
                print(f"  {key}: {value}")
    print(f"{'=' * 60}\n")


def run_morning() -> WorkflowResult:
    """Run morning briefing workflow.

    Returns:
        WorkflowResult.
    """
    workflow = MorningBriefingWorkflow()
    return workflow.run()


def run_closing() -> WorkflowResult:
    """Run closing review workflow.

    Returns:
        WorkflowResult.
    """
    workflow = ClosingReviewWorkflow()
    return workflow.run()


def run_weekly() -> WorkflowResult:
    """Run weekly review workflow.

    Returns:
        WorkflowResult.
    """
    workflow = WeeklyReviewWorkflow()
    return workflow.run()


def run_breaking(topic: str, tickers: list[str], urgency: str = "normal") -> WorkflowResult:
    """Run breaking news workflow.

    Args:
        topic: Breaking event description.
        tickers: Related ticker symbols.
        urgency: Urgency level ("normal" or "high").

    Returns:
        WorkflowResult.
    """
    trigger = BreakingNewsTrigger(
        topic=topic,
        tickers=tickers,
        urgency=urgency,
    )
    workflow = BreakingNewsWorkflow(trigger)
    return workflow.run()


def run_research(
    research_type: str,
    subject: str,
    tickers: list[str] | None = None,
    depth: str = "standard",
) -> WorkflowResult:
    """Run research workflow.

    Args:
        research_type: Research type string (stock, sector, theme, cross_market).
        subject: Research subject.
        tickers: Related ticker symbols.
        depth: Analysis depth ("standard" or "deep").

    Returns:
        WorkflowResult.
    """
    rt = ResearchType(research_type)
    request = ResearchRequest(
        research_type=rt,
        subject=subject,
        tickers=tickers or [],
        depth=depth,
    )
    workflow = ResearchWorkflow(request)
    return workflow.run()


def run_ohlcv_update(
    index: str = "all",
    years: int = 1,
    delay: float = 1.0,
) -> None:
    """Run OHLCV daily update for S&P 500 + NASDAQ 100.

    Args:
        index: Target index ("sp500", "ndx100", or "all").
        years: Number of years to fetch (1 for daily update).
        delay: Delay between API requests in seconds.
    """
    from src.backtesting.data.price_loader import PriceLoader
    from src.collectors.market.constituents import (
        fetch_ndx100_tickers,
        fetch_sp500_tickers,
        get_combined_universe,
    )
    from src.core.models import Market

    if index == "sp500":
        tickers = fetch_sp500_tickers()
    elif index == "ndx100":
        tickers = fetch_ndx100_tickers()
    else:
        tickers = get_combined_universe()

    if not tickers:
        logger.error("ohlcv_update_no_tickers")
        return

    loader = PriceLoader()
    success = 0
    failed = 0
    total_records = 0
    failed_tickers: list[str] = []

    logger.info("ohlcv_update_start", index=index, tickers=len(tickers), years=years)

    for i, ticker in enumerate(tickers, 1):
        try:
            count = loader.fetch_and_store(
                ticker, market=Market.US, years=years,
            )
            total_records += count
            success += 1
            if count > 0:
                logger.debug("ohlcv_updated", ticker=ticker, count=count)
        except Exception as e:
            failed += 1
            failed_tickers.append(ticker)
            logger.error("ohlcv_update_failed", ticker=ticker, error=str(e))

        if i < len(tickers):
            time.sleep(delay)

    logger.info(
        "ohlcv_update_complete",
        success=success,
        failed=failed,
        total_records=total_records,
    )

    print(f"\n{'=' * 60}")
    print(f"  OHLCV Update ({index})")
    print(f"  종목: {len(tickers)} | 성공: {success} | 실패: {failed}")
    print(f"  신규 레코드: {total_records}")
    if failed_tickers:
        print(f"  실패 종목: {', '.join(failed_tickers)}")
    print(f"{'=' * 60}\n")


def _run_morning_email() -> None:
    """Collect liquidity data and send morning email report.

    Called by the APScheduler job at morning briefing time (Mon-Sat).
    Silently skips if credentials are not configured.
    """
    try:
        import os
        import shutil
        import certifi as _certifi
        from pathlib import Path as _Path

        _cert_src = _Path(_certifi.where())
        try:
            str(_cert_src).encode("ascii")
        except (UnicodeEncodeError, UnicodeDecodeError):
            _cert_dst = _Path(os.environ.get("TEMP", "/tmp")) / "yf_certs" / "cacert.pem"
            if not _cert_dst.exists():
                _cert_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(_cert_src, _cert_dst)
            os.environ.setdefault("CURL_CA_BUNDLE", str(_cert_dst))

        from src.collectors.macro.fred_collector import FREDCollector
        from src.collectors.macro.fx_collector import FXCollector
        from src.publishers.email_publisher import EmailPublisher
        from src.core.config import PROJECT_ROOT

        output_dir = PROJECT_ROOT / "data" / "processed" / "dashboards"
        signal_files = sorted(
            output_dir.glob("Signal_Report_*.xlsx"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        excel_path = signal_files[0] if signal_files else None

        fred_data = FREDCollector().collect()
        fx_data   = FXCollector().collect()

        publisher = EmailPublisher()
        publisher.send_morning_report(
            fred_data=fred_data,
            fx_data=fx_data,
            excel_path=excel_path,
        )
        logger.info("morning_email_job_done")
    except Exception as e:
        logger.error("morning_email_job_failed", error=str(e))


def start_scheduler() -> None:
    """Start the APScheduler daemon with configured schedule times.

    Runs until interrupted (Ctrl+C).
    """
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger

    config = get_config()
    tz = config.schedule.timezone

    scheduler = BlockingScheduler(timezone=tz)

    # Morning briefing
    morning_time = config.schedule.morning_briefing
    h, m = morning_time.split(":")
    scheduler.add_job(
        run_morning,
        CronTrigger(hour=int(h), minute=int(m), timezone=tz),
        id="morning_briefing",
        name="Morning Briefing",
        misfire_grace_time=600,
    )
    logger.info("job_scheduled", job="morning_briefing", time=morning_time)

    # Closing review
    closing_time = config.schedule.closing_review
    h, m = closing_time.split(":")
    scheduler.add_job(
        run_closing,
        CronTrigger(hour=int(h), minute=int(m), timezone=tz),
        id="closing_review",
        name="Closing Review",
        misfire_grace_time=600,
    )
    logger.info("job_scheduled", job="closing_review", time=closing_time)

    # Weekly review (e.g., "SAT 10:00")
    weekly_spec = config.schedule.weekly_review
    parts = weekly_spec.split()
    day_abbr = parts[0].lower()[:3] if parts else "sat"
    wtime = parts[1] if len(parts) > 1 else "10:00"
    h, m = wtime.split(":")
    scheduler.add_job(
        run_weekly,
        CronTrigger(day_of_week=day_abbr, hour=int(h), minute=int(m), timezone=tz),
        id="weekly_review",
        name="Weekly Review",
        misfire_grace_time=1800,
    )
    logger.info("job_scheduled", job="weekly_review", spec=weekly_spec)

    # OHLCV daily update — US Eastern timezone, after market close
    ohlcv_cfg = config.schedule.ohlcv_update
    ohlcv_time = ohlcv_cfg["time"]
    ohlcv_tz = ohlcv_cfg.get("timezone", "America/New_York")
    h, m = ohlcv_time.split(":")
    scheduler.add_job(
        run_ohlcv_update,
        CronTrigger(
            day_of_week="mon-fri", hour=int(h), minute=int(m),
            timezone=ohlcv_tz,
        ),
        id="ohlcv_update",
        name="OHLCV Daily Update",
        misfire_grace_time=1800,
    )
    logger.info(
        "job_scheduled", job="ohlcv_update",
        time=ohlcv_time, timezone=ohlcv_tz,
    )

    # Morning email: liquidity + market report — Mon-Sat 08:00 KST
    email_h, email_m = morning_time.split(":")
    scheduler.add_job(
        _run_morning_email,
        CronTrigger(day_of_week="mon-sat", hour=int(email_h), minute=int(email_m), timezone=tz),
        id="morning_email",
        name="Morning Liquidity Email",
        misfire_grace_time=1800,
    )
    logger.info("job_scheduled", job="morning_email", time=morning_time, days="mon-sat")

    print(f"\nScheduler started (timezone: {tz})")
    print(f"  OHLCV update:     {ohlcv_time} Mon-Fri ({ohlcv_tz})")
    print(f"  Morning briefing: {morning_time}")
    print(f"  Morning email:    {morning_time} Mon-Sat (liquidity + market)")
    print(f"  Closing review:   {closing_time}")
    print(f"  Weekly review:    {weekly_spec}")
    print("\nPress Ctrl+C to stop.\n")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("scheduler_stopped")
        print("\nScheduler stopped.")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        description="주식부자프로젝트 — 워크플로우 실행기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/run_workflow.py morning\n"
            "  python scripts/run_workflow.py closing\n"
            "  python scripts/run_workflow.py weekly\n"
            '  python scripts/run_workflow.py breaking --topic "NVDA 실적" --tickers NVDA\n'
            "  python scripts/run_workflow.py research --type stock --subject NVDA\n"
            "  python scripts/run_workflow.py schedule\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", help="Workflow to run")

    # morning
    subparsers.add_parser("morning", help="모닝브리핑 즉시 실행")

    # closing
    subparsers.add_parser("closing", help="장마감 리뷰 즉시 실행")

    # weekly
    subparsers.add_parser("weekly", help="주간 리뷰 즉시 실행")

    # breaking
    breaking_parser = subparsers.add_parser("breaking", help="속보 즉시 실행")
    breaking_parser.add_argument(
        "--topic", required=True, help="속보 주제 (e.g., 'NVDA 실적 발표')",
    )
    breaking_parser.add_argument(
        "--tickers", nargs="*", default=[], help="관련 티커 (e.g., NVDA AAPL)",
    )
    breaking_parser.add_argument(
        "--urgency", default="normal", choices=["normal", "high"],
        help="긴급도 (default: normal)",
    )

    # research
    research_parser = subparsers.add_parser("research", help="리서치 즉시 실행")
    research_parser.add_argument(
        "--type", required=True, dest="research_type",
        choices=["stock", "sector", "theme", "cross_market"],
        help="리서치 유형",
    )
    research_parser.add_argument(
        "--subject", required=True, help="리서치 대상 (e.g., 'NVDA')",
    )
    research_parser.add_argument(
        "--tickers", nargs="*", default=[], help="관련 티커",
    )
    research_parser.add_argument(
        "--depth", default="standard", choices=["standard", "deep"],
        help="분석 깊이 (default: standard)",
    )

    # ohlcv-update
    ohlcv_parser = subparsers.add_parser(
        "ohlcv-update", help="S&P500+NASDAQ100 OHLCV 데이터 갱신",
    )
    ohlcv_parser.add_argument(
        "--index", default="all", choices=["sp500", "ndx100", "all"],
        help="대상 인덱스 (default: all)",
    )
    ohlcv_parser.add_argument(
        "--years", type=int, default=1,
        help="수집 연도 수 (default: 1, 일일 갱신용)",
    )
    ohlcv_parser.add_argument(
        "--delay", type=float, default=1.0,
        help="요청 간 대기 시간(초) (default: 1.0)",
    )

    # schedule
    subparsers.add_parser("schedule", help="스케줄러 데몬 시작")

    return parser


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize infrastructure
    config = get_config()
    setup_logging(
        level=config.logging.level,
        format=config.logging.format,
        log_file=config.logging.file,
    )
    init_db()

    # Dispatch
    if args.command == "schedule":
        start_scheduler()
        return

    result: WorkflowResult | None = None

    if args.command == "morning":
        result = run_morning()
    elif args.command == "closing":
        result = run_closing()
    elif args.command == "weekly":
        result = run_weekly()
    elif args.command == "breaking":
        result = run_breaking(
            topic=args.topic,
            tickers=args.tickers,
            urgency=args.urgency,
        )
    elif args.command == "research":
        result = run_research(
            research_type=args.research_type,
            subject=args.subject,
            tickers=args.tickers,
            depth=args.depth,
        )
    elif args.command == "ohlcv-update":
        run_ohlcv_update(
            index=args.index,
            years=args.years,
            delay=args.delay,
        )
        return

    if result:
        _print_result(result)
        sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
