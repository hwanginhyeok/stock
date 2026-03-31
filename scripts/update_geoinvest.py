#!/usr/bin/env python3
"""GeoInvest 자동 업데이트 — 뉴스 수집 → AI 추출 → DB 저장.

cron으로 1시간마다 실행:
    0 * * * * cd ~/stock && python3 scripts/update_geoinvest.py >> logs/geoinvest_update.log 2>&1

수동 실행:
    python scripts/update_geoinvest.py
    python scripts/update_geoinvest.py --skip-collect   # 뉴스 수집 건너뛰기
    python scripts/update_geoinvest.py --dry-run        # 추출만 하고 DB 저장 안 함
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# 이슈별 키워드 (뉴스 필터링용)
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
                # 수집 건수 추출
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


def extract_and_update(issue_name: str, news: list[dict], dry_run: bool = False) -> None:
    """뉴스에서 AI 추출 후 DB에 저장한다 (하이브리드 모드 — 로그로 검수 가능)."""
    from src.core.claude_client import ClaudeClient
    from src.core.models import ClaudeTask

    # 벤치마크에서 검증된 프롬프트 재사용
    from scripts.benchmark_geoinvest import EXTRACTION_SYSTEM_PROMPT, _parse_json_response

    articles_text = "\n\n---\n\n".join(
        f"Title: {item['title']}\nDate: {item['published_at']}\n"
        f"Content: {(item.get('content') or item.get('summary', ''))[:3000]}"
        for item in news[:15]
    )

    user_message = f"""Analyze these news articles related to '{issue_name}' and extract geopolitical entities and relationships.

{articles_text}

Extract all entities and relationships. Output as JSON."""

    client = ClaudeClient()
    response = client.generate(
        task=ClaudeTask.DEEP_ANALYSIS,
        user_message=user_message,
        system_prompt=EXTRACTION_SYSTEM_PROMPT,
    )

    result = _parse_json_response(response.content)
    entities = result.get("entities", [])
    rels = result.get("relationships", [])

    print(f"    추출 결과: {len(entities)}개 엔티티, {len(rels)}개 관계")

    if dry_run:
        print("    [DRY-RUN] DB 저장 건너뜀")
        print(f"    엔티티: {[e.get('name') for e in entities[:10]]}")
        return

    # DB에 새 엔티티/관계 저장 (기존 ontology_io.py의 cmd_apply 로직 활용)
    _save_extraction(entities, rels)


def _save_extraction(entities: list[dict], relationships: list[dict]) -> None:
    """추출 결과를 DB에 저장한다. 중복 체크 포함."""
    from src.core.models import OntologyEntity, OntologyLink, Market
    from src.storage import OntologyEntityRepository, OntologyLinkRepository

    e_repo = OntologyEntityRepository()
    l_repo = OntologyLinkRepository()

    # 엔티티 저장 (dedup by name)
    entity_id_map = {}
    for ent_data in entities:
        name = ent_data.get("name", "")
        if not name:
            continue
        existing = e_repo.find_by_name(name)
        if existing:
            entity_id_map[name.lower()] = existing.id
            continue

        entity = OntologyEntity(
            name=name,
            entity_type=ent_data.get("entity_type", "country"),
            market=Market.US,
            aliases=ent_data.get("aliases", []),
        )
        e_repo.create(entity)
        entity_id_map[name.lower()] = entity.id

    # 관계 저장 (dedup)
    new_links = 0
    for rel_data in relationships:
        src_name = rel_data.get("source_name", "").lower()
        tgt_name = rel_data.get("target_name", "").lower()
        src_id = entity_id_map.get(src_name)
        tgt_id = entity_id_map.get(tgt_name)
        if not src_id or not tgt_id:
            continue

        link_type = rel_data.get("relation_type", "impacts")
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
            confidence=rel_data.get("confidence", 0.7),
            evidence=rel_data.get("evidence", ""),
        )
        try:
            l_repo.create(link)
            new_links += 1
        except Exception:
            pass  # 중복 unique constraint

    if new_links > 0:
        print(f"    → {new_links}개 새 관계 저장")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main() -> None:
    parser = argparse.ArgumentParser(description="GeoInvest 자동 업데이트")
    parser.add_argument("--skip-collect", action="store_true", help="뉴스 수집 건너뛰기")
    parser.add_argument("--dry-run", action="store_true", help="추출만 하고 DB 저장 안 함")
    parser.add_argument("--issue", type=str, default=None, help="특정 이슈만 업데이트")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"GeoInvest 자동 업데이트 — {_now()}")
    print(f"{'='*50}")

    # 1. 뉴스 수집
    if not args.skip_collect:
        collect_news()

    # 2. DB 초기화
    from src.core.database import init_db
    init_db()

    # 3. 이슈별 업데이트
    issues = [args.issue] if args.issue else list(ISSUE_KEYWORDS.keys())
    for issue_name in issues:
        print(f"\n[{_now()}] 이슈 업데이트: {issue_name}")
        news = find_relevant_news(issue_name)
        print(f"  관련 뉴스: {len(news)}개")

        if not news:
            print("  → 관련 뉴스 없음. 스킵.")
            continue

        try:
            extract_and_update(issue_name, news, dry_run=args.dry_run)
        except Exception as e:
            print(f"  → 추출 에러: {e}")

    print(f"\n[{_now()}] 업데이트 완료.")


if __name__ == "__main__":
    main()
