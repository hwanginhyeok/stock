#!/usr/bin/env python3
"""이란 전쟁 GeoIssue 시딩 — 엔티티 + 관계 + 이슈를 DB에 등록.

Usage:
    python scripts/seed_iran_issue.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.database import init_db  # noqa: E402
from src.core.models import (  # noqa: E402
    GeoIssue,
    GeoIssueStatus,
    OntologyEntity,
    OntologyEvent,
    OntologyLink,
    EntityType,
    EventType,
    EventStatus,
    LinkType,
    Severity,
    Market,
)
from src.storage import (  # noqa: E402
    GeoIssueRepository,
    OntologyEntityRepository,
    OntologyEventRepository,
    OntologyLinkRepository,
)


def seed() -> None:
    """이란 전쟁 데이터를 시딩한다."""
    init_db()

    entity_repo = OntologyEntityRepository()
    event_repo = OntologyEventRepository()
    link_repo = OntologyLinkRepository()
    issue_repo = GeoIssueRepository()

    # ============================================================
    # 엔티티 등록
    # ============================================================
    entities_data = [
        # 직접 교전국
        ("United States", EntityType.COUNTRY, "", ["미국", "USA", "US"], {
            "역할": "공격측 주도국 (Operation Epic Fury)",
            "현황": "에너지 시설 공격 일시 중단 (4/6까지 연장), 협상 시도 중",
            "리스크": "지상군 투입 시 장기전화, 유가 $150 시나리오",
        }),
        ("Israel", EntityType.COUNTRY, "", ["이스라엘"], {
            "역할": "공격측 (Operation Roaring Lion)",
            "현황": "레바논 헤즈볼라 재교전, 후티 미사일 방어",
        }),
        ("Iran", EntityType.COUNTRY, "", ["이란"], {
            "역할": "방어측",
            "현황": "미사일 재고 소진 중, 호르무즈 통제 강화, 중국 선박 차단(3/27)",
            "변화": "하메네이 사망(2/28) → 모흐타바 하메네이 후계(3/8)",
        }),
        # 프록시
        ("Hezbollah", EntityType.PROXY, "", ["헤즈볼라", "히즈볼라"], {
            "역할": "이란 프록시, 대이스라엘 전선",
            "현황": "2024 전쟁으로 약화된 상태에서 재교전",
            "자금": "이란에서 연 $7억 지원",
        }),
        ("Houthis", EntityType.PROXY, "", ["후티", "안사르 알라"], {
            "역할": "이란 프록시, 홍해/이스라엘 전선",
            "현황": "3/28 이스라엘 향 탄도미사일 발사 — 공식 참전",
        }),
        ("Iraqi Shia Militias", EntityType.PROXY, "", ["시아파 민병대", "이라크 민병대", "PMF"], {
            "역할": "이란 프록시, 미군 기지 공격",
        }),
        ("Hamas", EntityType.PROXY, "", ["하마스"], {
            "역할": "이란 프록시, 가자 전선",
        }),
        ("Syria", EntityType.COUNTRY, "", ["시리아"], {
            "역할": "이란 보급로 (레바논 연결)",
            "현황": "아사드 정권 교체 후 불안정",
        }),
        # 동맹/기지 제공국
        ("Qatar", EntityType.COUNTRY, "", ["카타르"], {
            "역할": "미국 Al Udeid 공군기지 소재, LNG 수출 허브",
            "한국연결": "한국 헬륨가스 60-70% 카타르 수입 → 반도체 생산 위협",
        }),
        ("Bahrain", EntityType.COUNTRY, "", ["바레인"], {
            "역할": "미국 5함대 본부",
        }),
        ("UAE", EntityType.COUNTRY, "", ["아랍에미리트"], {
            "역할": "미국 군사 자산 소재, 석유 수출국",
        }),
        ("Saudi Arabia", EntityType.COUNTRY, "", ["사우디아라비아", "사우디"], {
            "역할": "미국 동맹, 석유 최대 수출국",
            "피해": "3/27 사우디 내 미 공군기지 공격으로 미군 부상",
        }),
        ("Jordan", EntityType.COUNTRY, "", ["요르단"], {
            "역할": "미국 동맹, 물류 거점",
        }),
        # 간접 영향국
        ("South Korea", EntityType.COUNTRY, "", ["한국", "대한민국"], {
            "경제영향": "유가 급등, 카타르 헬륨 수급 차질, 코스피 -12.06%",
            "최악시나리오": "유가 $150 → 성장률 -0.8%p, 물가 +2.9%p",
        }),
        ("China", EntityType.COUNTRY, "", ["중국"], {
            "입장": "중립 기조, 이란과 경제적 유대",
            "영향": "호르무즈 봉쇄 시 석유 수입 차질, 중국 선박 차단됨(3/27)",
        }),
        ("Japan", EntityType.COUNTRY, "", ["일본"], {
            "영향": "호르무즈 해협 의존도 높음 (석유 수입 80%+)",
        }),
        ("Russia", EntityType.COUNTRY, "", ["러시아"], {
            "입장": "이란과 군사/외교 협력, 직접 개입 회피",
        }),
        ("EU", EntityType.COUNTRY, "", ["유럽연합"], {
            "입장": "휴전 촉구, 인도적 지원",
        }),
        # 전략자산
        ("Strait of Hormuz", EntityType.ASSET, "", ["호르무즈 해협", "호르무즈"], {
            "일일통과량": "2,000만 배럴 (세계 해상 석유 교역 ~20%)",
            "봉쇄영향": "-1,000만 bpd (3/12 기준)",
        }),
        # 기관
        ("IRGC Quds Force", EntityType.INSTITUTION, "", ["IRGC 쿠드스군", "쿠드스군", "IRGC"], {
            "역할": "이란 해외 작전 총괄",
        }),
        # 원자재
        ("Crude Oil", EntityType.COMMODITY, "", ["원유", "유가", "Brent", "WTI"], {
            "현재가": "~$120/bbl",
            "전쟁전": "$75/bbl",
        }),
        ("Gold", EntityType.COMMODITY, "", ["금", "금값"], {
            "현재가": "$5,200+/oz",
            "변동": "안전자산 수요 폭증",
        }),
    ]

    # 기존 엔티티 확인 (name으로 dedup)
    entity_id_map: dict[str, str] = {}

    for name, etype, ticker, aliases, props in entities_data:
        existing = entity_repo.find_by_name(name)
        if existing:
            entity_id_map[name] = existing.id
            print(f"  SKIP: {name} (이미 존재)")
            continue

        entity = OntologyEntity(
            name=name,
            entity_type=etype,
            ticker=ticker,
            market=Market.US,
            aliases=aliases,
            properties=props,
        )
        entity_repo.create(entity)
        entity_id_map[name] = entity.id
        print(f"  ADD:  {name} [{etype}]")

    # ============================================================
    # 이벤트 등록
    # ============================================================
    events_data = [
        ("이란 전쟁 발발 (Operation Epic Fury + Roaring Lion)", EventType.WAR, Severity.CRITICAL,
         "2/28 미국+이스라엘, 이란 선제 공습. 하메네이 사망. 핵/군사 시설 타격."),
        ("호르무즈 해협 봉쇄 확대", EventType.MACRO, Severity.CRITICAL,
         "이란 호르무즈 해협 봉쇄 시도. 3/12 기준 -1,000만 bpd 차질. 세계 공급의 ~10%."),
        ("에너지 시설 공격 유예 (4/6 만료)", EventType.MILITARY, Severity.MAJOR,
         "미국 에너지 시설 공격 일시 중단. 4/6 유예 만료. 재개 시 유가 $150 시나리오."),
        ("후티 이스라엘 탄도미사일 발사 (3/28)", EventType.MILITARY, Severity.MAJOR,
         "후티, 이스라엘 Beer Sheva에 탄도미사일 발사. 예멘 전선 공식 참전."),
    ]

    event_id_list = []
    for title, etype, severity, summary in events_data:
        # title로 dedup
        existing = event_repo.get_many(filters={"title": title}, limit=1)
        if existing:
            event_id_list.append(existing[0].id)
            print(f"  SKIP: {title[:40]}... (이미 존재)")
            continue

        event = OntologyEvent(
            title=title,
            summary=summary,
            event_type=etype,
            severity=severity,
            market=Market.US,
            status=EventStatus.ESCALATING,
        )
        event_repo.create(event)
        event_id_list.append(event.id)
        print(f"  ADD:  {title[:50]}...")

    # ============================================================
    # 관계 등록
    # ============================================================
    links_data = [
        # 동맹
        ("United States", "Israel", LinkType.ALLY, "합동 공습 파트너 (Epic Fury + Roaring Lion)"),
        ("UAE", "United States", LinkType.ALLY, "미국 군사 자산 소재"),
        ("Saudi Arabia", "United States", LinkType.ALLY, "석유 최대 수출국, 미군 기지"),
        ("Jordan", "United States", LinkType.ALLY, "물류 거점"),
        # 적대
        ("United States", "Iran", LinkType.HOSTILE, "선제 공습 + 하메네이 제거"),
        ("Israel", "Iran", LinkType.HOSTILE, "합동 공습, 핵 시설 타격"),
        ("Israel", "Hezbollah", LinkType.HOSTILE, "레바논 전선 재교전"),
        # 기지 제공
        ("Qatar", "United States", LinkType.ALLY, "Al Udeid 공군기지 소재"),
        ("Bahrain", "United States", LinkType.ALLY, "미국 5함대 본부"),
        # 프록시
        ("Iran", "Hezbollah", LinkType.PROXY, "무기/자금 공급 (연 $7억)"),
        ("Iran", "Houthis", LinkType.PROXY, "미사일/드론 기술 지원"),
        ("Iran", "Iraqi Shia Militias", LinkType.PROXY, "IRGC 쿠드스군 지휘"),
        ("Iran", "Hamas", LinkType.PROXY, "자금/무기 지원"),
        # 보급
        ("Iran", "Syria", LinkType.SUPPLY, "헤즈볼라 보급로"),
        ("Syria", "Hezbollah", LinkType.SUPPLY, "시리아 경유 무기/물자 보급"),
        # 공격
        ("Iran", "Qatar", LinkType.HOSTILE, "이란 미사일 공격 대상"),
        ("Iran", "Bahrain", LinkType.HOSTILE, "이란 미사일 공격 대상"),
        ("Iran", "UAE", LinkType.HOSTILE, "이란 미사일/드론 공격 대상"),
        ("Iran", "Saudi Arabia", LinkType.HOSTILE, "3/27 미 공군기지 공격"),
        # 봉쇄
        ("Iran", "Strait of Hormuz", LinkType.IMPACTS, "호르무즈 해협 봉쇄 시도"),
        # 경제 의존
        ("South Korea", "Qatar", LinkType.TRADE, "헬륨가스 60-70% 수입"),
        ("China", "Strait of Hormuz", LinkType.TRADE, "석유 수입 의존"),
        ("Japan", "Strait of Hormuz", LinkType.TRADE, "석유 수입 80%+ 의존"),
        # 경제 영향
        ("Strait of Hormuz", "South Korea", LinkType.IMPACTS, "유가 급등 + 헬륨 수급 차질 → 반도체 위협"),
        ("Strait of Hormuz", "China", LinkType.IMPACTS, "석유 수입 차질, 선박 차단(3/27)"),
        ("Strait of Hormuz", "Japan", LinkType.IMPACTS, "에너지 비축 대응 필요"),
    ]

    link_count = 0
    for src_name, tgt_name, ltype, evidence in links_data:
        src_id = entity_id_map.get(src_name)
        tgt_id = entity_id_map.get(tgt_name)
        if not src_id or not tgt_id:
            print(f"  WARN: {src_name} → {tgt_name} 스킵 (엔티티 미발견)")
            continue

        # 중복 체크
        existing = link_repo.get_many(filters={
            "source_type": "entity", "source_id": src_id,
            "target_type": "entity", "target_id": tgt_id,
            "link_type": ltype.value,
        }, limit=1)
        if existing:
            continue

        link = OntologyLink(
            link_type=ltype,
            source_type="entity",
            source_id=src_id,
            target_type="entity",
            target_id=tgt_id,
            confidence=0.95,
            evidence=evidence,
        )
        link_repo.create(link)
        link_count += 1

    print(f"  → {link_count}개 관계 등록")

    # ============================================================
    # GeoIssue 등록
    # ============================================================
    existing_issues = issue_repo.get_many(filters={"title": "이란 전쟁"}, limit=1)
    if existing_issues:
        print(f"\n  SKIP: GeoIssue '이란 전쟁' 이미 존재 (id={existing_issues[0].id})")
    else:
        issue = GeoIssue(
            title="이란 전쟁",
            description="2026.2.28 미국+이스라엘 이란 선제 공습으로 시작된 전면전. "
                        "호르무즈 해협 봉쇄, 유가 $120+, 프록시 전선 확대.",
            severity=Severity.CRITICAL,
            status=GeoIssueStatus.ACTIVE,
            event_ids=event_id_list,
        )
        issue_repo.create(issue)
        print(f"\n  ADD: GeoIssue '이란 전쟁' (id={issue.id})")

    print("\n시딩 완료!")


if __name__ == "__main__":
    print("이란 전쟁 GeoIssue 시딩 시작...\n")
    seed()
