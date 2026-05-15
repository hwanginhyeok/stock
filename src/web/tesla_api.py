"""Tesla API 엔드포인트.

CSV 파일에서 데이터를 읽어서 반환하는 FastAPI 라우터.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from time import mktime
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
    days_back: int = Query(default=2500, ge=0, description="오늘로부터 몇 일 전까지"),
    days_forward: int = Query(default=365, ge=0, description="오늘로부터 몇 일 후까지"),
    importance_level: str = Query(default="important", pattern="^(core|important|all)$"),
) -> dict:
    """Tesla 타임라인 이벤트를 importance 점수로 필터링하여 반환한다.

    Args:
        days_back: 오늘로부터 몇 일 전까지 (기본 30)
        days_forward: 오늘로부터 몇 일 후까지 (기본 60)
        importance_level: 중요도 필터 (core/important/all, 기본 important)
    """
    from datetime import date, timedelta

    # importance 문자열 → 숫자 매핑
    IMPORTANCE_SCORES: dict[str, int] = {
        "critical": 20, "major": 12, "moderate": 6, "minor": 3,
    }
    # importance_level별 임계값
    LEVEL_THRESHOLDS: dict[str, int] = {
        "core": 15, "important": 10, "all": 1,
    }

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
    events = data if isinstance(data, list) else data.get("events", [])

    today = date.today()

    # 필터링 범위
    start_date = today - timedelta(days=days_back)
    end_date = today + timedelta(days=days_forward)

    scored_events = []
    for event in events:
        occurred_at = event.get("occurred_at", "")
        if not occurred_at:
            continue

        try:
            event_date = datetime.strptime(occurred_at, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        if not (start_date <= event_date <= end_date):
            continue

        days_offset = (event_date - today).days
        is_past = days_offset < 0

        # importance 점수 계산: base × freshness_bonus
        base_score = IMPORTANCE_SCORES.get(event.get("importance", "minor"), 3)
        abs_days = abs(days_offset)
        if abs_days <= 7:
            freshness_bonus = 1.5
        elif abs_days <= 30:
            freshness_bonus = 1.2
        else:
            freshness_bonus = 1.0
        importance_score = round(base_score * freshness_bonus, 1)

        scored_events.append({
            **event,
            "days_offset": days_offset,
            "is_past": is_past,
            "importance_score": importance_score,
        })

    # 각 레벨별 건수 계산 (필터 전)
    counts = {
        "total": len(scored_events),
        "core": sum(1 for e in scored_events if e["importance_score"] >= LEVEL_THRESHOLDS["core"]),
        "important": sum(1 for e in scored_events if e["importance_score"] >= LEVEL_THRESHOLDS["important"]),
        "all": len(scored_events),
    }

    # importance_level 기반 필터
    min_score = LEVEL_THRESHOLDS.get(importance_level, 10)
    filtered_events = [e for e in scored_events if e["importance_score"] >= min_score]

    # importance_score 내림차순 → occurred_at 오름차순
    filtered_events.sort(key=lambda e: (-e["importance_score"], e.get("occurred_at", "")))

    return {
        "today": today.isoformat(),
        "days_back": days_back,
        "days_forward": days_forward,
        "importance_level": importance_level,
        "counts": counts,
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


# ---------------------------------------------------------------------------
# yfinance / feedparser 기반 실시간 엔드포인트
# ---------------------------------------------------------------------------

@router.get("/price")
def get_price() -> dict:
    """yfinance로 TSLA 현재 주가를 반환한다."""
    try:
        import yfinance as yf  # noqa: WPS433

        ticker = yf.Ticker("TSLA")
        info = ticker.info or {}
        fast = ticker.fast_info

        price = fast.last_price if hasattr(fast, "last_price") and fast.last_price else None
        prev_close = fast.previous_close if hasattr(fast, "previous_close") else None
        if price is None:
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
        if prev_close is None:
            prev_close = info.get("previousClose") or price

        change = round(price - prev_close, 2) if price and prev_close else 0.0
        change_pct = round(change / prev_close * 100, 2) if prev_close else 0.0

        return {
            "price": round(price, 2),
            "change": change,
            "change_pct": change_pct,
            "open": info.get("open") or info.get("regularMarketOpen") or 0.0,
            "high": info.get("dayHigh") or info.get("regularMarketDayHigh") or 0.0,
            "low": info.get("dayLow") or info.get("regularMarketDayLow") or 0.0,
            "volume": info.get("volume") or info.get("regularMarketVolume") or 0,
            "market_cap": info.get("marketCap") or 0,
            "week52_high": info.get("fiftyTwoWeekHigh") or 0.0,
            "week52_low": info.get("fiftyTwoWeekLow") or 0.0,
            "pe_ratio": info.get("trailingPE") or 0.0,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
    except Exception:
        return {
            "price": 0.0, "change": 0.0, "change_pct": 0.0,
            "open": 0.0, "high": 0.0, "low": 0.0,
            "volume": 0, "market_cap": 0,
            "week52_high": 0.0, "week52_low": 0.0,
            "pe_ratio": 0.0, "updated_at": "",
        }


@router.get("/chart")
def get_chart(
    period: str = Query(default="1mo", description="조회 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y)"),
    interval: str = Query(default="1d", description="봉 간격 (1m, 5m, 1h, 1d)"),
) -> dict:
    """yfinance history로 주가 히스토리를 반환한다."""
    try:
        import yfinance as yf  # noqa: WPS433

        ticker = yf.Ticker("TSLA")
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            return {"period": period, "interval": interval, "data": []}

        data = []
        for index, row in hist.iterrows():
            item = {
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            }
            # 인덱스 타입에 따라 date 필드 생성
            ts = index
            if hasattr(ts, "date"):
                item["date"] = ts.date().isoformat()  # "2026-04-09" (timezone 제거)
            elif hasattr(ts, "isoformat"):
                item["date"] = ts.isoformat()[:10]
            else:
                item["date"] = str(ts)[:10]
            data.append(item)

        return {"period": period, "interval": interval, "data": data}
    except Exception:
        return {"period": period, "interval": interval, "data": []}


@router.get("/options")
def get_options() -> dict:
    """가장 가까운 만기 TSLA 옵션 요약을 반환한다."""
    try:
        import yfinance as yf  # noqa: WPS433

        ticker = yf.Ticker("TSLA")
        expirations = ticker.options
        if not expirations:
            return _empty_options()

        # 오늘이 만기일이면 다음 만기로 fallback
        from datetime import date
        today_str = date.today().isoformat()
        exp = next((e for e in expirations if e > today_str), expirations[0])
        opt = ticker.option_chain(exp)
        calls = opt.calls
        puts = opt.puts

        if calls.empty or puts.empty:
            return _empty_options(exp)

        # 현재가
        fast = ticker.fast_info
        current_price = float(fast.last_price) if hasattr(fast, "last_price") and fast.last_price else 0.0

        # ATM strike 찾기
        atm_strike = float(calls.iloc[(calls["strike"] - current_price).abs().argsort().iloc[0]]["strike"])

        # ATM IV
        atm_call_row = calls[(calls["strike"] == atm_strike)]
        atm_put_row = puts[(puts["strike"] == atm_strike)]
        atm_call_iv = float(atm_call_row["impliedVolatility"].iloc[0]) if not atm_call_row.empty else 0.0
        atm_put_iv = float(atm_put_row["impliedVolatility"].iloc[0]) if not atm_put_row.empty else 0.0

        # P/C ratio (총 OI 기준)
        total_call_oi = int(calls["openInterest"].sum())
        total_put_oi = int(puts["openInterest"].sum())
        pc_ratio = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 0.0

        # ATM ±20% 범위 내 OI 상위 5개
        lo = current_price * 0.8
        hi = current_price * 1.2

        def _top5(df: "pandas.DataFrame") -> list[dict]:
            mask = (df["strike"] >= lo) & (df["strike"] <= hi)
            filtered = df[mask].nlargest(5, "openInterest")
            return [
                {
                    "strike": float(r["strike"]),
                    "oi": int(r["openInterest"]),
                    "iv": round(float(r["impliedVolatility"]), 4),
                    "last": round(float(r["lastPrice"]), 2),
                }
                for _, r in filtered.iterrows()
            ]

        top_calls = _top5(calls)
        top_puts = _top5(puts)

        return {
            "expiration": exp,
            "current_price": round(current_price, 2),
            "atm_call_iv": round(atm_call_iv, 4),
            "atm_put_iv": round(atm_put_iv, 4),
            "pc_ratio": pc_ratio,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "top_calls": top_calls,
            "top_puts": top_puts,
        }
    except Exception:
        return _empty_options()


def _empty_options(expiration: str = "") -> dict:
    """옵션 빈 응답 기본 구조."""
    return {
        "expiration": expiration,
        "current_price": 0.0,
        "atm_call_iv": 0.0,
        "atm_put_iv": 0.0,
        "pc_ratio": 0.0,
        "total_call_oi": 0,
        "total_put_oi": 0,
        "top_calls": [],
        "top_puts": [],
    }


@router.get("/news")
def get_news(
    limit: int = Query(default=10, ge=1, le=30, description="반환할 최대 기사 수"),
) -> dict:
    """Teslarati + Electrek Tesla RSS 최신 뉴스를 반환한다."""
    try:
        import feedparser  # noqa: WPS433

        FEEDS = [
            ("Teslarati", "https://www.teslarati.com/feed/"),
            ("Electrek", "https://electrek.co/guides/tesla/feed/"),
        ]

        articles: list[dict] = []
        for source, url in FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    published = ""
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime.fromtimestamp(mktime(entry.published_parsed)).isoformat(timespec="seconds")
                    elif hasattr(entry, "published"):
                        published = entry.published

                    summary = ""
                    if hasattr(entry, "summary"):
                        clean = re.sub(r'<[^>]+>', '', entry.summary)
                        clean = re.sub(r'\s+', ' ', clean).strip()
                        summary = clean[:200]

                    articles.append({
                        "title": getattr(entry, "title", ""),
                        "url": getattr(entry, "link", ""),
                        "source": source,
                        "published": published,
                        "summary": summary,
                    })
            except Exception:
                continue

        # published 내림차순 정렬
        articles.sort(key=lambda a: a.get("published", ""), reverse=True)
        articles = articles[:limit]

        return {"articles": articles}
    except Exception:
        return {"articles": []}


# 모멘텀 실데이터 캐시 (5분 TTL)
_MOMENTUM_CACHE: dict[str, Any] = {"data": None, "ts": 0.0}
_MOMENTUM_TTL = 300.0


def _compute_momentum_realtime() -> dict[str, Any] | None:
    """yfinance TSLA 일봉으로 SMA 정배열 + 매수 시그널 + 점수 계산.

    Returns:
        dict: trend_alignment, score, delta_3d, comment, signal 정보.
        실패/데이터 부족 시 None.
    """
    import time

    now = time.time()
    cached = _MOMENTUM_CACHE.get("data")
    if cached is not None and now - _MOMENTUM_CACHE.get("ts", 0.0) < _MOMENTUM_TTL:
        return cached

    try:
        import yfinance as yf  # noqa: WPS433

        from src.analyzers.sma_signals import (
            classify_sma_alignment,
            detect_pullback_buy_signal,
        )

        hist = yf.Ticker("TSLA").history(period="1y", interval="1d")
        if hist is None or len(hist) < 120:
            return None

        align = classify_sma_alignment(hist)
        if align.get("alignment") in (None, "N/A"):
            return None

        sig = detect_pullback_buy_signal(hist, alignment_result=align)

        alignment = align["alignment"]
        close_vs_vwma = align.get("close_vs_vwma_pct") or 0.0

        # 점수 산정
        base = {"정배열": 70, "혼재": 50, "역배열": 25}.get(alignment, 50)
        if close_vs_vwma >= 5:
            base += 8
        elif close_vs_vwma >= 0:
            base += 4
        elif close_vs_vwma <= -5:
            base -= 8
        else:
            base -= 4
        if sig.get("signal"):
            base += 10
        score = max(0, min(100, base))

        # 3일 전 alignment 변화 (간단 비교)
        delta_3d = ""
        if len(hist) >= 3:
            try:
                prev_align = classify_sma_alignment(hist.iloc[:-3])
                prev_score = {"정배열": 70, "혼재": 50, "역배열": 25}.get(
                    prev_align.get("alignment"), 50
                )
                diff = score - prev_score
                if diff != 0:
                    delta_3d = f"{diff:+d}"
            except Exception:
                pass

        # 코멘트 조립
        v = align.get("values", {})
        chain_parts = []
        for p in (5, 10, 20, 50):
            if f"sma_{p}" in v:
                chain_parts.append(f"SMA{p} ${v[f'sma_{p}']:.2f}")
        if "vwma_100" in v:
            chain_parts.append(f"VWMA100 ${v['vwma_100']:.2f}")
        chain_str = " · ".join(chain_parts)

        if sig.get("signal"):
            comment = f"매수 시그널 발동 — {sig.get('reason', '')}"
        else:
            comment = f"{alignment} · VWMA100 {close_vs_vwma:+.1f}%"

        data = {
            "trend_alignment": alignment,
            "score": score,
            "delta_3d": delta_3d,
            "comment": comment,
            "chain_str": chain_str,
            "signal": sig,
            "values": v,
            "close_vs_vwma_pct": close_vs_vwma,
            "current_price": float(hist.iloc[-1]["Close"]),
            "vwma100_usd": float(v.get("vwma_100", 0.0)),
        }
        _MOMENTUM_CACHE["data"] = data
        _MOMENTUM_CACHE["ts"] = now
        return data
    except Exception:
        return None


@router.get("/portfolio")
def get_portfolio() -> dict:
    """포트폴리오 현황(비중·진입가·모멘텀) JSON을 그대로 반환한다.

    mock 단계: data/research/stocks/tesla/portfolio.json 파일을 그대로 응답.
    실데이터 단계에서는 브로커 연동/실시간 지표로 교체.
    """
    try:
        path = _CSV_DIR / "portfolio.json"
        if not path.exists():
            return {"source": "missing"}
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"source": "error"}


@router.get("/headline-cards")
def get_headline_cards() -> dict:
    """Essence 상단 3카드(비중관리·현재주가·모멘텀)용 컴팩트 응답.

    실시간 데이터 우선 (yfinance 5분 캐시). 실패 시 portfolio.json fallback.
    portfolio.json은 사용자 입력 필드(shares, avg_cost, target_pct, total_portfolio_usd)만 관리.
    """
    try:
        from datetime import date as _date

        path = _CSV_DIR / "portfolio.json"
        if not path.exists():
            return {"cards": [], "as_of": "", "source": "missing"}

        pf = json.loads(path.read_text(encoding="utf-8"))
        weight = pf.get("weight", {}) or {}
        price = pf.get("price_context", {}) or {}
        momentum = pf.get("momentum", {}) or {}
        position = pf.get("position", {}) or {}

        # ── 실시간 데이터 (yfinance, 캐시 공유)
        rt = _compute_momentum_realtime()

        if rt is not None:
            current_usd = rt["current_price"]
            vwma100_usd = rt["vwma100_usd"]
            close_vs_vwma = rt["close_vs_vwma_pct"]
            rt_source = "yfinance"
        else:
            current_usd = price.get("current_usd", 0.0)
            vwma100_usd = price.get("vwma100_usd", 0.0)
            close_vs_vwma = price.get("vwma100_deviation_pct", 0.0)
            rt_source = "mock"

        # ── 사용자 포지션 (portfolio.json 입력값)
        entry_avg = position.get("avg_cost_usd") or price.get("entry_avg_usd", 0.0)
        shares = position.get("shares", 0)
        total_portfolio_usd = pf.get("total_portfolio_usd", 0.0)

        # ── 현재주가 카드
        pl_pct = round((current_usd - entry_avg) / entry_avg * 100, 2) if entry_avg else 0.0

        if close_vs_vwma >= 5:
            channel_pos = "채널 상단"
        elif close_vs_vwma <= -5:
            channel_pos = "채널 하단"
        else:
            channel_pos = "채널 중단"

        price_card = {
            "key": "price",
            "label_ko": "현재주가",
            "primary": f"${current_usd:,.2f}",
            "primary_sub": f"진입 ${entry_avg:,.2f}",
            "delta": f"{pl_pct:+.2f}%",
            "delta_pos": pl_pct >= 0,
            "action": channel_pos,
            "comment": f"VWMA100 ${vwma100_usd:,.2f} ({close_vs_vwma:+.1f}%)",
            "color": "#3fb950" if pl_pct >= 0 else "#f85149",
            "source": rt_source,
        }

        # ── 비중관리 카드 — 실시간 주가로 current_pct 재계산
        if total_portfolio_usd and current_usd and shares:
            cur_pct = round(shares * current_usd / total_portfolio_usd * 100, 1)
        else:
            cur_pct = weight.get("current_pct", 0.0)

        tgt_pct = weight.get("target_pct", 0.0)
        delta_pct = round(cur_pct - tgt_pct, 1)

        if delta_pct < -2.0:
            action_label = weight.get("action_label_ko") or "분할 매수"
            weight_comment = f"타겟 {delta_pct:+.1f}%p 미달 · 추가 여력 있음"
        elif delta_pct > 2.0:
            action_label = "비중 축소"
            weight_comment = f"타겟 {delta_pct:+.1f}%p 초과 · 부분 익절 검토"
        else:
            action_label = "유지"
            weight_comment = f"타겟 ±{abs(delta_pct):.1f}%p 내 · 적정 비중"

        weight_card = {
            "key": "weight",
            "label_ko": "비중관리",
            "primary": f"{cur_pct:.1f}%",
            "primary_sub": f"타겟 {tgt_pct:.1f}%",
            "delta": f"{delta_pct:+.1f}%p",
            "delta_pos": delta_pct >= 0,
            "action": action_label,
            "comment": weight_comment,
            "color": "#3fb950" if -2.0 <= delta_pct <= 2.0 else ("#d29922" if delta_pct < -2.0 else "#f85149"),
        }

        # ── 모멘텀 카드
        if rt is not None:
            score = rt["score"]
            alignment = rt["trend_alignment"]
            delta_3d = rt["delta_3d"]
            signal = rt["signal"]
            action_text = (
                f"매수 시그널 ({signal.get('touched_sma', '').upper()})"
                if signal.get("signal")
                else rt["chain_str"]
            )
            comment_text = rt["comment"]
            momentum_source = "yfinance"
        else:
            score = momentum.get("score", 0)
            alignment = momentum.get("trend_alignment", "")
            delta_3d = momentum.get("delta_3d", "")
            action_text = momentum.get("macd_state", "")
            comment_text = momentum.get("comment", "")
            momentum_source = "mock"

        delta_pos = not str(delta_3d).startswith("-")
        momentum_card = {
            "key": "momentum",
            "label_ko": "모멘텀",
            "primary": f"{score}",
            "primary_sub": alignment,
            "delta": f"3D {delta_3d}" if delta_3d else "",
            "delta_pos": delta_pos,
            "action": action_text,
            "comment": comment_text,
            "color": "#3fb950" if score >= 60 else ("#d29922" if score >= 40 else "#f85149"),
            "source": momentum_source,
        }

        as_of = _date.today().isoformat() if rt_source == "yfinance" else pf.get("as_of", "")

        return {
            "as_of": as_of,
            "source": rt_source,
            "regime": pf.get("regime", {}),
            "cards": [weight_card, price_card, momentum_card],
        }
    except Exception:
        return {"cards": [], "as_of": "", "source": "error"}


@router.get("/delivery-signals")
def get_delivery_signals() -> dict:
    """delivery_signals JSON 파일을 반환한다."""
    try:
        _DELIVERY_DIR = Path("data/research/stocks/tesla/delivery_signals")
        if not _DELIVERY_DIR.exists():
            return {"china": {}, "eu": {}, "latest_month": ""}

        result: dict[str, Any] = {"china": {}, "eu": {}, "latest_month": ""}
        latest = ""

        for json_file in sorted(_DELIVERY_DIR.glob("*.json")):
            try:
                content = json.loads(json_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                continue

            # 파일명에서 월 추출 (예: china_2026-04.json → 2026-04)
            stem = json_file.stem
            parts = stem.rsplit("_", 1)
            month_key = parts[-1] if len(parts) == 2 and "-" in parts[-1] else stem

            # 중국/유럽 분기
            if "china" in stem.lower():
                result["china"][month_key] = content
            elif "eu" in stem.lower() or "europe" in stem.lower():
                result["eu"][month_key] = content
            else:
                # 범용: content에 region 힌트가 있으면 사용
                result["china" if "china" in str(content).lower() else "eu"][month_key] = content

            if month_key > latest:
                latest = month_key

        result["latest_month"] = latest
        return result
    except Exception:
        return {"china": {}, "eu": {}, "latest_month": ""}
