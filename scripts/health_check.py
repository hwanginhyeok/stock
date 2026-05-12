#!/usr/bin/env python3
"""주식부자프로젝트 헬스체크 스크립트.

PM의 health_orchestrator.py가 호출. JSON 출력.
사용법: python3 scripts/health_check.py --json
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

import requests

# =============================================================================
# 설정
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
LOGS_DIR = PROJECT_ROOT / "logs"
DB_PATH = PROJECT_ROOT / "data" / "db" / "stock_rich.db"
EARNINGS_DIR = PROJECT_ROOT / "docs" / "earnings"

# 로그 파일별 허용 시간 (초)
LOG_FRESHNESS_LIMITS = {
    "news_collect.log": 2 * 3600,        # 2시간
    "geoinvest_update.log": 2 * 3600,    # 2시간
    "stockinvest_update.log": 2 * 3600,  # 2시간
    "entity_review.log": 26 * 3600,      # 26시간
    "deep_analysis.log": 14 * 3600,      # 14시간
}

# 기능 정의
FEATURES = [
    {
        "id": "F001",
        "name": "뉴스 수집+분류",
        "log_file": "news_collect.log",
        "priority": "P0",
    },
    {
        "id": "F002",
        "name": "지정학 엔티티 추출",
        "log_file": "geoinvest_update.log",
        "priority": "P1",
    },
    {
        "id": "F003",
        "name": "주식 엔티티 추출",
        "log_file": "stockinvest_update.log",
        "priority": "P0",
    },
    {
        "id": "F004",
        "name": "엔티티 리뷰",
        "log_file": "entity_review.log",
        "priority": "P1",
    },
    {
        "id": "F005",
        "name": "심층분석",
        "log_file": "deep_analysis.log",
        "priority": "P1",
    },
    {
        "id": "F006",
        "name": "모닝 브리핑",
        "check_type": "briefing_morning",
        "priority": "P0",
    },
    {
        "id": "F007",
        "name": "이브닝 브리핑",
        "check_type": "briefing_evening",
        "priority": "P0",
    },
    {
        "id": "F008",
        "name": "실적 리포트 파이프라인",
        "check_type": "earnings_dir",
        "priority": "P2",
    },
    {
        "id": "F009",
        "name": "Essence 대시보드",
        "check_type": "http_server",
        "priority": "P1",
    },
]

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# =============================================================================
# 데이터 클래스
# =============================================================================

Severity = Literal["ok", "minor", "major", "critical"]
Status = Literal["ok", "warn", "fail"]


@dataclass
class CheckResult:
    """단일 검증 결과."""
    
    id: str
    name: str
    status: Status
    detail: str
    severity: Severity = "ok"
    priority: str = "P2"


@dataclass
class HealthSummary:
    """종합 요약."""
    
    total: int
    ok: int
    warn: int
    fail: int
    severity: Severity = "ok"


@dataclass
class HealthReport:
    """전체 헬스체크 리포트."""
    
    project: str = "stock"
    timestamp: str = ""
    results: list[CheckResult] = field(default_factory=list)
    summary: HealthSummary | None = None
    
    def to_dict(self) -> dict:
        """JSON 직렬화용 딕셔너리 반환."""
        return {
            "project": self.project,
            "timestamp": self.timestamp,
            "results": [
                {
                    "id": r.id,
                    "name": r.name,
                    "status": r.status,
                    "detail": r.detail,
                    "severity": r.severity,
                }
                for r in self.results
            ],
            "summary": {
                "total": self.summary.total,
                "ok": self.summary.ok,
                "warn": self.summary.warn,
                "fail": self.summary.fail,
                "severity": self.summary.severity,
            } if self.summary else None,
        }


# =============================================================================
# 검증 함수들
# =============================================================================

def log_freshness(log_file: str, max_age_seconds: int) -> CheckResult:
    """로그 파일 신선도 검증.
    
    Args:
        log_file: 로그 파일명 (logs/ 내)
        max_age_seconds: 허용 최대 경과 시간 (초)
    
    Returns:
        CheckResult: 로그 신선도 검증 결과
    """
    log_path = LOGS_DIR / log_file
    feature_id = next((f["id"] for f in FEATURES if f.get("log_file") == log_file), "UNKNOWN")
    feature_name = next((f["name"] for f in FEATURES if f.get("log_file") == log_file), log_file)
    priority = next((f["priority"] for f in FEATURES if f.get("log_file") == log_file), "P2")
    
    try:
        if not log_path.exists():
            return CheckResult(
                id=feature_id,
                name=feature_name,
                status="fail",
                detail=f"로그 파일 없음: {log_file}",
                severity="major",
                priority=priority,
            )
        
        mtime = log_path.stat().st_mtime
        age_seconds = datetime.now().timestamp() - mtime
        age_hours = age_seconds / 3600
        
        if age_seconds <= max_age_seconds:
            return CheckResult(
                id=feature_id,
                name=feature_name,
                status="ok",
                detail=f"로그 업데이트됨 ({age_hours:.1f}시간 전)",
                severity="ok",
                priority=priority,
            )
        else:
            return CheckResult(
                id=feature_id,
                name=feature_name,
                status="fail",
                detail=f"로그 오래됨 ({age_hours:.1f}시간 경과, 허용 {max_age_seconds/3600:.1f}시간)",
                severity="major",
                priority=priority,
            )
    
    except Exception as e:
        logger.error(f"log_freshness 오류 ({log_file}): {e}")
        return CheckResult(
            id=feature_id,
            name=feature_name,
            status="fail",
            detail=f"검증 오류: {e}",
            severity="major",
            priority=priority,
        )


def log_errors(log_file: str, recent_lines: int = 50) -> Severity:
    """로그 파일 에러 빈도 검증.
    
    Args:
        log_file: 로그 파일명
        recent_lines: 확인할 최근 줄 수
    
    Returns:
        Severity: 에러 심각도
    """
    log_path = LOGS_DIR / log_file
    
    try:
        if not log_path.exists():
            return "ok"  # 파일 없으면 에러 카운트 없음으로 처리
        
        # 최근 N줄 읽기
        lines = []
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                lines.append(line.rstrip("\n"))
        
        recent = lines[-recent_lines:] if len(lines) >= recent_lines else lines
        
        # 에러 패턴 매칭 (대소문자 무시)
        error_pattern = re.compile(r"(traceback|error|exception|fail)", re.IGNORECASE)
        error_count = sum(1 for line in recent if error_pattern.search(line))
        
        if error_count >= 5:
            return "critical"
        elif error_count >= 1:
            return "major"
        else:
            return "ok"
    
    except Exception as e:
        logger.warning(f"log_errors 검증 실패 ({log_file}): {e}")
        return "minor"


def briefing_exists(briefing_type: Literal["morning", "evening"]) -> CheckResult:
    """브리핑 파일 존재 검증.
    
    Args:
        briefing_type: 'morning' 또는 'evening'
    
    Returns:
        CheckResult: 브리핑 파일 검증 결과
    """
    today = datetime.now().strftime("%Y%m%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    
    if briefing_type == "morning":
        feature_id = "F006"
        feature_name = "모닝 브리핑"
        priority = "P0"
        log_name = f"briefing_{today}_morning.log"
        log_name_yesterday = f"briefing_{yesterday}_morning.log"
    else:  # evening
        feature_id = "F007"
        feature_name = "이브닝 브리핑"
        priority = "P0"
        log_name = f"briefing_{today}_evening.log"
        log_name_yesterday = f"briefing_{yesterday}_evening.log"
    
    log_path = LOGS_DIR / log_name
    log_path_yesterday = LOGS_DIR / log_name_yesterday
    
    try:
        if log_path.exists():
            # 오늘 파일 있음
            # 에러 체크
            severity = log_errors(log_name)
            status_val: Status = "ok" if severity == "ok" else "warn"
            return CheckResult(
                id=feature_id,
                name=feature_name,
                status=status_val,
                detail=f"오늘 브리핑 존재: {log_name}",
                severity=severity,
                priority=priority,
            )
        
        elif log_path_yesterday.exists():
            # 어제 파일만 있음 → warn
            return CheckResult(
                id=feature_id,
                name=feature_name,
                status="warn",
                detail=f"어제 브리핑만 존재: {log_name_yesterday}",
                severity="minor",
                priority=priority,
            )
        
        else:
            # 둘 다 없음 → fail
            return CheckResult(
                id=feature_id,
                name=feature_name,
                status="fail",
                detail=f"브리핑 파일 없음 (오늘/어제 모두 없음)",
                severity="major",
                priority=priority,
            )
    
    except Exception as e:
        logger.error(f"briefing_exists 오류 ({briefing_type}): {e}")
        return CheckResult(
            id=feature_id,
            name=feature_name,
            status="fail",
            detail=f"검증 오류: {e}",
            severity="major",
            priority=priority,
        )


def db_check() -> CheckResult:
    """DB 연결 검증.
    
    Returns:
        CheckResult: DB 상태 검증 결과
    """
    try:
        if not DB_PATH.exists():
            return CheckResult(
                id="DB01",
                name="DB 연결",
                status="fail",
                detail=f"DB 파일 없음: {DB_PATH}",
                severity="critical",
                priority="P0",
            )
        
        if DB_PATH.stat().st_size == 0:
            return CheckResult(
                id="DB01",
                name="DB 연결",
                status="fail",
                detail=f"DB 파일 비어있음: {DB_PATH}",
                severity="critical",
                priority="P0",
            )
        
        # sqlite3 연결 테스트
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 테이블 수 확인
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        conn.close()
        
        return CheckResult(
            id="DB01",
            name="DB 연결",
            status="ok",
            detail=f"DB 정상 (테이블 {table_count}개, 크기 {DB_PATH.stat().st_size:,} bytes)",
            severity="ok",
            priority="P0",
        )
    
    except sqlite3.Error as e:
        logger.error(f"db_check SQLite 오류: {e}")
        return CheckResult(
            id="DB01",
            name="DB 연결",
            status="fail",
            detail=f"SQLite 오류: {e}",
            severity="critical",
            priority="P0",
        )
    
    except Exception as e:
        logger.error(f"db_check 오류: {e}")
        return CheckResult(
            id="DB01",
            name="DB 연결",
            status="fail",
            detail=f"검증 오류: {e}",
            severity="major",
            priority="P0",
        )


def earnings_dir_check() -> CheckResult:
    """실적 리포트 디렉토리 검증.
    
    Returns:
        CheckResult: 실적 리포트 디렉토리 상태
    """
    try:
        if not EARNINGS_DIR.exists():
            return CheckResult(
                id="F008",
                name="실적 리포트 파이프라인",
                status="warn",
                detail=f"earnings 디렉토리 없음: {EARNINGS_DIR}",
                severity="minor",
                priority="P2",
            )
        
        # HTML 파일 수 확인
        html_files = list(EARNINGS_DIR.glob("*.html"))
        html_count = len(html_files)
        
        if html_count == 0:
            return CheckResult(
                id="F008",
                name="실적 리포트 파이프라인",
                status="warn",
                detail=f"HTML 파일 0개 (디렉토리는 존재)",
                severity="minor",
                priority="P2",
            )
        
        return CheckResult(
            id="F008",
            name="실적 리포트 파이프라인",
            status="ok",
            detail=f"HTML 파일 {html_count}개 존재",
            severity="ok",
            priority="P2",
        )
    
    except Exception as e:
        logger.error(f"earnings_dir_check 오류: {e}")
        return CheckResult(
            id="F008",
            name="실적 리포트 파이프라인",
            status="fail",
            detail=f"검증 오류: {e}",
            severity="minor",
            priority="P2",
        )


def http_check() -> CheckResult:
    """웹서버 상태 검증.
    
    Returns:
        CheckResult: 웹서버 응답 상태
    """
    url = "http://localhost:5001/api/tesla/essence"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return CheckResult(
                id="F009",
                name="Essence 대시보드",
                status="ok",
                detail=f"서버 정상 응답 (status={response.status_code})",
                severity="ok",
                priority="P1",
            )
        else:
            return CheckResult(
                id="F009",
                name="Essence 대시보드",
                status="fail",
                detail=f"서버 비정상 응답 (status={response.status_code})",
                severity="major",
                priority="P1",
            )
    
    except requests.exceptions.ConnectionError:
        # 서버 안 뜬 상태 → warn (not critical)
        return CheckResult(
            id="F009",
            name="Essence 대시보드",
            status="warn",
            detail="서버 연결 실패 (서버가 실행 중이 아닐 수 있음)",
            severity="minor",
            priority="P1",
        )
    
    except requests.exceptions.Timeout:
        return CheckResult(
            id="F009",
            name="Essence 대시보드",
            status="fail",
            detail="서버 응답 타임아웃",
            severity="major",
            priority="P1",
        )
    
    except Exception as e:
        logger.error(f"http_check 오류: {e}")
        return CheckResult(
            id="F009",
            name="Essence 대시보드",
            status="fail",
            detail=f"검증 오류: {e}",
            severity="minor",
            priority="P1",
        )


# =============================================================================
# 메인 검증 루프
# =============================================================================

def run_all_checks(verbose: bool = False) -> HealthReport:
    """모든 헬스체크 실행.
    
    Args:
        verbose: 상세 로그 출력 여부
    
    Returns:
        HealthReport: 전체 검증 결과
    """
    results: list[CheckResult] = []
    
    # 각 기능별 검증
    for feature in FEATURES:
        feature_id = feature["id"]
        check_type = feature.get("check_type")
        
        if verbose:
            logger.info(f"검증 중: {feature_id} - {feature['name']}")
        
        # 로그 파일 기반 검증
        if "log_file" in feature:
            log_file = feature["log_file"]
            max_age = LOG_FRESHNESS_LIMITS.get(log_file, 2 * 3600)
            
            # 신선도 체크
            result = log_freshness(log_file, max_age)
            
            # 에러 빈도 체크 → severity 업데이트
            error_severity = log_errors(log_file)
            if error_severity != "ok":
                # 에러가 있으면 severity 업데이트 (단, ok보다 나쁜 경우만)
                severity_order = {"ok": 0, "minor": 1, "major": 2, "critical": 3}
                if severity_order[error_severity] > severity_order[result.severity]:
                    result.severity = error_severity
                    # status도 업데이트
                    if error_severity in ("major", "critical"):
                        result.status = "warn" if result.status == "ok" else result.status
            
            results.append(result)
        
        # 브리핑 검증
        elif check_type == "briefing_morning":
            results.append(briefing_exists("morning"))
        
        elif check_type == "briefing_evening":
            results.append(briefing_exists("evening"))
        
        # 실적 리포트 검증
        elif check_type == "earnings_dir":
            results.append(earnings_dir_check())
        
        # 웹서버 검증
        elif check_type == "http_server":
            results.append(http_check())
    
    # DB 검증 (별도)
    db_result = db_check()
    results.insert(0, db_result)  # 맨 앞에 추가
    
    # 요약 계산
    total = len(results)
    ok_count = sum(1 for r in results if r.status == "ok")
    warn_count = sum(1 for r in results if r.status == "warn")
    fail_count = sum(1 for r in results if r.status == "fail")
    
    # 최대 severity 찾기
    severity_order = {"ok": 0, "minor": 1, "major": 2, "critical": 3}
    max_severity: Severity = max(
        (r.severity for r in results),
        key=lambda s: severity_order.get(s, 0),
    )
    
    summary = HealthSummary(
        total=total,
        ok=ok_count,
        warn=warn_count,
        fail=fail_count,
        severity=max_severity,
    )
    
    report = HealthReport(
        project="stock",
        timestamp=datetime.now().isoformat(),
        results=results,
        summary=summary,
    )
    
    return report


# =============================================================================
# CLI 엔트리포인트
# =============================================================================

def main() -> None:
    """메인 함수."""
    parser = argparse.ArgumentParser(
        description="주식부자프로젝트 헬스체크 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="JSON 출력 (기본값)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="상세 로그 출력",
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 검증 실행
    report = run_all_checks(verbose=args.verbose)
    
    # 결과 출력
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        # 텍스트 출력 (비상시용)
        print(f"# 헬스체크 리포트 - {report.timestamp}")
        print(f"총 {report.summary.total}개 검증: OK={report.summary.ok}, WARN={report.summary.warn}, FAIL={report.summary.fail}")
        print(f"최종 심각도: {report.summary.severity}")
        print()
        for r in report.results:
            status_symbol = {"ok": "✅", "warn": "⚠️", "fail": "❌"}[r.status]
            print(f"{status_symbol} [{r.id}] {r.name}: {r.detail}")


if __name__ == "__main__":
    main()
