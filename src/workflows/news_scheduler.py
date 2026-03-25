"""APScheduler-based news collection daemon.

Runs the news pipeline on a schedule:
- Market hours (KR or US open): every 30 minutes
- Off-hours: every 120 minutes

Usage::

    scheduler = NewsCollectionScheduler()
    scheduler.start()  # blocks until SIGINT/SIGTERM
"""

from __future__ import annotations

import signal
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.collectors.news.news_pipeline import NewsPipeline, PipelineResult
from src.core.config import get_config
from src.core.logger import get_logger
from src.core.models import Market

logger = get_logger(__name__)

KST = ZoneInfo("Asia/Seoul")
EST = ZoneInfo("America/New_York")


def is_market_hours() -> bool:
    """Check if any tracked market (KR or US) is currently open.

    KR: Mon-Fri 09:00~15:30 KST
    US: Mon-Fri 09:30~16:00 EST (DST handled by zoneinfo)

    Returns:
        True if at least one market is open.
    """
    now_kst = datetime.now(KST)
    now_est = datetime.now(EST)

    # 주말 체크 (KST 기준)
    if now_kst.weekday() > 4:
        return False

    # KR 장중: 09:00 ~ 15:30 KST
    kr_open = False
    kr_hour = now_kst.hour
    kr_min = now_kst.minute
    if 9 <= kr_hour < 15:
        kr_open = True
    elif kr_hour == 15 and kr_min <= 30:
        kr_open = True

    # US 장중: 09:30 ~ 16:00 EST
    us_open = False
    us_hour = now_est.hour
    us_min = now_est.minute
    # US 주말 별도 체크 (EST 기준 — KST와 요일이 다를 수 있음)
    if now_est.weekday() <= 4:
        if us_hour == 9 and us_min >= 30:
            us_open = True
        elif 10 <= us_hour < 16:
            us_open = True

    return kr_open or us_open


def get_current_interval_minutes() -> int:
    """Return the collection interval based on market hours.

    Returns:
        30 during market hours, 120 otherwise.
    """
    config = get_config()
    schedule = config.schedule.news_collection
    if is_market_hours():
        return schedule.get("market_hours_interval_min", 30)
    return schedule.get("off_hours_interval_min", 120)


class NewsCollectionScheduler:
    """Daemon that periodically runs the news pipeline.

    Uses APScheduler BlockingScheduler with dynamic interval adjustment.
    The interval is re-evaluated before each run.

    Args:
        analyze_sentiment: Pass to pipeline — run Claude sentiment scoring.
    """

    JOB_ID = "news_collection"

    def __init__(self, analyze_sentiment: bool = False) -> None:
        self._pipeline = NewsPipeline()
        self._analyze_sentiment = analyze_sentiment
        self._scheduler = BlockingScheduler(timezone=KST)
        self._setup_signals()

    def _setup_signals(self) -> None:
        """Register signal handlers for graceful shutdown."""
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._handle_signal)

    def _handle_signal(self, signum: int, frame: object) -> None:
        """Gracefully shut down the scheduler."""
        sig_name = signal.Signals(signum).name
        logger.info("shutdown_signal_received", signal=sig_name)
        self._scheduler.shutdown(wait=False)
        sys.exit(0)

    def start(self) -> None:
        """Start the scheduler (blocks the calling thread).

        Runs an immediate collection, then schedules recurring jobs.
        """
        logger.info(
            "news_scheduler_starting",
            sentiment=self._analyze_sentiment,
            initial_interval_min=get_current_interval_minutes(),
            market_hours=is_market_hours(),
        )

        # 즉시 1회 실행
        self._run_collection()

        # 기본 인터벌 (장중 30분)로 시작 — 매 실행마다 동적 조절
        interval = get_current_interval_minutes()
        self._scheduler.add_job(
            self._run_collection_with_reschedule,
            trigger=IntervalTrigger(minutes=interval, timezone=KST),
            id=self.JOB_ID,
            name="뉴스 자동 수집",
            replace_existing=True,
        )

        next_run = self._scheduler.get_job(self.JOB_ID).next_run_time
        logger.info(
            "scheduler_started",
            interval_min=interval,
            next_run=str(next_run),
        )

        try:
            self._scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("scheduler_stopped")

    def run_once(self, market_str: str | None = None) -> PipelineResult:
        """Run the pipeline once without starting the scheduler.

        Args:
            market_str: Optional market filter ("kr" or "us").

        Returns:
            PipelineResult from the pipeline execution.
        """
        market = None
        if market_str:
            market = Market.KOREA if market_str.lower() == "kr" else Market.US

        return self._pipeline.run(
            market=market,
            analyze_sentiment=self._analyze_sentiment,
        )

    def _run_collection(self) -> None:
        """Execute the pipeline and log results."""
        now = datetime.now(KST)
        logger.info(
            "collection_cycle_start",
            time_kst=now.strftime("%Y-%m-%d %H:%M:%S"),
            market_hours=is_market_hours(),
        )

        result = self._pipeline.run(
            analyze_sentiment=self._analyze_sentiment,
        )

        logger.info(
            "collection_cycle_complete",
            summary=result.summary(),
        )

        if result.errors:
            for err in result.errors:
                logger.warning("pipeline_error", error=err)

    def _run_collection_with_reschedule(self) -> None:
        """Run collection and adjust the interval if market hours changed."""
        self._run_collection()

        # 현재 인터벌 확인 & 필요시 재스케줄
        new_interval = get_current_interval_minutes()
        job = self._scheduler.get_job(self.JOB_ID)
        if job:
            current_interval = int(job.trigger.interval.total_seconds() / 60)
            if current_interval != new_interval:
                self._scheduler.reschedule_job(
                    self.JOB_ID,
                    trigger=IntervalTrigger(minutes=new_interval, timezone=KST),
                )
                logger.info(
                    "interval_adjusted",
                    old_min=current_interval,
                    new_min=new_interval,
                    market_hours=is_market_hours(),
                )
