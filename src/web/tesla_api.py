"""Tesla API 엔드포인트.

CSV 파일에서 데이터를 읽어서 반환하는 FastAPI 라우터.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

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


def _compute_is_past(occurred_at_str):
    """날짜 문자열이 오늘 이전인지 계산."""
    from datetime import date, datetime
    d = datetime.strptime(occurred_at_str, '%Y-%m-%d').date()
    return d < date.today()


def _days_offset(occurred_at_str):
    """오늘부터 날짜까지의 일수 차이 (음수=과거, 양수=미래)."""
    from datetime import date, datetime
    d = datetime.strptime(occurred_at_str, '%Y-%m-%d').date()
    return (d - date.today()).days


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


# JSON 파일 로딩 헬퍼 함수
def _load_json(json_name: str) -> dict[str, Any]:
    """JSON 파일을 로딩하여 딕셔너리로 반환.

    파일이 없으면 빈 딕셔너리 반환.
    """
    json_path = _CSV_DIR / json_name
    if not json_path.exists():
        return {}

    try:
        content = json_path.read_text(encoding="utf-8")
        return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return {}


@router.get("/thesis")
def get_thesis() -> dict:
    """Tesla 투자 논제(Thesis) 데이터를 반환한다.

    Returns:
        date: 업데이트 날짜
        overall_score: 전체 점수 (0-100)
        overall_label: 전체 라벨 (Bearish/Cautiously Bearish/Neutral/Cautiously Bullish/Bullish)
        bull_count: Bull 요소 개수
        bear_count: Bear 요소 개수
        net_delta: 순 delta 합
        bull: Bull 요소 리스트 (occurred_at 내림차순)
            - 각 아이템에 is_past, days_offset 추가
        bear: Bear 요소 리스트 (occurred_at 내림차순)
            - 각 아이템에 is_past, days_offset 추가
    """
    data = _load_json("thesis.json")

    # 기본값 설정
    bull_items = data.get("bull", [])
    bear_items = data.get("bear", [])

    # delta 합 계산
    bull_delta_sum = sum(item.get("delta", 0) for item in bull_items)
    bear_delta_sum = sum(item.get("delta", 0) for item in bear_items)
    net_delta = bull_delta_sum + bear_delta_sum  # bear delta는 음수여야 함

    # overall_score 계산: 기본 50 + net*2, 0~100 클램프
    overall_score = max(0, min(100, 50 + net_delta * 2))

    # overall_label 결정
    if overall_score < 35:
        overall_label = "Bearish"
    elif overall_score < 45:
        overall_label = "Cautiously Bearish"
    elif overall_score < 55:
        overall_label = "Neutral"
    elif overall_score < 70:
        overall_label = "Cautiously Bullish"
    else:
        overall_label = "Bullish"

    # bull/bear 리스트에 is_past, days_offset 추가하고 내림차순 정렬
    def enrich_and_sort(items):
        enriched = []
        for item in items:
            occurred_at = item.get("occurred_at", "")
            if occurred_at:
                item_enriched = {
                    **item,
                    "is_past": _compute_is_past(occurred_at),
                    "days_offset": _days_offset(occurred_at),
                }
                enriched.append(item_enriched)
            else:
                # occurred_at이 없는 경우도 포함
                enriched.append(item)
        # occurred_at 내림차순 정렬 (최신이 위)
        enriched.sort(key=lambda x: x.get("occurred_at", ""), reverse=True)
        return enriched

    return {
        "date": data.get("date", ""),
        "overall_score": overall_score,
        "overall_label": overall_label,
        "bull_count": len(bull_items),
        "bear_count": len(bear_items),
        "net_delta": net_delta,
        "bull": enrich_and_sort(bull_items),
        "bear": enrich_and_sort(bear_items),
    }


@router.get("/timeline")
def get_timeline(
    days_back: int = Query(default=30, ge=0, description="오늘로부터 몇 일 전까지"),
    days_forward: int = Query(default=60, ge=0, description="오늘로부터 몇 일 후까지")
) -> dict:
    """Tesla 타임라인 이벤트를 반환한다 (오늘 기준 필터링).

    Args:
        days_back: 오늘로부터 몇 일 전까지 (기본 30)
        days_forward: 오늘로부터 몇 일 후까지 (기본 60)

    Returns:
        today: 오늘 날짜 (YYYY-MM-DD)
        days_back: 조회 기간 (과거 방향 일수)
        days_forward: 조회 기간 (미래 방향 일수)
        topics: 토픽 리스트 (robotaxi, fsd, optimus, 4680, megapack, other 순서)
            - id: 토픽 ID
            - name_ko: 한국어 이름
            - essence_component: 연결된 본질 축
        events: 필터링된 이벤트 리스트
            - occurred_at: 사건 발생일, not 수집일
            - days_offset: 오늘로부터의 일수 차이
            - is_past: 과거 여부
            - topic: 토픽 ID (null인 경우 프론트에서 'other'로 매핑)
    """
    from datetime import date, timedelta

    # topics_quarterly.json에서 토픽 로딩
    topics_data = _load_json("topics_quarterly.json")
    all_topics = topics_data.get("topics", [])

    # 토픽 ID로 매핑 생성
    topics_map = {t.get("id"): t for t in all_topics}

    # 지정된 순서대로 topics 배열 생성
    topic_order = ["robotaxi", "fsd", "optimus", "4680", "megapack"]
    topics = []

    for topic_id in topic_order:
        if topic_id in topics_map:
            topic = topics_map[topic_id]
            topics.append({
                "id": topic.get("id"),
                "name_ko": topic.get("name_ko"),
                "essence_component": topic.get("essence_component"),
            })

    # 'other' 토픽 하드코딩 추가
    topics.append({
        "id": "other",
        "name_ko": "기타",
        "essence_component": None,
    })

    # 타임라인 이벤트 로딩
    data = _load_json("timeline_events.json")
    # JSON이 리스트(배열)이면 직접 사용, dict이면 events 키에서 추출
    events = data if isinstance(data, list) else data.get("events", [])

    today = date.today()

    # 필터링 범위
    start_date = today - timedelta(days=days_back)
    end_date = today + timedelta(days=days_forward)

    filtered_events = []
    for event in events:
        occurred_at = event.get("occurred_at", "")
        if not occurred_at:
            continue

        try:
            from datetime import datetime
            event_date = datetime.strptime(occurred_at, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        # 범위 체크
        if not (start_date <= event_date <= end_date):
            continue

        # days_offset, is_past 계산
        days_offset = (event_date - today).days
        is_past = days_offset < 0

        filtered_events.append({
            **event,
            "days_offset": days_offset,
            "is_past": is_past,
        })

    # occurred_at 오름차순 정렬
    filtered_events.sort(key=lambda e: e.get("occurred_at", ""))

    return {
        "today": today.isoformat(),
        "days_back": days_back,
        "days_forward": days_forward,
        "topics": topics,
        "events": filtered_events,
    }


@router.get("/topics")
def get_topics() -> dict:
    """Tesla 토픽 목록을 반환한다 (quarters 제외, 가볍게).

    Returns:
        topics: 토픽 리스트
            - id: 토픽 ID
            - name: 영어 이름
            - name_ko: 한국어 이름
            - status: 상태
            - essence_component: 연결된 본질 축
            - current_progress_pct: 현재 진행률
            - summary: 요약
    """
    data = _load_json("topics_quarterly.json")
    topics = data.get("topics", [])

    # 가볍게: 필요한 필드만 추출
    light_topics = []
    for topic in topics:
        light_topics.append({
            "id": topic.get("id", ""),
            "name": topic.get("name", ""),
            "name_ko": topic.get("name_ko", ""),
            "status": topic.get("status", ""),
            "essence_component": topic.get("essence_component", ""),
            "current_progress_pct": topic.get("current_progress_pct", 0),
            "summary": topic.get("summary", ""),
        })

    return {"topics": light_topics}


@router.get("/topics/{topic_id}/quarterly")
def get_topic_quarterly(topic_id: str) -> dict:
    """특정 토픽의 분기별 상세 정보를 반환한다.

    Args:
        topic_id: 토픽 ID

    Returns:
        topic: 토픽 정보 (전체)
        quarters: 분기별 데이터 리스트
            - 각 분기에 is_past 추가 (서버 계산)
            - 각 event에 days_offset 추가
            - events는 occurred_at 또는 expected_start 기준 오름차순 정렬
    """
    from datetime import date, datetime

    data = _load_json("topics_quarterly.json")
    topics = data.get("topics", [])

    # 해당 토픽 찾기
    target_topic = None
    for topic in topics:
        if topic.get("id") == topic_id:
            target_topic = topic
            break

    if target_topic is None:
        return {"topic": None, "quarters": []}

    quarters = target_topic.get("quarters", [])
    today = date.today()

    enriched_quarters = []
    for quarter in quarters:
        # 분기의 is_past 계산: 분기 종료월 마지막 날짜 < today
        # 예: 2024Q3 → 2024-09-30
        quarter_str = quarter.get("period", "") or quarter.get("quarter", "")
        is_past = False
        try:
            # 분기 문자열 파싱 (예: "2024Q3")
            if "Q" in quarter_str:
                year, q_num = quarter_str.split("Q")
                year = int(year)
                q_num = int(q_num)
                # 분기 종료월 계산
                end_month = q_num * 3  # Q1→3, Q2→6, Q3→9, Q4→12
                # 해당 월의 마지막 날짜 계산
                if end_month == 12:
                    end_date = date(year, 12, 31)
                else:
                    # 다음 달 1일에서 1일 빼기
                    end_date = date(year, end_month + 1, 1)
                    from datetime import timedelta
                    end_date = end_date - timedelta(days=1)
                is_past = end_date < today
        except (ValueError, TypeError):
            pass

        # events 정렬 및 days_offset 추가
        events = quarter.get("events", [])
        enriched_events = []
        for event in events:
            # occurred_at 또는 expected_start 사용
            event_date_str = event.get("occurred_at") or event.get("expected_start", "")
            event_enriched = {**event}
            if event_date_str:
                try:
                    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
                    event_enriched["days_offset"] = (event_date - today).days
                except (ValueError, TypeError):
                    pass
            enriched_events.append(event_enriched)

        # events 정렬: occurred_at 또는 expected_start 기준 오름차순
        enriched_events.sort(key=lambda e: e.get("occurred_at") or e.get("expected_start", ""))

        enriched_quarters.append({
            **quarter,
            "is_past": is_past,
            "events": enriched_events,
        })

    return {
        "topic": target_topic,
        "quarters": enriched_quarters,
    }


@router.get("/issues")
def get_issues(
    category: str | None = Query(default=None, description="카테고리 필터"),
    status: str | None = Query(default=None, description="상태 필터"),
    thesis_side: str | None = Query(default=None, description="테시스 방향 필터"),
    essence_component: str | None = Query(default=None, description="본질 축 필터"),
    limit: int = Query(default=50, ge=1, le=200, description="반환할 최대 이슈 수")
) -> dict:
    """Tesla 이슈 목록을 반환한다 (필터링 가능).

    Args:
        category: 카테고리 필터 (선택)
        status: 상태 필터 (선택)
        thesis_side: 테시스 방향 필터 (선택)
        essence_component: 본질 축 필터 (선택)
        limit: 반환할 최대 이슈 수 (기본 50, 최대 200)

    Returns:
        issues: 필터링된 이슈 리스트
            - 빈 문자열은 null로 변환
            - date 필드는 문자열 그대로 반환
        total: 필터 후 전체 건수
    """
    from fastapi import HTTPException

    rows = _load_csv("issues.csv")

    # 빈 문자열을 None으로 변환하는 헬퍼 함수
    def _empty_str_to_none(value: str | None) -> str | None:
        if value is None or value == "":
            return None
        return value

    # 필터링 적용
    filtered = []
    for row in rows:
        # 각 필터 조건 확인 (값이 있을 때만 필터링)
        if category is not None and row.get("category") != category:
            continue
        if status is not None and row.get("status") != status:
            continue
        if thesis_side is not None and row.get("thesis_side") != thesis_side:
            continue
        if essence_component is not None and row.get("essence_component") != essence_component:
            continue
        filtered.append(row)

    # last_event_at 기준 내림차순 정렬 (빈 값은 맨 뒤)
    def _sort_key(row: dict) -> tuple:
        """정렬 키: 빈 값은 최우선 순위로 뒤로 보냄."""
        last_event_at = row.get("last_event_at", "")
        if last_event_at == "" or last_event_at is None:
            return (0, "")  # 빈 값은 맨 뒤
        return (1, last_event_at)  # 있는 값은 앞쪽, 날짜순

    filtered.sort(key=_sort_key, reverse=True)

    # 전체 건수 (limit 적용 전)
    total = len(filtered)

    # limit 적용
    filtered = filtered[:limit]

    # 결과 변환 (빈 문자열 → None)
    issues = []
    for row in filtered:
        issue = {}
        for key, value in row.items():
            issue[key] = _empty_str_to_none(value)
        issues.append(issue)

    return {"issues": issues, "total": total}


@router.get("/issues/{issue_id}")
def get_issue_detail(issue_id: str) -> dict:
    """특정 Tesla 이슈의 상세 정보와 연결된 마일스톤을 반환한다.

    Args:
        issue_id: 이슈 ID

    Returns:
        issue: 이슈 상세 정보 (빈 문자열은 null로 변환)
        milestones: 연결된 마일스톤 리스트
            - occurred_at 또는 target_at 기준 오름차순 정렬
            - 둘 다 있으면 occurred_at 우선
            - 빈 문자열은 null로 변환

    Raises:
        404: 이슈를 찾을 수 없는 경우
    """
    from fastapi import HTTPException

    # 빈 문자열을 None으로 변환하는 헬퍼 함수
    def _empty_str_to_none(value: str | None) -> str | None:
        if value is None or value == "":
            return None
        return value

    # issues.csv에서 해당 issue_id 찾기
    issues = _load_csv("issues.csv")
    target_issue = None
    for row in issues:
        if row.get("issue_id") == issue_id:
            target_issue = row
            break

    if target_issue is None:
        raise HTTPException(status_code=404, detail=f"Issue '{issue_id}' not found")

    # issue에서 빈 문자열 → None 변환
    issue_cleaned = {}
    for key, value in target_issue.items():
        issue_cleaned[key] = _empty_str_to_none(value)

    # milestones.csv에서 해당 issue_id의 마일스톤 찾기
    milestones = _load_csv("milestones.csv")
    filtered_milestones = []
    for row in milestones:
        if row.get("issue_id") == issue_id:
            filtered_milestones.append(row)

    # 마일스톤 정렬: occurred_at 또는 target_at 기준 오름차순
    def _milestone_sort_key(row: dict) -> tuple:
        """마일스톤 정렬 키: occurred_at 우선, 없으면 target_at 사용."""
        occurred_at = row.get("occurred_at") or ""
        target_at = row.get("target_at") or ""

        # occurred_at가 있으면 우선, 없으면 target_at 사용
        if occurred_at and occurred_at != "":
            return (1, occurred_at)  # occurred_at가 있는 경우 우선
        elif target_at and target_at != "":
            return (0, target_at)   # target_at만 있는 경우
        else:
            return (-1, "")         # 둘 다 없는 경우 맨 뒤

    filtered_milestones.sort(key=_milestone_sort_key)

    # 마일스톤에서 빈 문자열 → None 변환
    milestones_cleaned = []
    for row in filtered_milestones:
        milestone_cleaned = {}
        for key, value in row.items():
            milestone_cleaned[key] = _empty_str_to_none(value)
        milestones_cleaned.append(milestone_cleaned)

    return {
        "issue": issue_cleaned,
        "milestones": milestones_cleaned,
    }
