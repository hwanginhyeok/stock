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
def list_issues() -> list[dict]:
    """활성 GeoIssue 목록을 랭킹 순으로 반환한다."""
    from src.collectors.news.classifier import ISSUE_RULES
    from src.collectors.news.issue_ranker import (
        compute_rankings, count_news_by_issue, get_previous_ranks,
        save_daily_ranking,
    )

    repo = GeoIssueRepository()
    issues = repo.get_active()

    # 이슈별 키워드로 뉴스 카운트
    issue_keywords = {
        title: [kw for kw, _ in rules[:10]]
        for title, rules in ISSUE_RULES.items()
    }
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
    save_daily_ranking(rankings)

    # 랭킹 순으로 이슈 반환
    rank_map = {r.issue_id: r for r in rankings}
    result = []
    for r in rankings:
        issue = next((i for i in issues if i.id == r.issue_id), None)
        if not issue:
            continue
        prev = prev_ranks.get(r.title)
        rank_change = (prev - r.rank) if prev else 0  # 양수 = 상승

        result.append({
            "id": issue.id,
            "title": issue.title,
            "description": issue.description,
            "severity": issue.severity,
            "status": issue.status,
            "event_count": len(issue.event_ids),
            "created_at": str(issue.created_at),
            "rank": r.rank,
            "score": r.score,
            "news_24h": r.news_24h,
            "trend": r.trend,
            "rank_change": rank_change,
        })

    # 랭킹에 안 잡힌 이슈 (키워드 미등록)
    ranked_ids = {r.issue_id for r in rankings}
    for issue in issues:
        if issue.id not in ranked_ids:
            result.append({
                "id": issue.id, "title": issue.title,
                "description": issue.description, "severity": issue.severity,
                "status": issue.status, "event_count": len(issue.event_ids),
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


@app.get("/api/news/latest")
def get_latest_news(limit: int = 30) -> list[dict]:
    """최신 뉴스를 반환한다 (티커용). 이슈 분류 포함."""
    from src.collectors.news.classifier import classify_news
    from src.storage import NewsRepository

    repo = NewsRepository()
    items = repo.get_latest(limit=limit)
    results = []
    for item in items:
        classified = classify_news(item.title, item.content or item.summary or "")
        results.append({
            "title": item.title,
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
