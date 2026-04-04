"""GeoInvest FastAPI 웹 서버.

Usage:
    uvicorn src.web.app:app --reload --port 8200
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.core.database import init_db
from src.storage import (
    GeoIssueRepository,
    OntologyEntityRepository,
    OntologyEventRepository,
    OntologyLinkRepository,
)

app = FastAPI(title="GeoInvest", version="0.1.0")

_STATIC_DIR = Path(__file__).parent / "static"


@app.on_event("startup")
def startup() -> None:
    """DB 초기화."""
    init_db()


@app.get("/")
def index() -> FileResponse:
    """메인 페이지."""
    return FileResponse(_STATIC_DIR / "index.html")


@app.get("/api/issues")
def list_issues(category: str = "geo") -> list[dict]:
    """활성 이슈 목록을 카테고리별로 랭킹 순 반환. category=geo|stock_us|stock_kr"""
    from src.collectors.news.classifier import ISSUE_RULES
    from src.collectors.news.issue_ranker import (
        compute_rankings, count_news_by_issue, get_previous_ranks,
        save_daily_ranking,
    )

    repo = GeoIssueRepository()
    all_active = repo.get_active()
    issues = [i for i in all_active if getattr(i, "category", "geo") == category]

    # 키워드 소스: geo는 ISSUE_RULES, stock은 STOCK_KEYWORDS
    if category == "geo":
        issue_keywords = {
            title: [kw for kw, _ in rules[:10]]
            for title, rules in ISSUE_RULES.items()
        }
    else:
        from scripts.seed_stock_issues import STOCK_KEYWORDS
        issue_keywords = STOCK_KEYWORDS

    news_counts = count_news_by_issue(issue_keywords)
    prev_ranks = get_previous_ranks()

    # 랭킹 계산
    issue_dicts = [
        {
            "id": issue.id,
            "title": issue.title,
            "severity": issue.severity,
            "event_count": len(issue.event_ids),
            "last_event_at": str(issue.created_at),
        }
        for issue in issues
    ]
    rankings = compute_rankings(issue_dicts, news_counts)
    if category == "geo":
        save_daily_ranking(rankings)

    # 랭킹 순으로 이슈 반환
    result = []
    for r in rankings:
        issue = next((i for i in issues if i.id == r.issue_id), None)
        if not issue:
            continue
        prev = prev_ranks.get(r.title)
        rank_change = (prev - r.rank) if prev else 0

        result.append({
            "id": issue.id,
            "title": issue.title,
            "description": issue.description,
            "severity": issue.severity,
            "status": issue.status,
            "category": getattr(issue, "category", "geo"),
            "analysis_type": getattr(issue, "analysis_type", ""),
            "event_count": len(issue.event_ids),
            "created_at": str(issue.created_at),
            "rank": r.rank,
            "score": r.score,
            "news_24h": r.news_24h,
            "trend": r.trend,
            "rank_change": rank_change,
        })

    # 랭킹에 안 잡힌 이슈
    ranked_ids = {r.issue_id for r in rankings}
    for issue in issues:
        if issue.id not in ranked_ids:
            result.append({
                "id": issue.id, "title": issue.title,
                "description": issue.description, "severity": issue.severity,
                "status": issue.status,
                "category": getattr(issue, "category", "geo"),
                "analysis_type": getattr(issue, "analysis_type", ""),
                "event_count": len(issue.event_ids),
                "created_at": str(issue.created_at),
                "rank": len(result) + 1, "score": 0, "news_24h": 0,
                "trend": "→", "rank_change": 0,
            })

    return result


@app.get("/api/issues/{issue_id}/graph")
def get_issue_graph(issue_id: str) -> dict:
    """GeoIssue의 관계도 그래프 데이터 (nodes + edges)를 반환한다.

    배치 쿼리로 N+1 방지: issue → events → links → entities 순.
    """
    issue_repo = GeoIssueRepository()
    issue = issue_repo.get_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue {issue_id} not found")

    event_repo = OntologyEventRepository()
    link_repo = OntologyLinkRepository()
    entity_repo = OntologyEntityRepository()

    # 1. 이슈에 속한 이벤트 조회
    events = []
    for eid in issue.event_ids:
        event = event_repo.get_by_id(eid)
        if event:
            events.append(event)

    # 2. 이슈에 속한 엔티티 ID 집합
    issue_entity_ids: set[str] = set(issue.entity_ids or [])

    # 3. 이 이슈에 태그된 링크만 가져오기 (geo_issue_id 필터)
    all_links = link_repo.get_many(
        filters={"geo_issue_id": issue_id}, limit=500,
    )

    # 이벤트에 연결된 링크도 수집
    for event in events:
        links_from = link_repo.get_many(
            filters={"source_type": "event", "source_id": event.id}, limit=200,
        )
        links_to = link_repo.get_many(
            filters={"target_type": "event", "target_id": event.id}, limit=200,
        )
        for lk in links_from + links_to:
            all_links.append(lk)

    # 4. 엔티티 배치 조회
    entities = []
    for eid in issue_entity_ids:
        entity = entity_repo.get_by_id(eid)
        if entity:
            entities.append(entity)

    # 4. nodes + edges 구성
    nodes = []
    node_ids = set()

    for entity in entities:
        nodes.append({
            "id": entity.id,
            "name": entity.name,
            "type": "entity",
            "entity_type": entity.entity_type,
            "ticker": entity.ticker,
            "aliases": entity.aliases,
        })
        node_ids.add(entity.id)

    for event in events:
        nodes.append({
            "id": event.id,
            "name": event.title,
            "type": "event",
            "event_type": event.event_type,
            "severity": event.severity,
            "status": event.status,
        })
        node_ids.add(event.id)

    # 링크 중복 제거
    seen_edges = set()
    edges = []
    for lk in all_links:
        if lk.source_id not in node_ids or lk.target_id not in node_ids:
            continue
        edge_key = (lk.source_id, lk.target_id, lk.link_type)
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)
        edges.append({
            "source": lk.source_id,
            "target": lk.target_id,
            "link_type": lk.link_type,
            "confidence": lk.confidence,
            "evidence": lk.evidence,
        })

    return {
        "issue": {
            "id": issue.id,
            "title": issue.title,
            "severity": issue.severity,
        },
        "nodes": nodes,
        "edges": edges,
    }


@app.get("/api/entities/{entity_id}/briefing")
def get_entity_briefing(entity_id: str) -> dict:
    """엔티티의 브리핑 데이터를 반환한다."""
    entity_repo = OntologyEntityRepository()
    entity = entity_repo.get_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

    link_repo = OntologyLinkRepository()

    # 이 엔티티와 연결된 모든 링크
    links_from = link_repo.get_many(
        filters={"source_type": "entity", "source_id": entity.id}, limit=100,
    )
    links_to = link_repo.get_many(
        filters={"target_type": "entity", "target_id": entity.id}, limit=100,
    )

    # 연결된 엔티티 이름 해소
    all_entity_ids = set()
    for lk in links_from + links_to:
        if lk.source_type == "entity":
            all_entity_ids.add(lk.source_id)
        if lk.target_type == "entity":
            all_entity_ids.add(lk.target_id)
    all_entity_ids.discard(entity.id)

    entity_names = {}
    for eid in all_entity_ids:
        e = entity_repo.get_by_id(eid)
        if e:
            entity_names[eid] = e.name

    # 관계 목록 구성
    relationships = []
    for lk in links_from:
        target_name = entity_names.get(lk.target_id, lk.target_id)
        relationships.append({
            "direction": "outgoing",
            "target": target_name,
            "link_type": lk.link_type,
            "confidence": lk.confidence,
            "evidence": lk.evidence,
        })
    for lk in links_to:
        source_name = entity_names.get(lk.source_id, lk.source_id)
        relationships.append({
            "direction": "incoming",
            "source": source_name,
            "link_type": lk.link_type,
            "confidence": lk.confidence,
            "evidence": lk.evidence,
        })

    return {
        "entity": {
            "id": entity.id,
            "name": entity.name,
            "entity_type": entity.entity_type,
            "ticker": entity.ticker,
            "aliases": entity.aliases,
            "properties": entity.properties,
        },
        "relationships": relationships,
    }


@app.get("/api/issues/{issue_id}/timeline")
def get_issue_timeline(issue_id: str) -> list[dict]:
    """GeoIssue의 이벤트를 시간순으로 반환한다."""
    issue_repo = GeoIssueRepository()
    issue = issue_repo.get_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue {issue_id} not found")

    event_repo = OntologyEventRepository()
    events = []
    for eid in issue.event_ids:
        event = event_repo.get_by_id(eid)
        if event:
            # 카테고리 추론 (제목 prefix)
            title = event.title
            if title.startswith("외교"):
                category = "diplomatic"
                title = title.replace("외교 | ", "")
            elif title.startswith("군사"):
                category = "military"
                title = title.replace("군사 | ", "")
            elif title.startswith("법적"):
                category = "legal"
                title = title.replace("법적 | ", "")
            else:
                category = "event"

            events.append({
                "id": event.id,
                "title": title,
                "summary": event.summary,
                "category": category,
                "severity": event.severity,
                "event_type": event.event_type,
                "started_at": str(event.started_at),
                "status": event.status,
            })

    events.sort(key=lambda e: e["started_at"], reverse=True)
    return events


import time as _time

# 번역 캐시 (제목 → 번역, 10분 TTL)
_translation_cache: dict[str, tuple[float, str]] = {}
_TRANS_CACHE_TTL = 600


def _translate_titles_ko(titles: list[str]) -> list[str]:
    """Ollama로 영어 뉴스 제목을 한국어로 일괄 번역한다. 캐시 적용."""
    import re

    import requests as _req

    now = _time.time()

    # 캐시에 있는 것과 없는 것 분리
    to_translate = []
    to_translate_idx = []
    result = list(titles)

    for i, t in enumerate(titles):
        if t in _translation_cache:
            cached_ts, cached_val = _translation_cache[t]
            if now - cached_ts < _TRANS_CACHE_TTL:
                result[i] = cached_val
                continue
        to_translate.append(t)
        to_translate_idx.append(i)

    if not to_translate:
        return result

    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(to_translate))
    prompt = f"""Translate these news headlines to Korean. Keep it concise (news headline style).
Return ONLY numbered lines, no explanation.

{numbered}"""

    try:
        resp = _req.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma3:4b", "prompt": prompt, "stream": False},
            timeout=30,
        )
        text = resp.json().get("response", "")
        lines = [ln.strip() for ln in text.strip().split("\n") if ln.strip()]
        translated = []
        for ln in lines:
            m = re.match(r"^\d+[\.\)]\s*(.+)", ln)
            translated.append(m.group(1) if m else ln)
        if len(translated) == len(to_translate):
            for idx, orig, trans in zip(to_translate_idx, to_translate, translated):
                result[idx] = trans
                _translation_cache[orig] = (now, trans)
    except Exception:
        pass
    return result


@app.get("/api/news/latest")
def get_latest_news(limit: int = 30) -> list[dict]:
    """최신 뉴스를 반환한다 (티커용). 이슈 분류 + 한국어 번역 포함."""
    from src.collectors.news.classifier import classify_news
    from src.storage import NewsRepository

    repo = NewsRepository()
    items = repo.get_latest(limit=limit)

    # 영어 제목만 모아서 일괄 번역
    en_indices = []
    en_titles = []
    for i, item in enumerate(items):
        if item.market != "kr" and any(c.isascii() and c.isalpha() for c in item.title[:20]):
            en_indices.append(i)
            en_titles.append(item.title)

    translated = _translate_titles_ko(en_titles) if en_titles else []
    title_map = dict(zip(en_indices, translated)) if translated else {}

    results = []
    for i, item in enumerate(items):
        classified = classify_news(item.title, item.content or item.summary or "")
        results.append({
            "title": title_map.get(i, item.title),
            "source": item.source,
            "market": item.market,
            "importance": item.importance,
            "published_at": str(item.published_at or item.created_at),
            "issues": classified.issues,
            "top_issue": classified.top_issue,
        })
    return results


# Static files (마지막에 마운트 — catch-all)
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
