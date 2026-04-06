#!/usr/bin/env python3
"""심층 뉴스 분석 — 하루 2회 (브리핑 전) Ollama 로컬 LLM으로 실행.

12시간치 뉴스를 이슈별로 묶어서:
  1. 이벤트 생성 (무슨 일이 벌어지고 있는가)
  2. 엔티티 피드백 (잘못된 엔티티 교정/삭제 제안)

cron:
    30 20 * * * cd ~/stock && python3 scripts/deep_analysis.py >> logs/deep_analysis.log 2>&1
    30 8 * * *  cd ~/stock && python3 scripts/deep_analysis.py >> logs/deep_analysis.log 2>&1

수동:
    python3 scripts/deep_analysis.py
    python3 scripts/deep_analysis.py --dry-run
    python3 scripts/deep_analysis.py --hours 6
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests as http_requests

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# ── Ollama 설정 ──────────────────────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"
OLLAMA_TIMEOUT = 180  # 심층분석은 길어질 수 있음


# ── 프롬프트 ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior investment analyst. Your job is to read raw news headlines grouped by topic (issue), then produce:

1. **Events**: What is actually happening? Merge multiple headlines into coherent events. Each event should answer "what happened, why it matters, and what to watch next."
2. **Entity feedback**: Flag any entity names in the provided entity list that are clearly wrong (domains like cnn.com, noise words, duplicates, wrong types).

Be concise but insightful. Focus on investment implications."""

ANALYSIS_PROMPT = """## Issue: {issue_title} ({category})

### Recent news (last {hours}h):
{news_block}

### Current entities for this issue:
{entity_block}

---

Analyze and respond with ONLY valid JSON (no markdown):
{{
  "events": [
    {{
      "title": "이벤트 제목 (한국어, 20자 이내)",
      "summary": "무슨 일이 벌어지고 있는가 + 왜 중요한가 + 다음에 볼 것 (한국어, 2~3문장)",
      "event_type": "war|policy|earnings|product|regulation|macro|deal|military",
      "severity": "critical|major|moderate|minor",
      "article_count": <int, how many articles this event covers>
    }}
  ],
  "entity_feedback": {{
    "delete": ["entity names that are noise/domains/wrong"],
    "retype": [{{"name": "...", "correct_type": "company|person|asset|institution|sector|country|commodity|proxy"}}]
  }}
}}

Rules:
- Create 1~5 events per issue (only if there's real news)
- If no meaningful news, return empty events array
- Merge similar headlines into one event
- Entity feedback: only flag obvious errors, don't over-correct
- All text in Korean"""


# ── 유틸 ─────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _parse_json(text: str) -> dict[str, Any]:
    """LLM 응답에서 JSON 파싱."""
    if not text:
        return {}
    if "```" in text:
        start = text.find("```")
        nl = text.find("\n", start)
        end = text.find("```", nl)
        if end > nl:
            text = text[nl:end].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for i in range(len(text), 0, -1):
            try:
                return json.loads(text[:i])
            except json.JSONDecodeError:
                continue
        return {}


# ── 데이터 수집 ──────────────────────────────────────────────────────────────

def get_recent_news(issue_title: str, keywords: list[str], hours: int) -> list[dict]:
    """이슈 키워드로 최근 N시간 뉴스를 가져온다."""
    from sqlalchemy import or_, select

    from src.core.database import NewsItemDB, get_session

    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    with get_session() as session:
        conditions = [NewsItemDB.title.ilike(f"%{kw}%") for kw in keywords]
        stmt = (
            select(NewsItemDB)
            .where(or_(*conditions))
            .where(NewsItemDB.created_at >= since)
            .order_by(NewsItemDB.created_at.desc())
            .limit(50)
        )
        rows = session.execute(stmt).scalars().all()

        # 제목 기준 중복 제거
        seen_titles: set[str] = set()
        unique = []
        for r in rows:
            normalized = re.sub(r"\s+", " ", r.title.lower().strip())
            if normalized not in seen_titles:
                seen_titles.add(normalized)
                unique.append({
                    "title": r.title,
                    "source": r.source,
                    "published_at": str(r.published_at or r.created_at),
                })

        return unique


def get_issue_entities(issue_id: str) -> list[dict]:
    """이슈에 연결된 엔티티 목록."""
    from src.storage import GeoIssueRepository, OntologyEntityRepository

    issue_repo = GeoIssueRepository()
    e_repo = OntologyEntityRepository()

    issue = issue_repo.get_by_id(issue_id)
    if not issue or not issue.entity_ids:
        return []

    entities = []
    for eid in issue.entity_ids[:50]:  # 최대 50개
        e = e_repo.get_by_id(eid)
        if e:
            entities.append({"name": e.name, "type": e.entity_type})

    return entities


# ── Ollama 호출 ──────────────────────────────────────────────────────────────

def _call_ollama(prompt: str) -> str | None:
    """Ollama API 호출."""
    try:
        resp = http_requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as e:
        print(f"    Ollama 호출 실패: {e}")
        return None


# ── 분석 실행 ────────────────────────────────────────────────────────────────

def analyze_issue(
    issue: Any,
    keywords: list[str],
    hours: int,
) -> dict[str, Any] | None:
    """이슈 하나에 대해 Ollama 심층분석 실행."""
    news = get_recent_news(issue.title, keywords, hours)
    if not news:
        return None

    entities = get_issue_entities(issue.id)

    news_block = "\n".join(
        f"- [{n['source']}] {n['title']}" for n in news[:20]
    )
    entity_block = ", ".join(
        f"{e['name']}({e['type']})" for e in entities[:20]
    ) or "(없음)"

    prompt = SYSTEM_PROMPT + "\n\n" + ANALYSIS_PROMPT.format(
        issue_title=issue.title,
        category=getattr(issue, "category", ""),
        hours=hours,
        news_block=news_block,
        entity_block=entity_block,
    )

    raw = _call_ollama(prompt)
    if not raw:
        return None

    result = _parse_json(raw)
    result["_meta"] = {
        "news_count": len(news),
        "entity_count": len(entities),
    }
    return result


# ── 저장 ─────────────────────────────────────────────────────────────────────

def save_events(issue: Any, events_data: list[dict]) -> int:
    """분석 결과에서 이벤트를 생성하고 이슈에 연결한다."""
    from src.core.models import OntologyEvent
    from src.storage import GeoIssueRepository, OntologyEventRepository

    event_repo = OntologyEventRepository()
    issue_repo = GeoIssueRepository()

    valid_event_types = {"war", "policy", "earnings", "product", "regulation", "macro", "deal", "military"}
    valid_severities = {"critical", "major", "moderate", "minor"}

    new_event_ids = []
    for ev_data in events_data:
        title = ev_data.get("title", "")
        if not title:
            continue

        event_type = ev_data.get("event_type", "macro")
        if event_type not in valid_event_types:
            event_type = "macro"

        severity = ev_data.get("severity", "moderate")
        if severity not in valid_severities:
            severity = "moderate"

        # market: stock_kr→korea, stock_us→us, geo→us
        cat = getattr(issue, "category", "geo")
        market = "korea" if "kr" in cat else "us"

        event = OntologyEvent(
            title=title,
            summary=ev_data.get("summary", ""),
            event_type=event_type,
            severity=severity,
            market=market,
            article_count=ev_data.get("article_count", 1),
        )

        event_repo.create(event)
        new_event_ids.append(event.id)

    # 이슈에 이벤트 연결
    if new_event_ids:
        existing = list(issue.event_ids or [])
        merged = existing + new_event_ids
        issue_repo.update(issue.id, event_ids=merged)

    return len(new_event_ids)


def apply_entity_feedback(issue: Any, feedback: dict) -> dict[str, int]:
    """엔티티 피드백 적용 — 삭제 + 타입 교정."""
    from src.storage import OntologyEntityRepository, OntologyLinkRepository

    e_repo = OntologyEntityRepository()
    l_repo = OntologyLinkRepository()
    stats = {"deleted": 0, "retyped": 0}

    # 삭제
    for name in feedback.get("delete", []):
        entity = e_repo.find_by_name(name)
        if entity:
            # 관계 먼저 삭제
            for lk in l_repo.get_many(filters={"source_id": entity.id}, limit=200):
                l_repo.delete(lk.id)
            for lk in l_repo.get_many(filters={"target_id": entity.id}, limit=200):
                l_repo.delete(lk.id)
            e_repo.delete(entity.id)
            stats["deleted"] += 1

    # 타입 교정
    from src.core.models import EntityType
    valid_types = {e.value for e in EntityType}
    for retype in feedback.get("retype", []):
        name = retype.get("name", "")
        new_type = retype.get("correct_type", "")
        if not name or new_type not in valid_types:
            continue
        entity = e_repo.find_by_name(name)
        if entity and entity.entity_type != new_type:
            e_repo.update(entity.id, entity_type=new_type)
            stats["retyped"] += 1

    return stats


# ── 키워드 통합 ──────────────────────────────────────────────────────────────

def get_all_keywords() -> dict[str, list[str]]:
    """geo + stock 이슈 키워드 통합."""
    from scripts.update_geoinvest import ISSUE_KEYWORDS as GEO_KW

    try:
        from scripts.seed_stock_issues import STOCK_KEYWORDS as STOCK_KW
    except ImportError:
        STOCK_KW = {}

    merged = {}
    merged.update(GEO_KW)
    merged.update(STOCK_KW)
    return merged


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="심층 뉴스 분석 (Claude Sonnet)")
    parser.add_argument("--dry-run", action="store_true", help="분석만 하고 DB 저장 안 함")
    parser.add_argument("--hours", type=int, default=12, help="분석할 뉴스 기간 (기본 12시간)")
    parser.add_argument("--issue", type=str, default=None, help="특정 이슈만 분석")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"심층 뉴스 분석 — {_now()} (Ollama {OLLAMA_MODEL})")
    print(f"범위: 최근 {args.hours}시간 | {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*60}")

    # 초기화
    from src.core.database import init_db
    init_db()

    # Ollama 접속 확인
    try:
        r = http_requests.get("http://localhost:11434/api/tags", timeout=3)
        r.raise_for_status()
    except Exception:
        print("  ✗ Ollama 미실행 — ollama serve 필요")
        sys.exit(1)

    from src.storage import GeoIssueRepository
    issue_repo = GeoIssueRepository()
    all_issues = issue_repo.get_active()
    all_keywords = get_all_keywords()

    if args.issue:
        all_issues = [i for i in all_issues if i.title == args.issue]

    total_events = 0
    total_deleted = 0
    total_retyped = 0

    for issue in all_issues:
        keywords = all_keywords.get(issue.title, [])
        if not keywords:
            continue

        result = analyze_issue(issue, keywords, args.hours)
        if not result:
            print(f"\n  {issue.title}: 뉴스 없음 — 스킵")
            continue

        meta = result.get("_meta", {})
        events = result.get("events", [])
        feedback = result.get("entity_feedback", {})

        print(f"\n  {issue.title} ({getattr(issue, 'category', '')})")
        print(f"    뉴스: {meta.get('news_count', 0)}건 → 이벤트: {len(events)}개")

        for ev in events:
            sev = ev.get("severity", "?")
            print(f"    📌 [{sev:8s}] {ev.get('title', '?')}")
            summary = ev.get("summary", "")
            if summary:
                print(f"       {summary[:80]}...")

        if feedback.get("delete"):
            print(f"    🗑️  삭제 제안: {feedback['delete'][:5]}")
        if feedback.get("retype"):
            print(f"    🔄 타입 교정: {[r['name'] for r in feedback['retype'][:5]]}")

        if not args.dry_run:
            # 이벤트 저장
            n_events = save_events(issue, events)
            total_events += n_events

            # 엔티티 피드백 적용
            if feedback:
                stats = apply_entity_feedback(issue, feedback)
                total_deleted += stats["deleted"]
                total_retyped += stats["retyped"]

    # 요약
    print(f"\n{'='*60}")
    print(f"완료 — {_now()}")
    print(f"  이벤트: {total_events}개 생성")
    print(f"  엔티티: {total_deleted}개 삭제, {total_retyped}개 타입 교정")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
