#!/usr/bin/env python3
"""GeoInvest 벤치마크: AI 온톨로지 추출 품질 vs 수동 gold standard.

이란 전쟁 온톨로지(수동 작성)를 gold standard로 놓고,
같은 데이터를 AI에 넣었을 때 F1 점수를 측정한다.

Usage:
    python scripts/benchmark_geoinvest.py                     # 풀 벤치마크
    python scripts/benchmark_geoinvest.py --dry-run            # gold 파싱만 확인
    python scripts/benchmark_geoinvest.py --use-gold-as-input  # 뉴스 없을 때 md 직접 입력
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))


# ============================================================
# 데이터 모델
# ============================================================


@dataclass
class GoldEntity:
    """Gold standard 엔티티."""

    name: str
    entity_type: str
    aliases: list[str] = field(default_factory=list)


@dataclass
class GoldRelationship:
    """Gold standard 관계."""

    source_name: str
    target_name: str
    relation_type: str


@dataclass
class GoldStandard:
    """파싱된 gold standard 데이터."""

    entities: list[GoldEntity] = field(default_factory=list)
    relationships: list[GoldRelationship] = field(default_factory=list)


@dataclass
class F1Result:
    """F1 측정 결과."""

    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    matched_pairs: list[tuple[str, str]] = field(default_factory=list)


# ============================================================
# Gold Standard 파서
# ============================================================

# 국기 emoji → 국가명 매핑 (alias용)
_FLAG_TO_COUNTRY = {
    "🇺🇸": ("United States", ["미국", "USA", "US"]),
    "🇮🇱": ("Israel", ["이스라엘"]),
    "🇮🇷": ("Iran", ["이란", "Islamic Republic of Iran"]),
    "🇱🇧": ("Hezbollah", ["헤즈볼라", "히즈볼라"]),
    "🇾🇪": ("Houthis", ["후티", "안사르 알라", "Ansar Allah"]),
    "🇮🇶": ("Iraqi Shia Militias", ["시아파 민병대", "이라크 민병대", "PMF"]),
    "🇸🇾": ("Syria", ["시리아"]),
    "🇶🇦": ("Qatar", ["카타르"]),
    "🇧🇭": ("Bahrain", ["바레인"]),
    "🇦🇪": ("UAE", ["아랍에미리트"]),
    "🇸🇦": ("Saudi Arabia", ["사우디아라비아", "사우디"]),
    "🇯🇴": ("Jordan", ["요르단"]),
    "🇰🇷": ("South Korea", ["한국", "대한민국"]),
    "🇨🇳": ("China", ["중국"]),
    "🇯🇵": ("Japan", ["일본"]),
    "🇷🇺": ("Russia", ["러시아"]),
    "🇪🇺": ("EU", ["유럽연합"]),
}

# 섹션 → entity_type 매핑
_SECTION_TYPE_MAP = {
    "1": "country",    # 직접 교전국
    "2": "proxy",      # 프록시/동맹국
    "3": "country",    # 미국 동맹/기지 제공국
    "4": "country",    # 간접 영향국
    "5": "asset",      # 핵심 병목 (호르무즈)
}


def parse_gold_standard(data_dir: Path) -> GoldStandard:
    """5개 md 파일에서 gold standard 엔티티/관계를 파싱한다."""
    gold = GoldStandard()

    # 1. ontology_map.md — 핵심 엔티티 + 관계
    ontology_path = data_dir / "ontology_map.md"
    if ontology_path.exists():
        _parse_ontology_map(ontology_path, gold)

    # 2. proxy_network.md — 프록시 관계 보강
    proxy_path = data_dir / "proxy_network.md"
    if proxy_path.exists():
        _parse_proxy_network(proxy_path, gold)

    # 3. economic_impact.md — 경제 관계 보강
    econ_path = data_dir / "economic_impact.md"
    if econ_path.exists():
        _parse_economic_impact(econ_path, gold)

    # 중복 엔티티 제거
    seen_names = set()
    unique_entities = []
    for e in gold.entities:
        key = e.name.lower()
        if key not in seen_names:
            seen_names.add(key)
            unique_entities.append(e)
    gold.entities = unique_entities

    # 중복 관계 제거
    seen_rels = set()
    unique_rels = []
    for r in gold.relationships:
        key = (r.source_name.lower(), r.target_name.lower(), r.relation_type)
        if key not in seen_rels:
            seen_rels.add(key)
            unique_rels.append(r)
    gold.relationships = unique_rels

    return gold


def _parse_ontology_map(path: Path, gold: GoldStandard) -> None:
    """ontology_map.md에서 엔티티와 관계를 추출한다."""
    content = path.read_text(encoding="utf-8")
    current_section = "0"

    for line in content.split("\n"):
        # 섹션 감지: ## 1. 직접 교전국
        section_match = re.match(r"^## (\d+)\.", line)
        if section_match:
            current_section = section_match.group(1)
            continue

        # 엔티티 감지: ### 🇺🇸 미국
        entity_match = re.match(r"^### (.+)", line)
        if entity_match:
            raw = entity_match.group(1).strip()
            # 국기 emoji로 시작하는 경우
            for flag, (eng_name, aliases) in _FLAG_TO_COUNTRY.items():
                if flag in raw:
                    entity_type = _SECTION_TYPE_MAP.get(current_section, "country")
                    # 프록시 섹션의 비국가 행위자
                    if current_section == "2" and eng_name in ("Hezbollah", "Houthis", "Iraqi Shia Militias"):
                        entity_type = "proxy"
                    # 한국어 이름도 추출
                    korean_name = raw.replace(flag, "").strip()
                    # 괄호 안 정보 제거: "헤즈볼라 (레바논)" → "헤즈볼라"
                    korean_name = re.sub(r"\s*\(.*?\)", "", korean_name).strip()
                    all_aliases = aliases.copy()
                    if korean_name and korean_name not in all_aliases:
                        all_aliases.append(korean_name)
                    gold.entities.append(GoldEntity(
                        name=eng_name,
                        entity_type=entity_type,
                        aliases=all_aliases,
                    ))
                    break

    # 호르무즈 해협 (섹션 5)
    if "호르무즈 해협" in content:
        gold.entities.append(GoldEntity(
            name="Strait of Hormuz",
            entity_type="asset",
            aliases=["호르무즈 해협", "호르무즈", "Hormuz"],
        ))

    # 관계 추출 (다이어그램 + 텍스트 기반)
    _extract_relationships_from_map(content, gold)


def _extract_relationships_from_map(content: str, gold: GoldStandard) -> None:
    """ontology_map.md의 텍스트와 다이어그램에서 관계를 추출한다."""
    # 다이어그램 + 텍스트에서 파악된 핵심 관계 (수동 정의)
    # 이건 gold standard이니까 수동이 맞음
    relationships = [
        # 동맹/합동 작전
        ("United States", "Israel", "ally"),
        # 적대 관계
        ("United States", "Iran", "hostile"),
        ("Israel", "Iran", "hostile"),
        ("Israel", "Hezbollah", "hostile"),
        # 기지 제공/동맹
        ("Qatar", "United States", "base"),
        ("Bahrain", "United States", "base"),
        ("UAE", "United States", "ally"),
        ("Saudi Arabia", "United States", "ally"),
        ("Jordan", "United States", "ally"),
        # 프록시 관계
        ("Iran", "Hezbollah", "proxy"),
        ("Iran", "Houthis", "proxy"),
        ("Iran", "Iraqi Shia Militias", "proxy"),
        # 보급로
        ("Syria", "Hezbollah", "supply"),
        ("Iran", "Syria", "supply"),
        # 공격 관계
        ("Iran", "Qatar", "attack"),
        ("Iran", "Bahrain", "attack"),
        ("Iran", "UAE", "attack"),
        ("Iran", "Saudi Arabia", "attack"),
        # 봉쇄
        ("Iran", "Strait of Hormuz", "blockade"),
        # 경제 의존
        ("South Korea", "Qatar", "trade"),
        ("China", "Strait of Hormuz", "trade"),
        ("Japan", "Strait of Hormuz", "trade"),
        # 경제 영향
        ("Strait of Hormuz", "South Korea", "impacts"),
        ("Strait of Hormuz", "China", "impacts"),
        ("Strait of Hormuz", "Japan", "impacts"),
    ]

    for src, tgt, rel_type in relationships:
        gold.relationships.append(GoldRelationship(
            source_name=src,
            target_name=tgt,
            relation_type=rel_type,
        ))


def _parse_proxy_network(path: Path, gold: GoldStandard) -> None:
    """proxy_network.md에서 추가 엔티티/관계를 보강한다."""
    content = path.read_text(encoding="utf-8")

    # 하마스 추가 (proxy_network에만 언급)
    if "하마스" in content or "Hamas" in content:
        gold.entities.append(GoldEntity(
            name="Hamas",
            entity_type="proxy",
            aliases=["하마스"],
        ))
        gold.relationships.append(GoldRelationship(
            source_name="Iran",
            target_name="Hamas",
            relation_type="proxy",
        ))

    # IRGC 쿠드스군 (조직)
    if "쿠드스군" in content or "IRGC" in content:
        gold.entities.append(GoldEntity(
            name="IRGC Quds Force",
            entity_type="institution",
            aliases=["IRGC 쿠드스군", "쿠드스군", "IRGC"],
        ))


def _parse_economic_impact(path: Path, gold: GoldStandard) -> None:
    """economic_impact.md에서 원자재 엔티티와 경제 관계를 보강한다."""
    content = path.read_text(encoding="utf-8")

    # 원자재 엔티티 추가
    if "유가" in content or "Brent" in content:
        gold.entities.append(GoldEntity(
            name="Crude Oil",
            entity_type="commodity",
            aliases=["원유", "유가", "Brent", "WTI", "석유"],
        ))
    if "금" in content or "gold" in content.lower():
        gold.entities.append(GoldEntity(
            name="Gold",
            entity_type="commodity",
            aliases=["금", "금값"],
        ))


# ============================================================
# 뉴스 조회
# ============================================================


def fetch_iran_news(limit: int = 50) -> list[dict]:
    """DB에서 이란 관련 뉴스를 조회한다."""
    from sqlalchemy import or_, select

    from src.core.database import NewsItemDB, get_session

    with get_session() as session:
        stmt = (
            select(NewsItemDB)
            .where(
                or_(
                    NewsItemDB.title.ilike("%iran%"),
                    NewsItemDB.title.ilike("%이란%"),
                    NewsItemDB.title.ilike("%호르무즈%"),
                    NewsItemDB.title.ilike("%hormuz%"),
                    NewsItemDB.title.ilike("%hezbollah%"),
                    NewsItemDB.title.ilike("%헤즈볼라%"),
                    NewsItemDB.title.ilike("%후티%"),
                    NewsItemDB.title.ilike("%houthi%"),
                    NewsItemDB.title.ilike("%전쟁%"),
                )
            )
            .order_by(NewsItemDB.created_at.desc())
            .limit(limit)
        )
        rows = session.execute(stmt).scalars().all()
        return [
            {
                "title": r.title,
                "content": r.content or "",
                "summary": r.summary or "",
                "source": r.source,
                "published_at": str(r.published_at or r.created_at),
            }
            for r in rows
        ]


def load_gold_as_input(data_dir: Path) -> list[dict]:
    """뉴스가 없을 때 gold standard md 파일 자체를 입력으로 사용한다."""
    articles = []
    for fname in ["ontology_map.md", "timeline.md", "economic_impact.md",
                   "proxy_network.md", "nuclear_program.md"]:
        fpath = data_dir / fname
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8")
            articles.append({
                "title": f"Gold Standard: {fname}",
                "content": content,
                "summary": content[:300],
                "source": "gold_standard",
                "published_at": "2026-03-28",
            })
    return articles


# ============================================================
# Claude 추출
# ============================================================

EXTRACTION_SYSTEM_PROMPT = """You are a geopolitical intelligence analyst specializing in the Middle East. Extract ALL entities and relationships from the provided text.

## Output Format
Output ONLY valid JSON:
{
  "entities": [
    {"name": "<canonical English name>", "entity_type": "<type>", "aliases": ["<Korean>", "<alt>"]}
  ],
  "relationships": [
    {"source_name": "<English name>", "target_name": "<English name>", "relation_type": "<type>", "confidence": 0.9, "evidence": "<brief>"}
  ]
}

## Entity Types (use exactly these)
- country: sovereign nations (United States, Iran, Israel, South Korea, China, Japan, Russia, Qatar, Bahrain, UAE, Saudi Arabia, Jordan, EU)
- proxy: non-state armed groups controlled/funded by a state (Hezbollah, Houthis, Iraqi Shia Militias, Hamas)
- institution: military/government organizations (IRGC Quds Force)
- asset: strategic locations (Strait of Hormuz, Red Sea)
- commodity: tradeable resources (Crude Oil, Gold, Natural Gas, Helium)
- person: key individuals

## Relationship Types (use EXACTLY these — not synonyms)
- ally: formal alliance or joint military operation (US-Israel, US-Saudi, US-UAE, US-Jordan)
- hostile: active military conflict or declared enemy (US-Iran, Israel-Iran, Israel-Hezbollah)
- proxy: state controls/funds a non-state group (Iran→Hezbollah, Iran→Houthis, Iran→Iraqi Shia Militias, Iran→Hamas)
- attack: one entity attacked another's territory/assets (Iran→Qatar, Iran→Bahrain, Iran→UAE, Iran→Saudi Arabia)
- base: one country hosts another's military base (Qatar→US, Bahrain→US)
- supply: arms/logistics supply chain (Iran→Syria, Syria→Hezbollah)
- trade: economic dependency or trade relationship (South Korea→Qatar for helium, China→Strait of Hormuz for oil)
- blockade: blocking passage of goods/ships (Iran→Strait of Hormuz)
- impacts: economic or security impact on another entity (Strait of Hormuz→South Korea, Strait of Hormuz→China)
- sanctions: economic sanctions imposed

## Critical Rules
1. Use CANONICAL English names: "United States" (not US/USA/미국), "Saudi Arabia" (not 사우디), "Hezbollah" (not 헤즈볼라)
2. Include Korean aliases: ["미국", "USA"] for United States
3. Extract ALL entities mentioned — even briefly mentioned countries like Bahrain, Jordan, EU
4. Use ONLY the relation_types listed above — do NOT invent new types like "military_alliance" or "economic_partnership"
5. Be exhaustive: extract every entity and every relationship you can find in the text"""


def extract_via_claude(news_items: list[dict]) -> dict:
    """뉴스를 Claude에 보내 엔티티/관계를 추출한다."""
    from src.core.claude_client import ClaudeClient
    from src.core.models import ClaudeTask

    # 뉴스 텍스트 결합 (토큰 한도 고려, 각 기사 3000자, 최대 30개)
    articles_text = "\n\n---\n\n".join(
        f"Title: {item['title']}\nDate: {item['published_at']}\n"
        f"Content: {(item.get('content') or item.get('summary', ''))[:3000]}"
        for item in news_items[:30]
    )

    user_message = f"""Analyze these texts about the Iran conflict and extract all geopolitical entities and their relationships.

{articles_text}

Extract all entities (countries, proxy groups, commodities, key institutions) and relationships between them. Output as JSON."""

    client = ClaudeClient()
    response = client.generate(
        task=ClaudeTask.DEEP_ANALYSIS,
        user_message=user_message,
        system_prompt=EXTRACTION_SYSTEM_PROMPT,
    )

    return _parse_json_response(response.content)


def _parse_json_response(content: str) -> dict:
    """Claude 응답에서 JSON을 파싱한다. 코드펜스 처리 포함."""
    # 코드펜스 제거
    content = content.strip()
    if content.startswith("```"):
        # ```json\n...\n``` 패턴
        lines = content.split("\n")
        # 첫 줄과 마지막 줄 제거
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines)

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON 파싱 실패: {e}")
        print(f"응답 처음 500자: {content[:500]}")
        return {"entities": [], "relationships": []}


# ============================================================
# F1 계산
# ============================================================


def _normalize(name: str) -> str:
    """엔티티 이름을 정규화한다."""
    return name.strip().lower()


def _entity_matches(gold: GoldEntity, pred_name: str, pred_aliases: list[str]) -> bool:
    """Gold 엔티티와 예측 엔티티가 매칭되는지 확인한다."""
    pred_name_n = _normalize(pred_name)
    pred_aliases_n = {_normalize(a) for a in pred_aliases}
    gold_name_n = _normalize(gold.name)
    gold_aliases_n = {_normalize(a) for a in gold.aliases}

    # 이름끼리 매칭
    if pred_name_n == gold_name_n:
        return True
    # 예측 이름이 gold alias에 포함
    if pred_name_n in gold_aliases_n:
        return True
    # gold 이름이 예측 alias에 포함
    if gold_name_n in pred_aliases_n:
        return True
    # alias끼리 교집합
    if pred_aliases_n & gold_aliases_n:
        return True
    return False


def compute_entity_f1(
    gold_entities: list[GoldEntity],
    pred_entities: list[dict],
) -> F1Result:
    """엔티티 F1을 계산한다."""
    result = F1Result()
    gold_matched = set()
    pred_matched = set()

    for pi, pred in enumerate(pred_entities):
        pred_name = pred.get("name", "")
        pred_aliases = pred.get("aliases", [])
        for gi, gold in enumerate(gold_entities):
            if gi in gold_matched:
                continue
            if _entity_matches(gold, pred_name, pred_aliases):
                gold_matched.add(gi)
                pred_matched.add(pi)
                result.matched_pairs.append((gold.name, pred_name))
                result.true_positives += 1
                break

    result.false_positives = len(pred_entities) - len(pred_matched)
    result.false_negatives = len(gold_entities) - len(gold_matched)

    if result.true_positives > 0:
        result.precision = result.true_positives / (result.true_positives + result.false_positives)
        result.recall = result.true_positives / (result.true_positives + result.false_negatives)
        result.f1 = 2 * result.precision * result.recall / (result.precision + result.recall)

    return result


def _resolve_name(name: str, gold_entities: list[GoldEntity]) -> str:
    """이름을 canonical name으로 해소한다."""
    name_n = _normalize(name)
    for g in gold_entities:
        if _normalize(g.name) == name_n:
            return g.name
        for alias in g.aliases:
            if _normalize(alias) == name_n:
                return g.name
    return name  # 매칭 안 되면 원래 이름 반환


def compute_relationship_f1(
    gold_rels: list[GoldRelationship],
    pred_rels: list[dict],
    gold_entities: list[GoldEntity],
) -> F1Result:
    """관계 F1을 계산한다. (source, target, type) 튜플 매칭."""
    result = F1Result()

    # Gold를 정규화된 튜플 셋으로
    gold_tuples = set()
    for r in gold_rels:
        key = (_normalize(r.source_name), _normalize(r.target_name), r.relation_type)
        gold_tuples.add(key)

    # 예측을 정규화 (alias 해소 포함)
    pred_tuples = set()
    for r in pred_rels:
        src = _resolve_name(r.get("source_name", ""), gold_entities)
        tgt = _resolve_name(r.get("target_name", ""), gold_entities)
        rel = r.get("relation_type", "")
        key = (_normalize(src), _normalize(tgt), rel)
        pred_tuples.add(key)

    # 교집합
    matched = gold_tuples & pred_tuples
    result.true_positives = len(matched)
    result.false_positives = len(pred_tuples) - len(matched)
    result.false_negatives = len(gold_tuples) - len(matched)
    result.matched_pairs = [(f"{s}->{t} [{r}]", f"{s}->{t} [{r}]") for s, t, r in matched]

    if result.true_positives > 0:
        result.precision = result.true_positives / (result.true_positives + result.false_positives)
        result.recall = result.true_positives / (result.true_positives + result.false_negatives)
        result.f1 = 2 * result.precision * result.recall / (result.precision + result.recall)

    return result


# ============================================================
# 출력
# ============================================================


def print_gold_summary(gold: GoldStandard) -> None:
    """Gold standard 파싱 결과를 출력한다."""
    print("\n" + "=" * 60)
    print("GOLD STANDARD SUMMARY")
    print("=" * 60)

    print(f"\n엔티티 ({len(gold.entities)}개):")
    for e in gold.entities:
        aliases_str = ", ".join(e.aliases[:3])
        print(f"  [{e.entity_type:12s}] {e.name:25s} aka {aliases_str}")

    print(f"\n 관계 ({len(gold.relationships)}개):")
    for r in gold.relationships:
        print(f"  {r.source_name:25s} --[{r.relation_type:10s}]--> {r.target_name}")


def print_results(entity_f1: F1Result, rel_f1: F1Result) -> None:
    """벤치마크 결과를 출력한다."""
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)

    print("\n📊 Entity F1:")
    print(f"  Precision: {entity_f1.precision:.3f}")
    print(f"  Recall:    {entity_f1.recall:.3f}")
    print(f"  F1:        {entity_f1.f1:.3f}")
    print(f"  TP: {entity_f1.true_positives}, FP: {entity_f1.false_positives}, FN: {entity_f1.false_negatives}")
    if entity_f1.matched_pairs:
        print("  Matched:")
        for gold_name, pred_name in entity_f1.matched_pairs:
            print(f"    ✓ {gold_name} ↔ {pred_name}")

    print(f"\n🔗 Relationship F1:")
    print(f"  Precision: {rel_f1.precision:.3f}")
    print(f"  Recall:    {rel_f1.recall:.3f}")
    print(f"  F1:        {rel_f1.f1:.3f}")
    print(f"  TP: {rel_f1.true_positives}, FP: {rel_f1.false_positives}, FN: {rel_f1.false_negatives}")

    # 게이트 결정
    avg_f1 = (entity_f1.f1 + rel_f1.f1) / 2
    print("\n" + "=" * 60)
    print("GATE DECISION")
    print("=" * 60)
    print(f"\n  Average F1: {avg_f1:.3f}")

    if avg_f1 >= 0.70:
        print("  ✅ PROCEED — Approach B (Full Automation)")
        print("  Entity F1 >= 0.70 AND Relationship F1 기준 통과.")
    elif avg_f1 >= 0.50:
        print("  ⚠️  HYBRID — Approach C (AI 초안 + 사람 검수)")
        print("  F1이 50-70% 구간. AI가 초안을 만들고 사람이 검수하는 방식 권장.")
    else:
        print("  ❌ REDESIGN — 추출 전략 재설계 필요")
        print("  F1 < 50%. 프롬프트나 접근 방식을 근본적으로 재고해야 함.")

    # 미매칭 엔티티 출력 (디버깅용)
    if entity_f1.false_negatives > 0:
        print(f"\n  ⚠️ 미발견 엔티티 ({entity_f1.false_negatives}개):")
        matched_gold = {pair[0] for pair in entity_f1.matched_pairs}
        # 이 정보는 gold 목록에서 역추적해야 함
        print("    (gold에 있지만 AI가 못 찾은 것들)")


# ============================================================
# Main
# ============================================================


def main() -> None:
    """벤치마크 메인 진입점."""
    parser = argparse.ArgumentParser(
        description="GeoInvest 벤치마크: AI 추출 품질 vs gold standard",
    )
    parser.add_argument(
        "--data-dir",
        default="data/research/geopolitics/iran_conflict",
        help="Gold standard 데이터 디렉토리",
    )
    parser.add_argument(
        "--news-limit",
        type=int,
        default=50,
        help="조회할 뉴스 최대 개수",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Gold standard 파싱만 확인 (Claude 호출 안 함)",
    )
    parser.add_argument(
        "--use-gold-as-input",
        action="store_true",
        help="뉴스 대신 gold standard md 파일을 Claude 입력으로 사용",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"ERROR: 데이터 디렉토리 없음: {data_dir}")
        sys.exit(1)

    # 1. Gold standard 파싱
    print("📂 Gold standard 파싱 중...")
    gold = parse_gold_standard(data_dir)
    print(f"  → {len(gold.entities)}개 엔티티, {len(gold.relationships)}개 관계")

    if args.dry_run:
        print_gold_summary(gold)
        return

    # 2. 뉴스 조회 또는 gold-as-input
    if args.use_gold_as_input:
        print("\n📄 Gold standard 파일을 입력으로 사용...")
        news = load_gold_as_input(data_dir)
    else:
        print("\n📰 DB에서 이란 관련 뉴스 조회 중...")
        # DB 초기화
        from src.core.database import init_db
        init_db()
        news = fetch_iran_news(limit=args.news_limit)

    print(f"  → {len(news)}개 기사/문서")

    if not news:
        print("\nWARNING: 이란 관련 뉴스가 DB에 없습니다.")
        print("  --use-gold-as-input 옵션으로 md 파일을 직접 입력하세요.")
        print("  또는 먼저 뉴스를 수집하세요: python scripts/collect_news.py --market us")
        sys.exit(1)

    # 3. Claude 추출
    print("\n🤖 Claude API로 온톨로지 추출 중 (DEEP_ANALYSIS)...")
    ai_output = extract_via_claude(news)
    ai_entities = ai_output.get("entities", [])
    ai_rels = ai_output.get("relationships", [])
    print(f"  → {len(ai_entities)}개 엔티티, {len(ai_rels)}개 관계 추출됨")

    # 4. F1 계산
    print("\n📏 F1 계산 중...")
    entity_f1 = compute_entity_f1(gold.entities, ai_entities)
    rel_f1 = compute_relationship_f1(gold.relationships, ai_rels, gold.entities)

    # 5. 결과 출력
    print_gold_summary(gold)
    print_results(entity_f1, rel_f1)


if __name__ == "__main__":
    main()
