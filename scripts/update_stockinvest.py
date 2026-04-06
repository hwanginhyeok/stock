#!/usr/bin/env python3
"""StockInvest 자동 업데이트 — 주식 뉴스 → Ollama 엔티티/관계 추출 → DB 저장.

cron으로 매 정각 실행:
    0 * * * * cd ~/stock && python3 scripts/update_stockinvest.py >> logs/stockinvest_update.log 2>&1

수동 실행:
    python3 scripts/update_stockinvest.py
    python3 scripts/update_stockinvest.py --category stock_us
    python3 scripts/update_stockinvest.py --category stock_kr
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests as http_requests

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# ── Ollama 설정 ──────────────────────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"
OLLAMA_TIMEOUT = 120

# 엔티티 노이즈 필터 — 도메인, 무의미 단어, 숫자만 있�� 값
_DOMAIN_RE = re.compile(
    r"^[\w.-]+\.(com|org|net|io|gov|edu|co\.kr|co\.jp|co\.uk|info|biz|me|ai|kr|jp|az)$",
    re.IGNORECASE,
)
_NOISE_NAMES = {
    "metadata", "capabilities", "endpoints", "operational details",
    "war", "conflict", "news", "report", "article", "source",
    "the post", "the report",
}

def _is_noise_entity(name: str) -> bool:
    """도메인, 숫자, 노이즈 단���를 걸러낸다."""
    if not name or len(name) < 2:
        return True
    if _DOMAIN_RE.match(name):
        return True
    if name.lower().strip() in _NOISE_NAMES:
        return True
    cleaned = re.sub(r"[\d$€₩¥%,.~\-–—주년월일개건조억만천]", "", name).strip()
    if not cleaned:
        return True
    return False

EXTRACTION_PROMPT = """You are a financial analyst. Extract entities and relationships from these news articles about '{issue}'.

{articles}

Entity types: company, person, asset, institution, sector, country, commodity
Relationship types: competitor, supplier, investor, regulator, partner, impacts, mentions, triggers, reacts_to

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "entities": [
    {{"name": "...", "entity_type": "company|person|asset|institution|sector|country|commodity"}}
  ],
  "relationships": [
    {{"source": "...", "target": "...", "relation_type": "competitor|supplier|investor|regulator|partner|impacts|mentions|triggers|reacts_to", "evidence": "one sentence"}}
  ]
}}"""

# ���─ 키워드 임포트 ────────────────────────────────────────────────────────────
from scripts.seed_stock_issues import STOCK_KEYWORDS


# ── 뉴스 조회 ────────────────────────────────────────────────────────────────

def find_relevant_news(issue_name: str) -> list[dict]:
    """이슈별 키워드로 최근 뉴스를 필터링한다."""
    from sqlalchemy import or_, select

    from src.core.database import NewsItemDB, get_session

    keywords = STOCK_KEYWORDS.get(issue_name, [])
    if not keywords:
        return []

    with get_session() as session:
        conditions = [NewsItemDB.title.ilike(f"%{kw}%") for kw in keywords]
        stmt = (
            select(NewsItemDB)
            .where(or_(*conditions))
            .order_by(NewsItemDB.created_at.desc())
            .limit(20)
        )
        rows = session.execute(stmt).scalars().all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "content": r.content or "",
                "summary": r.summary or "",
                "source": r.source,
                "published_at": str(r.published_at or r.created_at),
            }
            for r in rows
        ]


# ── Ollama 추출 ──────────────────────────────────────────────────────────────

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


def _parse_json(text: str) -> dict[str, Any]:
    """LLM 응답에서 JSON 파싱."""
    if not text:
        return {}
    if "```" in text:
        start = text.find("```")
        first_newline = text.find("\n", start)
        end = text.find("```", first_newline)
        if end > first_newline:
            text = text[first_newline:end].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for i in range(len(text), 0, -1):
            try:
                return json.loads(text[:i])
            except json.JSONDecodeError:
                continue
        return {}


def extract_entities(issue_name: str, news: list[dict]) -> dict[str, Any]:
    """Ollama로 뉴스에서 엔티티/관계를 추출한다."""
    articles_text = "\n---\n".join(
        f"Title: {item['title']}\nDate: {item['published_at']}"
        + (f"\nSummary: {item['summary'][:200]}" if item.get("summary") else "")
        + (f"\nContent: {item['content'][:300]}" if item.get("content") else "")
        for item in news[:10]
    )

    prompt = EXTRACTION_PROMPT.format(issue=issue_name, articles=articles_text)
    raw = _call_ollama(prompt)
    if not raw:
        return {}
    return _parse_json(raw)


# ── DB 저장 ──────────────────────────────────────────────────────────────────

def _save_extraction(
    entities: list[dict],
    relationships: list[dict],
    issue_id: str,
) -> int:
    """추출 결과를 DB에 저장. 이슈에 엔티티 연결."""
    from src.core.models import EntityType, Market, OntologyEntity, OntologyLink
    from src.storage import GeoIssueRepository, OntologyEntityRepository, OntologyLinkRepository

    e_repo = OntologyEntityRepository()
    l_repo = OntologyLinkRepository()
    issue_repo = GeoIssueRepository()

    # 엔티티 저장 (노이즈 필터 적용)
    entity_id_map: dict[str, str] = {}
    new_entity_ids: list[str] = []
    valid_types = {e.value for e in EntityType}
    filtered_count = 0

    for ent_data in entities:
        name = ent_data.get("name", "")
        if not name:
            continue
        if _is_noise_entity(name):
            filtered_count += 1
            continue
        existing = e_repo.find_by_name(name)
        if existing:
            entity_id_map[name.lower()] = existing.id
            new_entity_ids.append(existing.id)
            continue

        raw_type = ent_data.get("entity_type", "company")
        if raw_type not in valid_types:
            print(f"  ⚠ entity_type '{raw_type}' → 'institution' ({name})")
            raw_type = "institution"

        entity = OntologyEntity(
            name=name,
            entity_type=raw_type,
            market=Market.US,
            aliases=ent_data.get("aliases", []),
        )
        e_repo.create(entity)
        entity_id_map[name.lower()] = entity.id
        new_entity_ids.append(entity.id)

    # 이슈에 엔티티 연결
    if new_entity_ids and issue_id:
        issue = issue_repo.get_by_id(issue_id)
        if issue:
            existing_ids = set(issue.entity_ids or [])
            added = [eid for eid in new_entity_ids if eid not in existing_ids]
            if added:
                issue_repo.update(
                    issue_id,
                    entity_ids=list(existing_ids | set(added)),
                )

    # 관계 저장
    new_links = 0
    allowed_types = {
        "competitor", "supplier", "investor", "regulator", "partner",
        "impacts", "mentions", "triggers", "reacts_to",
        "supports", "ally", "hostile", "trade", "supply", "sanctions",
    }
    for rel_data in relationships:
        src_name = rel_data.get("source", "").lower()
        tgt_name = rel_data.get("target", "").lower()
        src_id = entity_id_map.get(src_name)
        tgt_id = entity_id_map.get(tgt_name)
        if not src_id or not tgt_id or src_id == tgt_id:
            continue

        # DB enum에 맞게 매핑
        LINK_TYPE_MAP = {
            "competitor": "hostile", "supplier": "supply", "investor": "supports",
            "regulator": "impacts", "partner": "ally",
        }
        from src.core.models import LinkType
        valid_link_types = {e.value for e in LinkType}

        rel_type = rel_data.get("relation_type", "mentions")
        rel_type = LINK_TYPE_MAP.get(rel_type, rel_type)
        if rel_type not in valid_link_types:
            rel_type = "mentions"

        link = OntologyLink(
            link_type=rel_type,
            source_type="entity",
            source_id=src_id,
            target_type="entity",
            target_id=tgt_id,
            confidence=0.8,
            evidence=rel_data.get("evidence", ""),
            geo_issue_id=issue_id,
        )
        try:
            l_repo.create(link)
            new_links += 1
        except Exception:
            pass

    if filtered_count:
        print(f"    ⚡ 노이즈 필터: {filtered_count}개 엔티티 제외")

    return new_links


# ── 유틸 ─────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="StockInvest 자동 업데이트 (Ollama)")
    parser.add_argument("--category", type=str, default=None, help="stock_us 또는 stock_kr")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"StockInvest 업데이트 — {_now()} (Ollama {OLLAMA_MODEL})")
    print(f"{'='*50}")

    from src.core.database import init_db
    init_db()

    # Ollama 확인
    try:
        r = http_requests.get("http://localhost:11434/api/tags", timeout=3)
        r.raise_for_status()
    except Exception:
        print("  ✗ Ollama 미실행")
        sys.exit(1)

    # 대상 이슈 조회
    from src.storage import GeoIssueRepository
    repo = GeoIssueRepository()
    all_issues = repo.get_active()

    categories = [args.category] if args.category else ["stock_us", "stock_kr"]
    issues = [i for i in all_issues if getattr(i, "category", "") in categories]

    total_entities = 0
    total_links = 0

    for issue in issues:
        news = find_relevant_news(issue.title)
        if not news:
            print(f"\n  {issue.title}: 뉴스 없음 — 스킵")
            continue

        print(f"\n  {issue.title}: {len(news)}개 뉴스 → Ollama 추출 중...")
        result = extract_entities(issue.title, news)
        entities = result.get("entities", [])
        rels = result.get("relationships", [])
        print(f"    추출: {len(entities)}개 엔티티, {len(rels)}개 관계")

        if args.dry_run:
            print(f"    [DRY-RUN] {[e.get('name') for e in entities[:8]]}")
            continue

        if entities or rels:
            new_links = _save_extraction(entities, rels, issue.id)
            total_entities += len(entities)
            total_links += new_links
            if new_links:
                print(f"    → {new_links}개 새 관계 저장")

    print(f"\n[{_now()}] 완료 — 엔티티 {total_entities}개 처리, 새 관계 {total_links}개 저장")


if __name__ == "__main__":
    main()
