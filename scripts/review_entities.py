#!/usr/bin/env python3
"""엔티티 리뷰 & 정제 파이프라인.

실행:
    python3 scripts/review_entities.py
    python3 scripts/review_entities.py --dry-run     # 변경 없이 리포트만
    python3 scripts/review_entities.py --phase noise  # 도메인/노이즈 삭제만
    python3 scripts/review_entities.py --phase type   # 타입 교정만
    python3 scripts/review_entities.py --phase merge   # 병합만
    python3 scripts/review_entities.py --phase dedup   # 관계 중복 제거만
    python3 scripts/review_entities.py --phase cross   # 크로스 이슈 연결만
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests as http_requests

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"
REPORT_DIR = _PROJECT_ROOT / "data" / "reports"


def _call_ollama(prompt: str, timeout: int = 60) -> str:
    """Ollama 호출."""
    try:
        resp = http_requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as e:
        print(f"    Ollama 에러: {e}")
        return ""


def _parse_json(text: str) -> Any:
    """JSON 파싱 (마크다운 코드블록 처리)."""
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


# ============================================================
# Phase 0: 도메인/노이즈 엔티티 삭제
# ============================================================

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
    cleaned = re.sub(r"[\d$€₩¥%,.~\-–��주년월일개건조억만천]", "", name).strip()
    if not cleaned:
        return True
    return False


def phase_noise_cleanup(dry_run: bool = False) -> dict:
    """도메인, 숫���, 노이즈 단어 엔티티를 삭제한다."""
    from src.storage import OntologyEntityRepository, OntologyLinkRepository

    e_repo = OntologyEntityRepository()
    l_repo = OntologyLinkRepository()

    all_entities = e_repo.get_many(limit=3000)
    print(f"\n{'='*60}")
    print(f"Phase 0: 도메인/노이��� 엔티티 삭제 — {len(all_entities)}개 검토")
    print(f"{'='*60}")

    noise_entities = [e for e in all_entities if _is_noise_entity(e.name)]
    removed = []

    for entity in noise_entities:
        removed.append({"id": entity.id, "name": entity.name, "type": entity.entity_type})
        if not dry_run:
            # 연결된 관계 먼저 삭제
            links_from = l_repo.get_many(filters={"source_id": entity.id}, limit=500)
            links_to = l_repo.get_many(filters={"target_id": entity.id}, limit=500)
            for lk in links_from + links_to:
                l_repo.delete(lk.id)
            e_repo.delete(entity.id)

    if removed:
        print(f"  삭제 대상 (상위 20개):")
        for r in removed[:20]:
            print(f"    {r['name']:40s} ({r['type']})")
        if len(removed) > 20:
            print(f"    ... 외 {len(removed) - 20}개")

    print(f"\n  결과: {len(removed)}개 노이��� 엔티티 삭제")
    return {"total": len(all_entities), "removed": len(removed), "removed_list": removed}


# ============================================================
# Phase 1: 엔티티 타입 교정
# ============================================================

def phase_type_correction(dry_run: bool = False) -> dict:
    """institution으로 잘못 분류된 엔티티를 Ollama로 재분류."""
    from src.core.models import EntityType
    from src.storage import OntologyEntityRepository

    repo = OntologyEntityRepository()
    valid_types = {e.value for e in EntityType}

    # institution 엔티��� 조회
    all_entities = repo.get_many(filters={"entity_type": "institution"}, limit=1000)
    print(f"\n{'='*60}")
    print(f"Phase 1: 엔티티 타입 교정 — {len(all_entities)}개 institution 검토")
    print(f"{'='*60}")

    if not all_entities:
        print("  교정 대상 없음")
        return {"reviewed": 0, "corrected": 0, "corrections": []}

    # 배치로 Ollama에 타입 ���류 요청 (30개씩)
    corrections = []
    batch_size = 30

    for batch_start in range(0, len(all_entities), batch_size):
        batch = all_entities[batch_start:batch_start + batch_size]
        names = [e.name for e in batch]

        prompt = f"""Classify each entity into exactly one type. Types: company, person, asset, institution, sector, country, commodity, proxy

Rules:
- company: corporations, firms (Samsung, Tesla, Apple)
- person: individuals (Elon Musk, Powell, 이창용)
- asset: stocks, ETFs, currencies, crypto (S&P500, Bitcoin, USD, 원화)
- institution: government agencies, central banks, international orgs (Fed, BOK, SEC, NATO)
- sector: industries (반도체, AI, 배터리, fintech)
- country: nations (미국, China, Japan)
- commodity: raw materials, energy (oil, gold, lithium, 원유)
- proxy: non-state actors, militias (Hezbollah, Wagner)

Entities:
{json.dumps(names, ensure_ascii=False)}

Return ONLY a JSON array of objects, no explanation:
[{{"name": "...", "type": "company|person|asset|institution|sector|country|commodity|proxy"}}]"""

        raw = _call_ollama(prompt, timeout=90)
        results = _parse_json(raw)

        if not isinstance(results, list):
            print(f"    배치 {batch_start//batch_size + 1} 파싱 실패 — 스킵")
            continue

        name_to_type = {r.get("name", ""): r.get("type", "") for r in results}

        for entity in batch:
            new_type = name_to_type.get(entity.name, "")
            if not new_type or new_type not in valid_types:
                continue
            if new_type == "institution":
                continue  # 이미 institution이면 변경 없음

            corrections.append({
                "id": entity.id,
                "name": entity.name,
                "old_type": "institution",
                "new_type": new_type,
            })

            if not dry_run:
                repo.update(entity.id, entity_type=new_type)

        done = min(batch_start + batch_size, len(all_entities))
        print(f"  [{done}/{len(all_entities)}] 검토 완료 — {len(corrections)}개 교정")

    print(f"\n  결과: {len(all_entities)}개 검토, {len(corrections)}개 교정")
    return {
        "reviewed": len(all_entities),
        "corrected": len(corrections),
        "corrections": corrections,
    }


# ============================================================
# Phase 2: 별칭 병합 (중복 엔티티)
# ============================================================

def phase_merge_duplicates(dry_run: bool = False) -> dict:
    """같은 대상을 가리키는 엔티티를 병합."""
    from src.storage import OntologyEntityRepository, OntologyLinkRepository

    e_repo = OntologyEntityRepository()
    l_repo = OntologyLinkRepository()

    all_entities = e_repo.get_many(limit=2000)
    print(f"\n{'='*60}")
    print(f"Phase 2: 별칭 병합 — {len(all_entities)}개 엔티티 검토")
    print(f"{'='*60}")

    # 이름 정규화 → 같은 대상 찾기
    normalized: dict[str, list] = defaultdict(list)
    for e in all_entities:
        # 정규화: 소문자, 공백 제거, 특수문자 제거
        key = re.sub(r"[^a-z0-9가-힣]", "", e.name.lower())
        normalized[key].append(e)

    # 추가: 한영 매칭 (알려진 매핑)
    KNOWN_ALIASES = {
        "tesla": ["테슬라", "tsla"],
        "samsung": ["삼성전자", "삼성"],
        "skhynix": ["sk하이닉스", "하이닉스"],
        "hyundai": ["현대차", "현대자동차"],
        "nvidia": ["엔비디아", "nvda"],
        "apple": ["애플", "aapl"],
        "microsoft": ["마이크로소프트", "msft"],
        "amazon": ["아마존", "amzn"],
        "google": ["구글", "googl", "alphabet"],
        "fed": ["연준", "federalreserve", "연방준비"],
        "bok": ["한국은행", "한은"],
        "bitcoin": ["비트코인", "btc"],
        "ethereum": ["이더리움", "eth"],
        "elonmusk": ["일론머스크", "일론", "머스크"],
        "china": ["중국"],
        "japan": ["일본"],
        "usa": ["미국", "unitedstates"],
        "russia": ["러시아"],
        "ukraine": ["우크라이나"],
        "iran": ["이란"],
    }

    # 별칭 그룹 구성
    alias_groups: dict[str, list[str]] = {}
    for canonical, aliases in KNOWN_ALIASES.items():
        all_names = [canonical] + aliases
        all_norm = [re.sub(r"[^a-z0-9가-힣]", "", n.lower()) for n in all_names]
        alias_groups[canonical] = all_norm

    # 병합 대상 찾기
    merge_candidates = []

    # 1) 정규화 중복
    for key, entities in normalized.items():
        if len(entities) > 1:
            merge_candidates.append({
                "reason": "normalized_match",
                "keep": entities[0],
                "merge": entities[1:],
            })

    # 2) 알려진 별칭 중복
    for canonical, norm_names in alias_groups.items():
        matching = []
        for norm in norm_names:
            if norm in normalized:
                matching.extend(normalized[norm])
        if len(matching) > 1:
            # 중복 제거
            seen_ids = set()
            unique = []
            for e in matching:
                if e.id not in seen_ids:
                    seen_ids.add(e.id)
                    unique.append(e)
            if len(unique) > 1:
                merge_candidates.append({
                    "reason": f"known_alias({canonical})",
                    "keep": unique[0],
                    "merge": unique[1:],
                })

    print(f"  병합 후보: {len(merge_candidates)}개 그룹")

    merged_count = 0
    merge_log = []

    for candidate in merge_candidates:
        keep = candidate["keep"]
        for dup in candidate["merge"]:
            merge_log.append({
                "keep_id": keep.id,
                "keep_name": keep.name,
                "remove_id": dup.id,
                "remove_name": dup.name,
                "reason": candidate["reason"],
            })

            if not dry_run:
                # 관계의 source/target을 keep으로 재연결
                links_from = l_repo.get_many(
                    filters={"source_id": dup.id}, limit=500)
                links_to = l_repo.get_many(
                    filters={"target_id": dup.id}, limit=500)

                for lk in links_from:
                    l_repo.update(lk.id, source_id=keep.id)
                for lk in links_to:
                    l_repo.update(lk.id, target_id=keep.id)

                # 별칭 보존
                keep_aliases = set(keep.aliases or [])
                keep_aliases.add(dup.name)
                keep_aliases.update(dup.aliases or [])
                e_repo.update(keep.id, aliases=list(keep_aliases))

                # 중복 ���티티 삭제
                e_repo.delete(dup.id)

            merged_count += 1

    print(f"  결과: {merged_count}개 엔티티 병합")
    return {
        "candidates": len(merge_candidates),
        "merged": merged_count,
        "log": merge_log,
    }


# ============================================================
# Phase 3: 관계 중복 제거
# ============================================================

def phase_dedup_links(dry_run: bool = False) -> dict:
    """동일 source→target→type 관계 중복 제거."""
    from src.storage import OntologyLinkRepository

    l_repo = OntologyLinkRepository()
    all_links = l_repo.get_many(limit=5000)

    print(f"\n{'='*60}")
    print(f"Phase 3: 관계 중복 제거 — {len(all_links)}개 관계 검토")
    print(f"{'='*60}")

    seen: dict[tuple, str] = {}  # (src, tgt, type) → keep_id
    duplicates = []

    for lk in all_links:
        key = (lk.source_id, lk.target_id, lk.link_type)
        if key in seen:
            duplicates.append(lk.id)
            if not dry_run:
                l_repo.delete(lk.id)
        else:
            seen[key] = lk.id

    print(f"  결과: {len(duplicates)}개 중복 관계 제거")
    return {
        "total": len(all_links),
        "duplicates_removed": len(duplicates),
    }


# ============================================================
# Phase 4: 크로스 이슈 엔티티 ���유
# ============================================================

def phase_cross_issue(dry_run: bool = False) -> dict:
    """엔티티가 여러 이슈에 관련되면 자동 연결."""
    from src.storage import GeoIssueRepository, OntologyLinkRepository

    issue_repo = GeoIssueRepository()
    link_repo = OntologyLinkRepository()

    all_issues = issue_repo.get_active()
    all_links = link_repo.get_many(limit=5000)

    print(f"\n{'='*60}")
    print(f"Phase 4: 크로스 이슈 엔티티 공유")
    print(f"{'='*60}")

    # 이슈별 엔티티 ID 맵
    issue_entity_map: dict[str, set[str]] = {}
    for issue in all_issues:
        issue_entity_map[issue.id] = set(issue.entity_ids or [])

    # 링크에서 이슈별 엔티티 수집
    link_issue_entities: dict[str, set[str]] = defaultdict(set)
    for lk in all_links:
        if lk.geo_issue_id:
            link_issue_entities[lk.geo_issue_id].add(lk.source_id)
            link_issue_entities[lk.geo_issue_id].add(lk.target_id)

    # 엔티티 → 이슈 매핑
    entity_to_issues: dict[str, set[str]] = defaultdict(set)
    for issue_id, entity_ids in issue_entity_map.items():
        for eid in entity_ids:
            entity_to_issues[eid].add(issue_id)
    for issue_id, entity_ids in link_issue_entities.items():
        for eid in entity_ids:
            entity_to_issues[eid].add(issue_id)

    # 2개 이상 이슈에 걸친 엔티티
    shared = {eid: issues for eid, issues in entity_to_issues.items() if len(issues) >= 2}

    # 이슈 entity_ids 갱신
    updates = 0
    for eid, issue_ids in shared.items():
        for iid in issue_ids:
            if iid in issue_entity_map and eid not in issue_entity_map[iid]:
                issue_entity_map[iid].add(eid)
                if not dry_run:
                    issue_repo.update(iid, entity_ids=list(issue_entity_map[iid]))
                updates += 1

    print(f"  공유 엔티티: {len(shared)}개 (2개+ 이슈 걸침)")
    print(f"  이슈 연결 갱신: {updates}건")
    return {
        "shared_entities": len(shared),
        "issue_updates": updates,
    }


# ============================================================
# 리포트 생성
# ============================================================

def generate_report(results: dict, dry_run: bool) -> str:
    """리뷰 결과 리포트 생성."""
    from src.core.models import EntityType
    from src.storage import OntologyEntityRepository, OntologyLinkRepository

    e_repo = OntologyEntityRepository()
    l_repo = OntologyLinkRepository()

    # 현재 상태 조회
    all_entities = e_repo.get_many(limit=2000)
    all_links = l_repo.get_many(limit=5000)

    type_dist = Counter(e.entity_type for e in all_entities)
    link_type_dist = Counter(lk.link_type for lk in all_links)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    mode = "DRY-RUN" if dry_run else "APPLIED"

    report = f"""# 엔티티 리뷰 리포트

> 생성: {ts} | 모드: {mode}

---

## 요약

| 항목 | 결과 |
|------|------|
| Phase 0: 노이즈 삭제 | {results['noise']['total']}개 검토 → {results['noise']['removed']}개 삭제 |
| Phase 1: 타입 교정 | {results['type']['reviewed']}개 검토 → {results['type']['corrected']}개 교정 |
| Phase 2: 별칭 병합 | {results['merge']['candidates']}개 후보 → {results['merge']['merged']}개 병합 |
| Phase 3: 관계 중복 제거 | {results['dedup']['total']}개 중 {results['dedup']['duplicates_removed']}개 제거 |
| Phase 4: 크로스 이슈 | {results['cross']['shared_entities']}개 공유, {results['cross']['issue_updates']}건 연결 |

---

## 현재 엔티티 분포 (리뷰 후)

| 타입 | 건수 |
|------|------|
"""
    for t, c in sorted(type_dist.items(), key=lambda x: -x[1]):
        report += f"| {t} | {c} |\n"
    report += f"| **합계** | **{len(all_entities)}** |\n"

    report += f"""
## 현재 관계 분포

| 타입 | 건수 |
|------|------|
"""
    for t, c in sorted(link_type_dist.items(), key=lambda x: -x[1]):
        report += f"| {t} | {c} |\n"
    report += f"| **합계** | **{len(all_links)}** |\n"

    # 타입 교정 상세
    if results["type"]["corrections"]:
        report += "\n## Phase 1: 타입 교정 상세 (상위 30건)\n\n"
        report += "| 엔티티 | 변경 전 | 변경 후 |\n"
        report += "|--------|---------|--------|\n"
        for c in results["type"]["corrections"][:30]:
            report += f"| {c['name']} | {c['old_type']} | {c['new_type']} |\n"

    # 병합 상세
    if results["merge"]["log"]:
        report += "\n## Phase 2: 병합 상세\n\n"
        report += "| 유지 | 병합(삭제) | 이유 |\n"
        report += "|------|-----------|------|\n"
        for m in results["merge"]["log"][:30]:
            report += f"| {m['keep_name']} | {m['remove_name']} | {m['reason']} |\n"

    return report


# ============================================================
# 메인
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="엔티티 리뷰 & 정제")
    parser.add_argument("--dry-run", action="store_true", help="변경 없이 리포트만")
    parser.add_argument("--phase", type=str, default=None,
                        help="특정 phase만 실행 (type/merge/dedup/cross)")
    args = parser.parse_args()

    from src.core.database import init_db
    init_db()

    phases = args.phase.split(",") if args.phase else ["noise", "type", "merge", "dedup", "cross"]

    results = {
        "noise": {"total": 0, "removed": 0, "removed_list": []},
        "type": {"reviewed": 0, "corrected": 0, "corrections": []},
        "merge": {"candidates": 0, "merged": 0, "log": []},
        "dedup": {"total": 0, "duplicates_removed": 0},
        "cross": {"shared_entities": 0, "issue_updates": 0},
    }

    if "noise" in phases:
        results["noise"] = phase_noise_cleanup(dry_run=args.dry_run)
    if "type" in phases:
        results["type"] = phase_type_correction(dry_run=args.dry_run)
    if "merge" in phases:
        results["merge"] = phase_merge_duplicates(dry_run=args.dry_run)
    if "dedup" in phases:
        results["dedup"] = phase_dedup_links(dry_run=args.dry_run)
    if "cross" in phases:
        results["cross"] = phase_cross_issue(dry_run=args.dry_run)

    # 리포트 생성
    report = generate_report(results, dry_run=args.dry_run)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"entity_review_{ts}.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"리포트 저장: {report_path}")
    print(f"{'='*60}")
    print(report)


if __name__ == "__main__":
    main()
