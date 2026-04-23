"""Tesla API 엔드포인트.

CSV 파일에서 데이터를 읽어서 반환하는 FastAPI 라우터.
"""

from __future__ import annotations

import csv
from pathlib import Path

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/tesla", tags=["tesla"])

# CSV 파일 경로
_CSV_DIR = Path("data/research/stocks/tesla")


def _load_csv(csv_name: str) -> list[dict]:
    """CSV 파일을 로딩하여 딕셔너리 리스트로 반환.
    
    파일이 없으면 빈 리스트 반환.
    """
    csv_path = _CSV_DIR / csv_name
    if not csv_path.exists():
        return []
    
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def _to_int(value: str | None, default: int = 0) -> int:
    """문자열을 정수로 변환. 실패하면 default 반환."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _to_float(value: str | None, default: float = 0.0) -> float:
    """문자열을 실수로 변환. 실패하면 default 반환."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


@router.get("/essence")
def get_essence_scores() -> dict:
    """Tesla 본질 점수 데이터를 반환한다.
    
    Returns:
        components: 본질 축별 점수 리스트
            - name: 컴포넌트 이름
            - label_ko: 한국어 라벨
            - score: 점수
            - delta_7d: 7일 변화
            - last_event_title: 최근 이벤트 제목
            - last_event_date: 최근 이벤트 날짜
            - color: 표시 색상
    """
    rows = _load_csv("essence_scores.csv")
    
    components = []
    for row in rows:
        components.append({
            "name": row.get("component", ""),
            "label_ko": row.get("label_ko", ""),
            "score": _to_int(row.get("score")),
            "delta_7d": row.get("delta_7d", ""),
            "last_event_title": row.get("last_event_title", ""),
            "last_event_date": row.get("last_event_date", ""),
            "color": row.get("color", ""),
        })
    
    return {"components": components}


@router.get("/moat")
def get_moat_status() -> dict:
    """Tesla 경제적 해자(Moat) 현황을 반환한다.
    
    Returns:
        moats: 해자 유형별 현황 리스트
            - moat_type: 해자 유형
            - label_ko: 한국어 라벨
            - strength: 강도 (0-100)
            - trend: 추세 (improving/stable/declining)
            - threat_summary: 위협 요약
    """
    rows = _load_csv("moat_status.csv")
    
    moats = []
    for row in rows:
        moats.append({
            "moat_type": row.get("moat_type", ""),
            "label_ko": row.get("label_ko", ""),
            "strength": _to_int(row.get("strength")),
            "trend": row.get("trend", ""),
            "threat_summary": row.get("threat_summary", ""),
        })
    
    return {"moats": moats}


@router.get("/master-plan")
def get_master_plan() -> dict:
    """Tesla 마스터플랜 이니셔티브 현황을 반환한다.
    
    Returns:
        initiatives: 이니셔티브 리스트
            - initiative: 이니셔티브 ID
            - label_ko: 한국어 라벨
            - progress_pct: 진행률 (%)
            - status: 상태 (on_track/in_progress/at_risk)
            - next_milestone: 다음 마일스톤
            - target_date: 목표 날짜
            - essence_component: 연결된 본질 축
    """
    rows = _load_csv("master_plan.csv")
    
    initiatives = []
    for row in rows:
        initiatives.append({
            "initiative": row.get("initiative", ""),
            "label_ko": row.get("label_ko", ""),
            "progress_pct": _to_int(row.get("progress_pct")),
            "status": row.get("status", ""),
            "next_milestone": row.get("next_milestone", ""),
            "target_date": row.get("target_date", ""),
            "essence_component": row.get("essence_component", ""),
        })
    
    return {"initiatives": initiatives}


@router.get("/issues/tagged")
def get_tagged_issues(
    limit: int = Query(default=20, ge=1, le=100, description="반환할 최대 이슈 수")
) -> dict:
    """Tesla 관련 태그된 이슈 목록을 반환한다 (날짜 역순).
    
    Args:
        limit: 반환할 최대 이슈 수 (기본 20, 최대 100)
    
    Returns:
        issues: 이슈 리스트
            - issue_id: 이슈 ID
            - title: 제목
            - category: 카테고리 (initiative/product/capability/factory/essence/musk_statement/regulatory)
            - essence_component: 연결된 본질 축
            - severity: 심각도 (critical/major/moderate/minor)
            - sentiment: 감정 (positive/negative/neutral)
            - date: 날짜
            - summary: 요약
        total: 전체 이슈 수
    """
    rows = _load_csv("tagged_issues.csv")
    
    # 날짜 역순 정렬
    rows.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # limit 적용
    rows = rows[:limit]
    
    issues = []
    for row in rows:
        issues.append({
            "issue_id": row.get("issue_id", ""),
            "title": row.get("title", ""),
            "category": row.get("category", ""),
            "essence_component": row.get("essence_component", ""),
            "severity": row.get("severity", ""),
            "sentiment": row.get("sentiment", ""),
            "date": row.get("date", ""),
            "summary": row.get("summary", ""),
        })
    
    # 전체 개수는 원본 rows 길이 (limit 적용 전)
    total = len(_load_csv("tagged_issues.csv"))
    
    return {"issues": issues, "total": total}
