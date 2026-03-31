#!/usr/bin/env python3
"""트럼프 관세전쟁 2.0 GeoIssue 시딩."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.database import init_db
from src.core.models import (
    GeoIssue, GeoIssueStatus, OntologyEntity, OntologyEvent, OntologyLink,
    EntityType, EventType, EventStatus, LinkType, Severity, Market,
)
from src.storage import (
    GeoIssueRepository, OntologyEntityRepository,
    OntologyEventRepository, OntologyLinkRepository,
)

def _dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)

def seed() -> None:
    init_db()
    e_repo = OntologyEntityRepository()
    ev_repo = OntologyEventRepository()
    l_repo = OntologyLinkRepository()
    i_repo = GeoIssueRepository()

    entities = [
        ("United States", EntityType.COUNTRY, "", ["미국", "USA"], {}),
        ("China", EntityType.COUNTRY, "", ["중국"], {
            "관세현황": "총 145% → 대법원 판결 후 Section 301 전환 중",
        }),
        ("EU", EntityType.COUNTRY, "", ["유럽연합"], {
            "관세현황": "20% 상호관세 → 위헌 판결로 무효, 301조 조사 대상",
        }),
        ("South Korea", EntityType.COUNTRY, "", ["한국", "대한민국"], {
            "관세현황": "25% 상호관세 → 위헌, 301조 조사 대상 16개국 포함",
            "영향": "자동차·철강·반도체 수출 직격",
        }),
        ("Japan", EntityType.COUNTRY, "", ["일본"], {
            "관세현황": "24% 상호관세 → 위헌, 301조 조사 대상",
        }),
        ("Mexico", EntityType.COUNTRY, "", ["멕시코"], {
            "관세현황": "25% 관세, 펜타닐/이민 연계",
        }),
        ("Canada", EntityType.COUNTRY, "", ["캐나다"], {
            "관세현황": "25% 관세, USMCA 재협상 압박",
        }),
        ("India", EntityType.COUNTRY, "", ["인도"], {
            "관세현황": "26% 상호관세 → 위헌, 301조 조사 대상",
        }),
        ("Taiwan", EntityType.COUNTRY, "", ["대만"], {
            "관세현황": "32% 상호관세 → 위헌, 반도체 관세 별도",
        }),
        ("Vietnam", EntityType.COUNTRY, "", ["베트남"], {
            "관세현황": "46% 상호관세 → 위헌, 우회수출 단속 강화",
        }),
        ("US Supreme Court", EntityType.INSTITUTION, "", ["미국 대법원"], {
            "역할": "IEEPA 관세 위헌 판결 (2026.2.20), 6-3",
        }),
        ("USTR", EntityType.INSTITUTION, "", ["미국 무역대표부"], {
            "역할": "Section 301 조사 주도, 80개국 대상",
        }),
        ("WTO", EntityType.INSTITUTION, "", ["세계무역기구"], {
            "역할": "다자무역 규범, 관세전쟁으로 무력화 위기",
        }),
        ("US Auto Industry", EntityType.SECTOR, "", ["미국 자동차 산업"], {
            "영향": "25% 자동차 관세 유지, 부품 공급망 혼란",
        }),
        ("US Steel Industry", EntityType.SECTOR, "", ["미국 철강 산업"], {
            "영향": "25% 철강/알루미늄 관세 (Section 232, 유지)",
        }),
        ("Ecuador", EntityType.COUNTRY, "", ["에콰도르"], {
            "역할": "대법원 판결 후 최초 무역 협정 서명 (2026.3.13)",
        }),
    ]

    eid = {}
    for name, etype, ticker, aliases, props in entities:
        existing = e_repo.find_by_name(name)
        if existing:
            eid[name] = existing.id
        else:
            e = OntologyEntity(name=name, entity_type=etype, ticker=ticker,
                               market=Market.US, aliases=aliases, properties=props)
            e_repo.create(e)
            eid[name] = e.id
            print(f"  ADD:  {name}")

    events = [
        ("트럼프 상호관세 발효 (Liberation Day)", EventType.SANCTIONS, Severity.CRITICAL,
         "2025.4.2 '해방의 날' 상호관세 발효. 중국 145%, EU 20%, 한국 25%, 일본 24%.",
         "2025-04-02"),
        ("대법원 IEEPA 관세 위헌 판결 (6-3)", EventType.REGULATION, Severity.CRITICAL,
         "2026.2.20 대법원 6-3 판결. 상호관세 불법. $1,650억 환불 명령. Barrett·Gorsuch 찬성에 트럼프 격노.",
         "2026-02-20"),
        ("Section 122 임시 글로벌 관세 10%", EventType.SANCTIONS, Severity.MAJOR,
         "대법원 판결 직후 Section 122 발동. 150일 한정 글로벌 10% 관세. 의회 연장 필요.",
         "2026-02-20"),
        ("Section 301 조사 개시 (80개국)", EventType.REGULATION, Severity.CRITICAL,
         "2026.3.11 USTR, 80개국 대상 301조 조사 개시. 한국·중국·일본·인도·EU·멕시코 포함. 제조업 과잉생산 조사.",
         "2026-03-11"),
        ("에콰도르 무역 협정 서명", EventType.DIPLOMATIC, Severity.MODERATE,
         "2026.3.13 대법원 판결 후 첫 무역 협정. 새 관세 전략의 템플릿.",
         "2026-03-13"),
    ]

    ev_ids = []
    for title, etype, sev, summary, date_str in events:
        existing = ev_repo.get_many(filters={"title": title}, limit=1)
        if existing:
            ev_ids.append(existing[0].id)
            continue
        ev = OntologyEvent(title=title, summary=summary, event_type=etype,
                           severity=sev, market=Market.US, status=EventStatus.DEVELOPING,
                           started_at=_dt(date_str))
        ev_repo.create(ev)
        ev_ids.append(ev.id)
        print(f"  ADD:  {title[:50]}...")

    links = [
        # 관세 부과 관계 (US → 대상국)
        ("United States", "China", LinkType.SANCTIONS, "145% 관세 → 대법원 위헌 → 301조 전환"),
        ("United States", "EU", LinkType.SANCTIONS, "20% 상호관세 → 위헌, 301조 조사 대상"),
        ("United States", "South Korea", LinkType.SANCTIONS, "25% 상호관세 → 위헌, 301조 조사 대상"),
        ("United States", "Japan", LinkType.SANCTIONS, "24% 상호관세 → 위헌, 301조 조사 대상"),
        ("United States", "Mexico", LinkType.SANCTIONS, "25% 관세, 펜타닐/이민 연계"),
        ("United States", "Canada", LinkType.SANCTIONS, "25% 관세, USMCA 재협상 압박"),
        ("United States", "India", LinkType.SANCTIONS, "26% 상호관세 → 위헌, 301조 조사 대상"),
        ("United States", "Taiwan", LinkType.SANCTIONS, "32% 상호관세 → 위헌, 반도체 관세 별도"),
        ("United States", "Vietnam", LinkType.SANCTIONS, "46% 상호관세 → 위헌, 우회수출 단속"),
        # 제도적 견제
        ("US Supreme Court", "United States", LinkType.IMPACTS, "IEEPA 관세 위헌 판결 6-3"),
        ("USTR", "China", LinkType.HOSTILE, "Section 301 조사 주도"),
        ("USTR", "South Korea", LinkType.IMPACTS, "301조 조사 대상 16개국 포함"),
        # 보복/대응
        ("China", "United States", LinkType.SANCTIONS, "보복 관세 + 희토류 수출 제한"),
        ("EU", "United States", LinkType.SANCTIONS, "보복 관세 준비"),
        # 무역 규범 영향
        ("United States", "WTO", LinkType.HOSTILE, "다자무역 규범 무시, 일방적 관세"),
        # 협정
        ("United States", "Ecuador", LinkType.ALLY, "대법원 판결 후 첫 무역 협정 서명"),
        # 산업 영향
        ("United States", "US Auto Industry", LinkType.IMPACTS, "25% 자동차 관세 유지"),
        ("United States", "US Steel Industry", LinkType.IMPACTS, "25% 철강 관세 (Section 232)"),
        # 한국 구체적 영향
        ("South Korea", "US Auto Industry", LinkType.TRADE, "현대·기아 미국 수출 직격"),
    ]

    cnt = 0
    for src, tgt, ltype, evidence in links:
        sid, tid = eid.get(src), eid.get(tgt)
        if not sid or not tid:
            continue
        existing = l_repo.get_many(filters={
            "source_type": "entity", "source_id": sid,
            "target_type": "entity", "target_id": tid,
            "link_type": ltype.value,
        }, limit=1)
        if existing:
            continue
        l_repo.create(OntologyLink(link_type=ltype, source_type="entity", source_id=sid,
                                    target_type="entity", target_id=tid,
                                    confidence=0.95, evidence=evidence))
        cnt += 1
    print(f"  → {cnt}개 관계")

    existing = i_repo.get_many(filters={"title": "트럼프 관세전쟁 2.0"}, limit=1)
    if not existing:
        issue = GeoIssue(title="트럼프 관세전쟁 2.0",
                         description="2025.4.2 상호관세 발효 → 2026.2.20 대법원 위헌 판결 → "
                                     "Section 301 조사로 전환. 80개국 대상, 한국 포함.",
                         severity=Severity.CRITICAL, status=GeoIssueStatus.ACTIVE,
                         event_ids=ev_ids, entity_ids=list(eid.values()))
        i_repo.create(issue)
        print(f"\n  ADD: GeoIssue '트럼프 관세전쟁 2.0'")
    print("\n관세전쟁 시딩 완료!")


if __name__ == "__main__":
    print("트럼프 관세전쟁 2.0 시딩 시작...\n")
    seed()
