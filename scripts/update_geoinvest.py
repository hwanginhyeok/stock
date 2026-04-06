#!/usr/bin/env python3
"""GeoInvest 자동 업데이트 — 뉴스 수집 → Ollama 로컬 LLM 추출 → DB 저장.

cron으로 10분마다 실행:
    */10 * * * * cd ~/stock && python3 scripts/update_geoinvest.py --skip-collect >> logs/geoinvest_update.log 2>&1

수동 실행:
    python3 scripts/update_geoinvest.py
    python3 scripts/update_geoinvest.py --skip-collect   # 뉴스 수집 건너뛰기
    python3 scripts/update_geoinvest.py --dry-run        # 추출만 하고 DB 저장 안 함
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
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
OLLAMA_TIMEOUT = 120  # 초 (RTX 2060 6GB 기준)

# 엔티티 노이즈 필터 — 도메인, 무의미 단어, 숫자만 있는 값
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
    """도메인, 숫자, 노이즈 단어를 걸러낸다."""
    if not name or len(name) < 2:
        return True
    if _DOMAIN_RE.match(name):
        return True
    if name.lower().strip() in _NOISE_NAMES:
        return True
    # 숫자/통화만으로 구성 ($71,500, 140주년, 2월 등)
    cleaned = re.sub(r"[\d$€₩¥%,.~\-–—주년월일개건조억만천]", "", name).strip()
    if not cleaned:
        return True
    return False

EXTRACTION_PROMPT = """You are a geopolitical analyst. Extract entities and relationships from these news articles about '{issue}'.

{articles}

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "entities": [
    {{"name": "...", "entity_type": "country|person|institution|asset|company|proxy|commodity"}}
  ],
  "relationships": [
    {{"source": "...", "target": "...", "relation_type": "mentions|triggers|involves|impacts|reacts_to|supports|ally|hostile|proxy|trade|supply|sanctions", "evidence": "one sentence"}}
  ]
}}"""

# ── 이슈별 키워드 ────────────────────────────────────────────────────────────
ISSUE_KEYWORDS = {
    "이란 전쟁": [
        "iran", "이란", "호르무즈", "hormuz", "hezbollah", "헤즈볼라",
        "후티", "houthi", "중동", "middle east", "이스라엘 전쟁",
    ],
    "비트코인 지정학": [
        "bitcoin", "비트코인", "crypto", "크립토", "가상자산", "stablecoin",
        "스테이블코인", "SEC crypto", "ETF 비트코인", "CBDC", "디지털화폐",
        "USDT", "USDC", "tether", "테더",
    ],
    "IMEC 회랑": [
        "IMEC", "인도 중동 유럽", "경제 회랑", "일대일로", "belt and road",
        "BRI", "하이파", "피레우스", "suez", "수에즈",
    ],
    "트럼프 관세전쟁 2.0": [
        "tariff", "관세", "trade war", "무역전쟁", "301조", "section 301",
        "상호관세", "reciprocal", "USTR", "무역대표", "관세 위헌",
        "section 122", "무역 협정",
    ],
    "AI/반도체 패권전쟁": [
        "AI chip", "AI칩", "export control", "수출통제", "nvidia",
        "엔비디아", "TSMC", "huawei", "화웨이", "ASML",
        "반도체 제재", "chips act", "칩스법", "H100", "H200",
        "ascend", "CoWoS", "HBM",
    ],
    "러시아-우크라이나 전쟁": [
        "russia", "러시아", "ukraine", "우크라이나", "nato", "나토",
        "zelensky", "젤렌스키", "putin", "푸틴", "crimea", "크림",
        "donbas", "돈바스",
    ],
    "대만 해협 위기": [
        "taiwan strait", "대만 해협", "taiwan china", "대만 중국",
        "cross-strait", "양안", "PLA taiwan", "대만 군사",
    ],
    "유럽 정치 위기": [
        "france politics", "프랑스 정치", "germany coalition", "독일 연립",
        "le pen", "르펜", "macron", "마크롱", "scholz", "숄츠",
        "EU crisis", "유럽 위기", "populism europe",
    ],
    "글로벌 AI 규제 경쟁": [
        "AI regulation", "AI 규제", "EU AI Act", "AI법",
        "openai regulation", "AI safety", "AI 안전",
        "deepfake law", "AI governance",
    ],
    "일본 금리 전환 (BOJ)": [
        "BOJ", "bank of japan", "일본은행", "일본 금리",
        "yen carry", "엔 캐리", "japanese yen", "엔화",
        "japan rate", "ueda", "우에다",
    ],
}


# ── 뉴스 수집 ────────────────────────────────────────────────────────────────

def collect_news() -> None:
    """뉴스 수집 실행."""
    print(f"[{_now()}] 뉴스 수집 시작...")
    for market in ["us", "kr"]:
        try:
            result = subprocess.run(
                ["python3", "scripts/collect_news.py", "--market", market],
                capture_output=True, text=True, timeout=120,
                cwd=str(_PROJECT_ROOT),
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                print(f"  [{market}] 수집 완료 ({len(lines)} lines output)")
            else:
                print(f"  [{market}] 수집 실패: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print(f"  [{market}] 수집 타임아웃 (120초)")
        except Exception as e:
            print(f"  [{market}] 수집 에러: {e}")


def find_relevant_news(issue_name: str) -> list[dict]:
    """이슈별 키워드로 최근 뉴스를 필터링한다."""
    from sqlalchemy import or_, select

    from src.core.database import NewsItemDB, get_session

    keywords = ISSUE_KEYWORDS.get(issue_name, [])
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


# ── Ollama 로컬 LLM 추출 ────────────────────────────────────────────────────

def _call_ollama(prompt: str) -> str | None:
    """Ollama API 호출. 실패 시 None 반환."""
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
    """LLM 응답에서 JSON을 파싱한다. 마크다운 코드블록도 처리."""
    if not text:
        return {}
    # ```json ... ``` 블록 추출
    if "```" in text:
        start = text.find("```")
        # json 태그 건너뛰기
        first_newline = text.find("\n", start)
        end = text.find("```", first_newline)
        if end > first_newline:
            text = text[first_newline:end].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 부분 JSON이라도 시도
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
        for item in news[:10]  # 10개로 확대 (summary/content 포함)
    )

    prompt = EXTRACTION_PROMPT.format(issue=issue_name, articles=articles_text)
    raw = _call_ollama(prompt)
    if not raw:
        return {}

    result = _parse_json(raw)
    return result


def _save_extraction(entities: list[dict], relationships: list[dict]) -> int:
    """추출 결과를 DB에 저장한다. 중복 체크 포함. 새 관계 수 반환."""
    from src.core.models import EntityType, Market, OntologyEntity, OntologyLink
    from src.storage import OntologyEntityRepository, OntologyLinkRepository

    e_repo = OntologyEntityRepository()
    l_repo = OntologyLinkRepository()

    # 엔티티 저장 (dedup by name, 노이즈 필터 적용)
    entity_id_map: dict[str, str] = {}
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
            continue

        # Ollama가 허용 범위 밖의 entity_type 반환 시 기본값 처리
        raw_type = ent_data.get("entity_type", "country")
        valid_types = {e.value for e in EntityType}
        if raw_type not in valid_types:
            print(f"  ⚠ 잘못된 entity_type '{raw_type}' → 'institution' 대체 ({name})")
            raw_type = "institution"

        entity = OntologyEntity(
            name=name,
            entity_type=raw_type,
            market=Market.US,
            aliases=ent_data.get("aliases", []),
        )
        e_repo.create(entity)
        entity_id_map[name.lower()] = entity.id

    # 관계 저장 (dedup)
    new_links = 0
    allowed_types = {
        "mentions", "triggers", "involves", "impacts", "reacts_to",
        "supports", "ally", "hostile", "proxy", "trade", "supply", "sanctions",
    }
    for rel_data in relationships:
        src_name = rel_data.get("source", "").lower()
        tgt_name = rel_data.get("target", "").lower()
        src_id = entity_id_map.get(src_name)
        tgt_id = entity_id_map.get(tgt_name)
        if not src_id or not tgt_id:
            continue

        link_type = rel_data.get("relation_type", "impacts")
        if link_type not in allowed_types:
            link_type = "impacts"  # 허용되지 않는 타입 → fallback

        existing = l_repo.get_many(filters={
            "source_type": "entity", "source_id": src_id,
            "target_type": "entity", "target_id": tgt_id,
            "link_type": link_type,
        }, limit=1)
        if existing:
            continue

        link = OntologyLink(
            link_type=link_type,
            source_type="entity", source_id=src_id,
            target_type="entity", target_id=tgt_id,
            confidence=rel_data.get("confidence", 0.6),
            evidence=rel_data.get("evidence", ""),
        )
        try:
            l_repo.create(link)
            new_links += 1
        except Exception:
            pass  # 중복 unique constraint

    if filtered_count:
        print(f"    ⚡ 노이즈 필터: {filtered_count}개 엔티티 제외")

    return new_links


# ── 유틸 ─────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="GeoInvest 자동 업데이트 (Ollama 로컬 LLM)")
    parser.add_argument("--skip-collect", action="store_true", help="뉴스 수집 건너뛰기")
    parser.add_argument("--dry-run", action="store_true", help="추출만 하고 DB 저장 안 함")
    parser.add_argument("--issue", type=str, default=None, help="특정 이슈만 업데이트")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"GeoInvest 업데이트 — {_now()} (Ollama {OLLAMA_MODEL})")
    print(f"{'='*50}")

    # 1. 뉴스 수집
    if not args.skip_collect:
        collect_news()

    # 2. DB 초기화
    from src.core.database import init_db
    init_db()

    # 3. Ollama 접속 확인
    try:
        r = http_requests.get("http://localhost:11434/api/tags", timeout=3)
        r.raise_for_status()
    except Exception:
        print("  ✗ Ollama 미실행 — ollama serve 필요")
        sys.exit(1)

    # 4. 이슈별 업데이트
    issues = [args.issue] if args.issue else list(ISSUE_KEYWORDS.keys())
    total_entities = 0
    total_links = 0

    for issue_name in issues:
        news = find_relevant_news(issue_name)
        if not news:
            continue

        print(f"\n  {issue_name}: {len(news)}개 뉴스 → Ollama 추출 중...")
        result = extract_entities(issue_name, news)
        entities = result.get("entities", [])
        rels = result.get("relationships", [])
        print(f"    추출: {len(entities)}개 엔티티, {len(rels)}개 관계")

        if args.dry_run:
            print(f"    [DRY-RUN] {[e.get('name') for e in entities[:8]]}")
            continue

        if entities or rels:
            new_links = _save_extraction(entities, rels)
            total_entities += len(entities)
            total_links += new_links
            if new_links:
                print(f"    → {new_links}개 새 관계 저장")

    print(f"\n[{_now()}] 완료 — 엔티티 {total_entities}개 처리, 새 관계 {total_links}개 저장")


if __name__ == "__main__":
    main()
