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
def get_issue_graph(issue_id: str, top: int = 0, depth: int = 2) -> dict:
    # C2: 입력 검증
    top = max(0, min(top, 200))
    depth = max(1, min(depth, 3))
    """GeoIssue의 관계도 그래프 데이터 (nodes + edges)를 반환한다.

    Args:
        top: 0이면 전체, N이면 관계 수(degree) 상위 N개 엔티티만 반환.
        depth: 관계 깊이 (1=직접 연결만, 2=2차까지, 3=3차까지). 기본 2.

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

    # 3. 이 이슈에 태그된 링크만 가져오기 (geo_issue_id 필터) + 중복 제거
    seen_link_ids: set[str] = set()
    all_links = []
    for lk in link_repo.get_many(filters={"geo_issue_id": issue_id}, limit=500):
        if lk.id not in seen_link_ids:
            seen_link_ids.add(lk.id)
            all_links.append(lk)

    # 이벤트에 연결된 링크도 수집 (중복 제거)
    for event in events:
        links_from = link_repo.get_many(
            filters={"source_type": "event", "source_id": event.id}, limit=200,
        )
        links_to = link_repo.get_many(
            filters={"target_type": "event", "target_id": event.id}, limit=200,
        )
        for lk in links_from + links_to:
            if lk.id not in seen_link_ids:
                seen_link_ids.add(lk.id)
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

    # Top N 필터: degree 기준 상위 엔티티만 남기기
    if top > 0:
        from collections import Counter
        degree: Counter[str] = Counter()
        for lk in all_links:
            degree[lk.source_id] += 1
            degree[lk.target_id] += 1
        # 엔티티만 필터 (이벤트는 유지)
        entity_ids_ranked = [
            eid for eid, _ in degree.most_common()
            if eid in issue_entity_ids
        ][:top]
        top_set = set(entity_ids_ranked)
        # 엔티티 노드 필터
        nodes = [n for n in nodes if n["type"] == "event" or n["id"] in top_set]
        node_ids = {n["id"] for n in nodes}

    # depth 기반 필터: entity→entity 직접 링크에서 BFS로 깊이 제한
    if depth > 0 and depth < 10:
        from collections import Counter, defaultdict, deque

        # entity→entity 인접 그래프 구축
        adj: dict[str, set[str]] = defaultdict(set)
        for lk in all_links:
            if lk.source_type == "entity" and lk.target_type == "entity":
                adj[lk.source_id].add(lk.target_id)
                adj[lk.target_id].add(lk.source_id)

        # 이벤트와 직접 연결된 엔티티를 시드(depth=1)로 사용
        event_ids = {e.id for e in events}
        seed_entity_ids: set[str] = set()
        for lk in all_links:
            if lk.source_id in event_ids and lk.target_type == "entity":
                seed_entity_ids.add(lk.target_id)
            if lk.target_id in event_ids and lk.source_type == "entity":
                seed_entity_ids.add(lk.source_id)
        if not seed_entity_ids:
            seed_entity_ids = issue_entity_ids  # 시드 없으면 전체 사용

        # BFS로 depth 이내 엔티티만 남기기
        reachable: set[str] = set()
        queue: deque[tuple[str, int]] = deque(
            (eid, 1) for eid in seed_entity_ids if eid in node_ids
        )
        while queue:
            eid, d = queue.popleft()
            if eid in reachable:
                continue
            reachable.add(eid)
            if d < depth:
                for neighbor in adj.get(eid, []):
                    if neighbor not in reachable and neighbor in node_ids:
                        queue.append((neighbor, d + 1))

        # 이벤트는 유지, 엔티티는 reachable만
        nodes = [n for n in nodes if n["type"] == "event" or n["id"] in reachable]
        node_ids = {n["id"] for n in nodes}

    # degree 하위 30% pruning (노드가 10개 이상일 때만)
    if len([n for n in nodes if n["type"] == "entity"]) > 10:
        from collections import Counter
        degree_count: Counter[str] = Counter()
        for lk in all_links:
            if lk.source_id in node_ids and lk.target_id in node_ids:
                degree_count[lk.source_id] += 1
                degree_count[lk.target_id] += 1
        entity_nodes = [n for n in nodes if n["type"] == "entity"]
        if entity_nodes:
            degrees = sorted(degree_count.get(n["id"], 0) for n in entity_nodes)
            cutoff = degrees[max(0, len(degrees) * 30 // 100)]  # 하위 30% 경계
            prune_ids = {
                n["id"] for n in entity_nodes
                if degree_count.get(n["id"], 0) <= cutoff
                and n["id"] not in (seed_entity_ids if depth > 0 else set())
            }
            nodes = [n for n in nodes if n["id"] not in prune_ids]
            node_ids = {n["id"] for n in nodes}

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
        "total_entities": len(issue_entity_ids),
        "filtered": len([n for n in nodes if n["type"] == "entity"]),
        "depth": depth,
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

    # 관계 목록 구성 — 중요도 소팅 + 그룹핑
    LINK_LABELS = {
        "hostile": "적대", "ally": "동맹", "sanctions": "제재",
        "trade": "무역", "supply": "보급", "proxy": "대리전",
        "attack": "공격", "blockade": "봉쇄", "base": "기지",
        "supports": "지원", "impacts": "영향", "involves": "관련",
        "reacts_to": "반응", "triggers": "촉발", "mentions": "언급",
    }
    # 상대 엔티티별 관계 집계
    from collections import defaultdict
    rel_summary: dict[str, dict] = {}  # name → {types: [...], count, max_confidence}
    for lk in links_from + links_to:
        if lk.source_type != "entity" or lk.target_type != "entity":
            continue
        other_id = lk.target_id if lk.source_id == entity.id else lk.source_id
        other_name = entity_names.get(other_id)
        if not other_name:
            continue
        if other_name not in rel_summary:
            rel_summary[other_name] = {"types": [], "count": 0, "max_conf": 0.0}
        rel_summary[other_name]["types"].append(lk.link_type)
        rel_summary[other_name]["count"] += 1
        rel_summary[other_name]["max_conf"] = max(
            rel_summary[other_name]["max_conf"], lk.confidence,
        )

    # 중요도 순 정렬 (빈도 * 신뢰도)
    sorted_rels = sorted(
        rel_summary.items(),
        key=lambda x: x[1]["count"] * x[1]["max_conf"],
        reverse=True,
    )

    relationships = []
    for name, info in sorted_rels[:20]:  # 상위 20개만
        # 관계 타입별 카운트
        from collections import Counter
        type_counts = Counter(info["types"])
        type_labels = [
            {"type": t, "label": LINK_LABELS.get(t, t), "count": c}
            for t, c in type_counts.most_common(3)
        ]
        relationships.append({
            "name": name,
            "types": type_labels,
            "total_count": info["count"],
            "confidence": round(info["max_conf"], 2),
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
def get_issue_timeline(issue_id: str) -> dict:
    """GeoIssue의 이벤트를 story_thread별로 그룹핑하여 반환한다."""
    issue_repo = GeoIssueRepository()
    issue = issue_repo.get_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue {issue_id} not found")

    event_repo = OntologyEventRepository()
    events = []
    for eid in issue.event_ids:
        event = event_repo.get_by_id(eid)
        if event:
            events.append({
                "id": event.id,
                "title": event.title,
                "summary": event.summary,
                "category": event.event_type,
                "severity": event.severity,
                "event_type": event.event_type,
                "started_at": str(event.started_at),
                "status": event.status,
                "story_thread": getattr(event, "story_thread", "") or "",
            })

    events.sort(key=lambda e: e["started_at"], reverse=True)

    # story_thread별 그룹핑
    threads: dict[str, list] = {}
    ungrouped = []
    for ev in events:
        thread = ev["story_thread"]
        if thread:
            threads.setdefault(thread, []).append(ev)
        else:
            ungrouped.append(ev)

    return {
        "events": events,
        "threads": threads,
        "ungrouped": ungrouped,
        "total": len(events),
    }


@app.get("/api/events/{event_id}/detail")
def get_event_detail(event_id: str) -> dict:
    """이벤트 상세 + 관련 뉴스를 반환한다 (타임라인 클릭 시)."""
    event_repo = OntologyEventRepository()
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    link_repo = OntologyLinkRepository()
    entity_repo = OntologyEntityRepository()

    # 이벤트에 연결된 뉴스 (1차: ontology_links, 2차: 키워드 검색)
    from src.storage import NewsRepository
    news_repo = NewsRepository()
    news_items = []

    # 1차: ontology_links news→event
    news_links = link_repo.get_many(
        filters={"target_type": "event", "target_id": event_id, "link_type": "triggers"},
        limit=20,
    )
    for lk in news_links:
        if lk.source_type == "news":
            item = news_repo.get_by_id(lk.source_id)
            if item:
                news_items.append({
                    "title": item.title,
                    "source": item.source,
                    "published_at": str(item.published_at or item.created_at),
                    "summary": (item.summary or "")[:200],
                })

    # 2차: 링크 없으면 이벤트 제목 키워드로 뉴스 검색
    if not news_items and event.title:
        from sqlalchemy import or_, select
        from src.core.database import NewsItemDB, get_session
        # 제목에서 핵심 키워드 추출 (2글자 이상 단어)
        import re
        words = [w for w in re.split(r"[\s,·—\-]+", event.title) if len(w) >= 2][:3]
        if words:
            with get_session() as session:
                conditions = [NewsItemDB.title.ilike(f"%{w}%") for w in words]
                stmt = (
                    select(NewsItemDB)
                    .where(or_(*conditions))
                    .order_by(NewsItemDB.published_at.desc())
                    .limit(5)
                )
                rows = session.execute(stmt).scalars().all()
                for r in rows:
                    news_items.append({
                        "title": r.title,
                        "source": r.source,
                        "published_at": str(r.published_at or r.created_at),
                        "summary": (r.summary or "")[:200],
                    })

    # 이벤트에 연결된 엔티티 (ontology_links: event→entity involves)
    entity_links = link_repo.get_many(
        filters={"source_type": "event", "source_id": event_id},
        limit=30,
    )
    related_entities = []
    for lk in entity_links:
        if lk.target_type == "entity":
            ent = entity_repo.get_by_id(lk.target_id)
            if ent:
                related_entities.append({
                    "name": ent.name,
                    "entity_type": ent.entity_type,
                    "link_type": lk.link_type,
                })

    return {
        "event": {
            "id": event.id,
            "title": event.title,
            "summary": event.summary,
            "event_type": event.event_type,
            "severity": event.severity,
            "started_at": str(event.started_at),
            "status": event.status,
            "story_thread": getattr(event, "story_thread", "") or "",
        },
        "news": news_items,
        "entities": related_entities,
    }


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
def get_latest_news(per_category: int = 2) -> list[dict]:
    """카테고리별 핫뉴스를 반환한다 (티커용).

    GEO/US/KR 각 카테고리에서 importance 높은 순 + 최신순으로 선별.
    """
    from src.collectors.news.classifier import classify_news
    from src.storage import NewsRepository

    repo = NewsRepository()
    # published_at 기준 최신 뉴스 (get_timeline은 published_at 정렬)
    candidates = repo.get_timeline(hours=24, limit=200)

    # 이슈 분류 후 카테고리별 그룹핑
    geo_keywords = {"전쟁", "지정학", "관세", "제재", "외교", "군사", "해협"}
    categorized: dict[str, list] = {"geo": [], "stock_us": [], "stock_kr": []}
    processed = 0
    for item in candidates:
        classified = classify_news(item.title, item.content or item.summary or "")
        processed += 1

        # 기본 분류: korea → stock_kr, 그 외 → stock_us
        cat = "stock_kr" if item.market == "korea" else "stock_us"
        # geo 이슈 키워드가 있으면 geo로 오버라이드
        if classified.top_issue and any(kw in classified.top_issue for kw in geo_keywords):
            cat = "geo"

        entry = {
            "title": item.title,
            "source": item.source,
            "market": item.market,
            "importance": item.importance,
            "published_at": str(item.published_at or item.created_at),
            "issues": classified.issues,
            "top_issue": classified.top_issue,
            "category": cat,
        }
        if len(categorized.get(cat, [])) < per_category:
            categorized.setdefault(cat, []).append(entry)

        # 모든 카테고리가 per_category개씩 찼으면 조기 종료
        if all(len(v) >= per_category for v in categorized.values()):
            break
        # 성능 보호: 최대 50개만 처리
        if processed >= 50:
            break

    # 영어 제목 번역
    results = []
    for cat in ["geo", "stock_us", "stock_kr"]:
        results.extend(categorized.get(cat, []))

    en_items = [(i, r["title"]) for i, r in enumerate(results)
                if r["market"] != "kr" and any(c.isascii() and c.isalpha() for c in r["title"][:20])]
    if en_items:
        translated = _translate_titles_ko([t for _, t in en_items])
        if translated:
            for (idx, _), tr in zip(en_items, translated):
                results[idx]["title"] = tr

    return results


# Static files (마지막에 마운트 — catch-all)
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
