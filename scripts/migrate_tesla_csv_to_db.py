"""Tesla CSV → SQLite ORM 마이그레이션 스크립트.

사용법:
    python3 scripts/migrate_tesla_csv_to_db.py --dry-run
    python3 scripts/migrate_tesla_csv_to_db.py --confirm
    python3 scripts/migrate_tesla_csv_to_db.py --csv-dir data/research/stocks/tesla/ --confirm
    python3 scripts/migrate_tesla_csv_to_db.py --only issues --confirm
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# 프로젝트 루트를 sys.path에 추가 (스크립트 직접 실행 지원)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.database import init_db
from src.core.models import (
    IssueStatus,
    MilestoneStatus,
    Sentiment,
    Severity,
    TeslaEssenceComponent,
    TeslaIssue,
    TeslaIssueCategory,
    TeslaMilestone,
    TeslaTaggedIssue,
    ThesisSide,
)
from src.storage.tesla_repository import (
    TeslaIssueRepository,
    TeslaMilestoneRepository,
    TeslaTaggedIssueRepository,
)


# ============================================================
# 변환 유틸리티
# ============================================================

def _empty_str_to_none(value: str) -> str | None:
    """빈 문자열을 None으로 변환. tesla_api.py _empty_str_to_none() 패턴 따름."""
    return None if value.strip() == "" else value


def _parse_date_utc_midnight(value: str) -> datetime | None:
    """날짜 문자열 'YYYY-MM-DD' → UTC 자정 datetime. 빈 값은 None 반환.

    Q6=옵션B: UTC 자정으로 통일 (KST 변환 없음).
    """
    v = _empty_str_to_none(value)
    if v is None:
        return None
    try:
        dt = datetime.strptime(v.strip(), "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _parse_related_entity_ids(value: str) -> list[str]:
    """related_entity_ids CSV 값 → list. 빈 값은 빈 리스트 반환."""
    v = value.strip()
    if not v:
        return []
    # 쉼표 구분 문자열이면 분리, 아니면 단일 항목으로
    return [x.strip() for x in v.split(",") if x.strip()]


# ============================================================
# 행 변환 함수
# ============================================================

def _row_to_issue(row: dict[str, str]) -> TeslaIssue | None:
    """CSV 행 → TeslaIssue Pydantic 모델.

    변환 실패 시 None 반환 (호출자가 skip 처리).
    """
    issue_id = row.get("issue_id", "").strip()
    if not issue_id:
        return None

    # category: "TSLA-E" → "E" → TeslaIssueCategory["E"] (by name)
    raw_category = row.get("category", "").strip()
    try:
        code = raw_category.split("-")[1]  # "TSLA-E" → "E"
        category = TeslaIssueCategory[code]
    except (IndexError, KeyError):
        raise ValueError(f"알 수 없는 category 값: {raw_category!r}")

    # essence_component: enum value 그대로 (nullable)
    raw_ec = _empty_str_to_none(row.get("essence_component", ""))
    essence_component: TeslaEssenceComponent | None = None
    if raw_ec is not None:
        try:
            essence_component = TeslaEssenceComponent(raw_ec)
        except ValueError:
            raise ValueError(f"알 수 없는 essence_component 값: {raw_ec!r}")

    # status: IssueStatus enum (by value)
    raw_status = row.get("status", "open").strip() or "open"
    try:
        status = IssueStatus(raw_status)
    except ValueError:
        raise ValueError(f"알 수 없는 status 값: {raw_status!r}")

    # severity: Severity enum (by value)
    raw_severity = row.get("severity", "moderate").strip() or "moderate"
    try:
        severity = Severity(raw_severity)
    except ValueError:
        raise ValueError(f"알 수 없는 severity 값: {raw_severity!r}")

    # thesis_side: ThesisSide enum (by value)
    raw_ts = row.get("thesis_side", "bull").strip() or "bull"
    try:
        thesis_side = ThesisSide(raw_ts)
    except ValueError:
        raise ValueError(f"알 수 없는 thesis_side 값: {raw_ts!r}")

    return TeslaIssue(
        id=issue_id,  # 도메인 ID = PK (8-C 결정)
        category=category,
        title=row.get("title", "").strip(),
        summary=row.get("summary", "") or "",
        essence_component=essence_component,
        severity=severity,
        status=status,
        thesis_side=thesis_side,
        first_occurred_at=_parse_date_utc_midnight(row.get("first_occurred_at", "")),
        last_event_at=_parse_date_utc_midnight(row.get("last_event_at", "")),
        deadline=_parse_date_utc_midnight(row.get("deadline", "")),
        blocker=_empty_str_to_none(row.get("blocker", "")) or "",
        owner=_empty_str_to_none(row.get("owner", "")) or "",
        related_topic_id=_empty_str_to_none(row.get("related_topic_id", "")) or "",
        related_entity_ids=_parse_related_entity_ids(row.get("related_entity_ids", "")),
        source_hint=_empty_str_to_none(row.get("source_hint", "")) or "",
        notion_page_id=_empty_str_to_none(row.get("notion_page_id", "")) or "",
        # created_at / updated_at: CSV 대부분 비어있으므로 Pydantic 기본값(_utcnow) 사용
    )


def _row_to_milestone(row: dict[str, str]) -> TeslaMilestone | None:
    """CSV 행 → TeslaMilestone Pydantic 모델."""
    milestone_id = row.get("milestone_id", "").strip()
    if not milestone_id:
        return None

    issue_id = row.get("issue_id", "").strip()
    if not issue_id:
        return None

    # status: MilestoneStatus enum (by value)
    raw_status = row.get("status", "planned").strip() or "planned"
    try:
        status = MilestoneStatus(raw_status)
    except ValueError:
        raise ValueError(f"알 수 없는 milestone status 값: {raw_status!r}")

    # confidence: int (0~100)
    raw_conf = row.get("confidence", "100").strip()
    try:
        confidence = int(raw_conf) if raw_conf else 100
    except ValueError:
        confidence = 100

    return TeslaMilestone(
        id=milestone_id,  # TSLA-E-001-M1 형식 PK
        issue_id=issue_id,
        title=row.get("title", "").strip(),
        occurred_at=_parse_date_utc_midnight(row.get("occurred_at", "")),
        target_at=_parse_date_utc_midnight(row.get("target_at", "")),
        status=status,
        confidence=confidence,
        evidence_url=_empty_str_to_none(row.get("evidence_url", "")) or "",
        source_hint=_empty_str_to_none(row.get("source_hint", "")) or "",
    )


def _row_to_tagged_issue(row: dict[str, str]) -> TeslaTaggedIssue | None:
    """CSV 행 → TeslaTaggedIssue Pydantic 모델."""
    issue_id = row.get("issue_id", "").strip()
    if not issue_id:
        return None

    # category: tagged_issues.csv는 enum value 그대로 ("essence", "product", ...)
    raw_category = row.get("category", "").strip()
    try:
        category = TeslaIssueCategory(raw_category)
    except ValueError:
        raise ValueError(f"알 수 없는 category 값: {raw_category!r}")

    # essence_component (nullable)
    raw_ec = _empty_str_to_none(row.get("essence_component", ""))
    essence_component: TeslaEssenceComponent | None = None
    if raw_ec is not None:
        try:
            essence_component = TeslaEssenceComponent(raw_ec)
        except ValueError:
            raise ValueError(f"알 수 없는 essence_component 값: {raw_ec!r}")

    # severity
    raw_severity = row.get("severity", "moderate").strip() or "moderate"
    try:
        severity = Severity(raw_severity)
    except ValueError:
        raise ValueError(f"알 수 없는 severity 값: {raw_severity!r}")

    # sentiment
    raw_sentiment = row.get("sentiment", "neutral").strip() or "neutral"
    try:
        sentiment = Sentiment(raw_sentiment)
    except ValueError:
        raise ValueError(f"알 수 없는 sentiment 값: {raw_sentiment!r}")

    # tagged_at: CSV "date" 컬럼
    tagged_at = _parse_date_utc_midnight(row.get("date", ""))
    if tagged_at is None:
        raise ValueError(f"tagged_at(date) 필드 누락 또는 변환 실패: {row.get('date', '')!r}")

    return TeslaTaggedIssue(
        id=issue_id,  # TSLA-I-001 등 PK
        title=row.get("title", "").strip(),
        category=category,
        essence_component=essence_component,
        severity=severity,
        sentiment=sentiment,
        tagged_at=tagged_at,
        summary=_empty_str_to_none(row.get("summary", "")) or "",
    )


# ============================================================
# CSV 파일 마이그레이션 함수
# ============================================================

def migrate_issues(csv_path: Path, dry_run: bool) -> tuple[int, int]:
    """issues.csv → tesla_issues 테이블 마이그레이션.

    Returns:
        (성공 건수, 스킵 건수)
    """
    repo = TeslaIssueRepository()
    success = 0
    skipped = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # 헤더 포함 line 2부터
            try:
                model = _row_to_issue(row)
                if model is None:
                    print(f"  [SKIP] issues.csv line {i}: issue_id 누락")
                    skipped += 1
                    continue
                if dry_run:
                    print(f"  [DRY] {model.id} | {model.title[:40]} | {model.status} | {model.thesis_side}")
                else:
                    repo.upsert(model)
                    print(f"  [OK]  {model.id} | {model.title[:40]}")
                success += 1
            except Exception as e:
                print(f"  [SKIP] issues.csv line {i}: {e}")
                skipped += 1

    return success, skipped


def migrate_milestones(csv_path: Path, dry_run: bool) -> tuple[int, int]:
    """milestones.csv → tesla_milestones 테이블 마이그레이션.

    Returns:
        (성공 건수, 스킵 건수)
    """
    repo = TeslaMilestoneRepository()
    success = 0
    skipped = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                model = _row_to_milestone(row)
                if model is None:
                    print(f"  [SKIP] milestones.csv line {i}: milestone_id 또는 issue_id 누락")
                    skipped += 1
                    continue
                if dry_run:
                    print(f"  [DRY] {model.id} | issue={model.issue_id} | {model.status} | conf={model.confidence}")
                else:
                    repo.upsert(model)
                    print(f"  [OK]  {model.id} | issue={model.issue_id}")
                success += 1
            except Exception as e:
                print(f"  [SKIP] milestones.csv line {i}: {e}")
                skipped += 1

    return success, skipped


def migrate_tagged_issues(csv_path: Path, dry_run: bool) -> tuple[int, int]:
    """tagged_issues.csv → tesla_tagged_issues 테이블 마이그레이션.

    Returns:
        (성공 건수, 스킵 건수)
    """
    repo = TeslaTaggedIssueRepository()
    success = 0
    skipped = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                model = _row_to_tagged_issue(row)
                if model is None:
                    print(f"  [SKIP] tagged_issues.csv line {i}: issue_id 누락")
                    skipped += 1
                    continue
                if dry_run:
                    print(f"  [DRY] {model.id} | {model.title[:40]} | {model.sentiment}")
                else:
                    repo.upsert(model)
                    print(f"  [OK]  {model.id} | {model.title[:40]}")
                success += 1
            except Exception as e:
                print(f"  [SKIP] tagged_issues.csv line {i}: {e}")
                skipped += 1

    return success, skipped


# ============================================================
# 적재 후 자동 검증
# ============================================================

def verify_counts() -> None:
    """적재 후 카운트 + 샘플 row 검증. 불일치 시 AssertionError 발생."""
    issue_repo = TeslaIssueRepository()
    milestone_repo = TeslaMilestoneRepository()
    tagged_repo = TeslaTaggedIssueRepository()

    issue_count = issue_repo.count()
    milestone_count = milestone_repo.count()
    tagged_count = tagged_repo.count()

    print(f"\n[검증] tesla_issues: {issue_count} (예상 10)")
    print(f"[검증] tesla_milestones: {milestone_count} (예상 24)")
    print(f"[검증] tesla_tagged_issues: {tagged_count} (예상 10)")

    assert issue_count == 10, f"tesla_issues 카운트 불일치: {issue_count} != 10"
    assert milestone_count == 24, f"tesla_milestones 카운트 불일치: {milestone_count} != 24"
    assert tagged_count == 10, f"tesla_tagged_issues 카운트 불일치: {tagged_count} != 10"

    sample = issue_repo.get_by_id("TSLA-E-001")
    assert sample is not None, "TSLA-E-001 조회 실패"
    assert "수직통합" in sample.title, f"TSLA-E-001 title 불일치: {sample.title!r}"

    print(f"[검증] TSLA-E-001 샘플: id={sample.id} | status={sample.status} | thesis_side={sample.thesis_side}")
    print("[검증] 모든 카운트/샘플 검증 통과 ✅")


# ============================================================
# 메인
# ============================================================

def main() -> None:
    """메인 진입점."""
    parser = argparse.ArgumentParser(description="Tesla CSV → SQLite ORM 마이그레이션")
    parser.add_argument("--dry-run", action="store_true", help="변환 결과만 출력, DB 적재 안 함")
    parser.add_argument("--confirm", action="store_true", help="실제 DB에 적재")
    parser.add_argument(
        "--csv-dir",
        default="data/research/stocks/tesla/",
        help="CSV 디렉토리 경로 (기본: data/research/stocks/tesla/)",
    )
    parser.add_argument(
        "--only",
        choices=["issues", "milestones", "tagged_issues"],
        default=None,
        help="특정 CSV만 마이그레이션",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.confirm:
        print("--dry-run 또는 --confirm 중 하나를 지정해야 합니다.")
        parser.print_help()
        sys.exit(1)

    dry_run = args.dry_run
    csv_dir = _PROJECT_ROOT / args.csv_dir

    if not csv_dir.exists():
        print(f"CSV 디렉토리를 찾을 수 없습니다: {csv_dir}")
        sys.exit(1)

    mode = "DRY-RUN" if dry_run else "CONFIRM"
    print(f"=== Tesla CSV → DB 마이그레이션 [{mode}] ===")
    print(f"CSV 디렉토리: {csv_dir}\n")

    # DB 테이블 존재 보장 (additive)
    init_db()

    total_success = 0
    total_skipped = 0

    # 순서: issues → milestones (FK 의존) → tagged_issues (독립)
    run_issues = args.only in (None, "issues")
    run_milestones = args.only in (None, "milestones")
    run_tagged = args.only in (None, "tagged_issues")

    if run_issues:
        issues_csv = csv_dir / "issues.csv"
        if issues_csv.exists():
            print(f"[1/3] issues.csv 처리 중...")
            try:
                s, sk = migrate_issues(issues_csv, dry_run)
                total_success += s
                total_skipped += sk
                print(f"      → 성공 {s}건, 스킵 {sk}건\n")
            except Exception as e:
                print(f"      [ERROR] issues.csv 전체 실패: {e}\n")
        else:
            print(f"[1/3] issues.csv 파일 없음: {issues_csv}\n")

    if run_milestones:
        milestones_csv = csv_dir / "milestones.csv"
        if milestones_csv.exists():
            print(f"[2/3] milestones.csv 처리 중...")
            try:
                s, sk = migrate_milestones(milestones_csv, dry_run)
                total_success += s
                total_skipped += sk
                print(f"      → 성공 {s}건, 스킵 {sk}건\n")
            except Exception as e:
                print(f"      [ERROR] milestones.csv 전체 실패: {e}\n")
        else:
            print(f"[2/3] milestones.csv 파일 없음: {milestones_csv}\n")

    if run_tagged:
        tagged_csv = csv_dir / "tagged_issues.csv"
        if tagged_csv.exists():
            print(f"[3/3] tagged_issues.csv 처리 중...")
            try:
                s, sk = migrate_tagged_issues(tagged_csv, dry_run)
                total_success += s
                total_skipped += sk
                print(f"      → 성공 {s}건, 스킵 {sk}건\n")
            except Exception as e:
                print(f"      [ERROR] tagged_issues.csv 전체 실패: {e}\n")
        else:
            print(f"[3/3] tagged_issues.csv 파일 없음: {tagged_csv}\n")

    print(f"=== 마이그레이션 완료: 성공 {total_success}건, 스킵 {total_skipped}건 ===")

    if args.confirm:
        print()
        verify_counts()


if __name__ == "__main__":
    main()
