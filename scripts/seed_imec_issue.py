#!/usr/bin/env python3
"""IMEC (인도-중동-유럽 경제 회랑) 지정학 GeoIssue 시딩."""

from __future__ import annotations

import sys
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


def seed() -> None:
    init_db()
    e_repo = OntologyEntityRepository()
    ev_repo = OntologyEventRepository()
    l_repo = OntologyLinkRepository()
    i_repo = GeoIssueRepository()

    entities = [
        ("India", EntityType.COUNTRY, "", ["인도"], {
            "역할": "IMEC 동쪽 끝, 제조업 허브, 중국 대안 공급망",
        }),
        ("Saudi Arabia", EntityType.COUNTRY, "", ["사우디아라비아", "사우디"], {}),
        ("UAE", EntityType.COUNTRY, "", ["아랍에미리트"], {
            "역할": "IMEC 중동 허브, 물류 중심",
        }),
        ("Israel", EntityType.COUNTRY, "", ["이스라엘"], {
            "역할": "IMEC 하이파항 연결, 지중해 게이트웨이",
        }),
        ("Greece", EntityType.COUNTRY, "", ["그리스"], {
            "역할": "IMEC 유럽 상륙 지점, 피레우스항",
        }),
        ("Italy", EntityType.COUNTRY, "", ["이탈리아"], {
            "역할": "IMEC 유럽 종착지 후보",
        }),
        ("EU", EntityType.COUNTRY, "", ["유럽연합"], {}),
        ("United States", EntityType.COUNTRY, "", ["미국", "USA"], {}),
        ("China", EntityType.COUNTRY, "", ["중국"], {}),
        ("Iran", EntityType.COUNTRY, "", ["이란"], {}),
        ("Strait of Hormuz", EntityType.ASSET, "", ["호르무즈 해협"], {}),
        # IMEC 특유 엔티티
        ("IMEC Corridor", EntityType.ASSET, "", ["IMEC", "인도-중동-유럽 경제 회랑",
         "India-Middle East-Europe Economic Corridor"], {
            "발표": "2023 G20 뉴델리 정상회의",
            "구간": "인도 → UAE → 사우디 → 요르단 → 이스라엘 → 그리스 → EU",
            "목적": "중국 일대일로 대항, 서방 주도 무역 루트",
        }),
        ("Belt and Road Initiative", EntityType.ASSET, "", ["일대일로", "BRI", "One Belt One Road"], {
            "주도": "중국", "규모": "150+ 국가 참여",
        }),
        ("Haifa Port", EntityType.ASSET, "", ["하이파항", "Haifa"], {
            "역할": "IMEC 지중해 연결 항구, 이스라엘 최대 항구",
        }),
        ("Piraeus Port", EntityType.ASSET, "", ["피레우스항", "Piraeus"], {
            "역할": "IMEC 유럽 상륙 항구, 그리스 최대 항구",
            "소유": "중국 COSCO 지분 보유 → 지정학적 긴장",
        }),
        ("Suez Canal", EntityType.ASSET, "", ["수에즈 운하"], {
            "역할": "기존 아시아-유럽 해상 루트, IMEC의 대안 대상",
        }),
    ]

    eid = {}
    for name, etype, ticker, aliases, props in entities:
        existing = e_repo.find_by_name(name)
        if existing:
            eid[name] = existing.id
            print(f"  SKIP: {name}")
            continue
        e = OntologyEntity(name=name, entity_type=etype, ticker=ticker,
                           market=Market.US, aliases=aliases, properties=props)
        e_repo.create(e)
        eid[name] = e.id
        print(f"  ADD:  {name}")

    events = [
        ("IMEC 회랑 발표 (2023 G20)", EventType.DIPLOMATIC, Severity.CRITICAL,
         "2023 G20 뉴델리 정상회의에서 미국-인도-사우디-UAE-이스라엘-EU 공동 발표. "
         "중국 일대일로 대항 서방 주도 무역 회랑."),
        ("이란 전쟁으로 IMEC 차질", EventType.MILITARY, Severity.CRITICAL,
         "2026.2.28 이란 전쟁 발발 → 호르무즈 봉쇄 + 중동 불안정화. "
         "IMEC 핵심 경유지(사우디, UAE, 이스라엘) 전쟁 직접 영향권."),
        ("중국 일대일로 vs IMEC 경쟁", EventType.DIPLOMATIC, Severity.MAJOR,
         "중국 일대일로(BRI)와 서방 IMEC의 글로벌 인프라 패권 경쟁. "
         "피레우스항 중국 소유가 IMEC 유럽 상륙에 장애."),
    ]

    ev_ids = []
    for title, etype, sev, summary in events:
        existing = ev_repo.get_many(filters={"title": title}, limit=1)
        if existing:
            ev_ids.append(existing[0].id)
            continue
        ev = OntologyEvent(title=title, summary=summary, event_type=etype,
                           severity=sev, market=Market.US, status=EventStatus.DEVELOPING)
        ev_repo.create(ev)
        ev_ids.append(ev.id)
        print(f"  ADD:  {title[:50]}...")

    links = [
        # IMEC 참여국 관계
        ("United States", "IMEC Corridor", LinkType.ALLY, "IMEC 주도국, G20 발표"),
        ("India", "IMEC Corridor", LinkType.ALLY, "IMEC 동쪽 기점"),
        ("Saudi Arabia", "IMEC Corridor", LinkType.ALLY, "IMEC 중동 경유지"),
        ("UAE", "IMEC Corridor", LinkType.ALLY, "IMEC 중동 물류 허브"),
        ("Israel", "IMEC Corridor", LinkType.ALLY, "IMEC 지중해 연결"),
        ("EU", "IMEC Corridor", LinkType.ALLY, "IMEC 유럽 종착지"),
        # 이스라엘-하이파 연결
        ("Israel", "Haifa Port", LinkType.SUPPLY, "IMEC 지중해 연결 항구"),
        ("Haifa Port", "IMEC Corridor", LinkType.SUPPLY, "IMEC 핵심 인프라"),
        # 그리스-피레우스 연결
        ("Greece", "Piraeus Port", LinkType.SUPPLY, "IMEC 유럽 상륙 항구"),
        ("China", "Piraeus Port", LinkType.TRADE, "COSCO 지분 보유, 지정학 긴장"),
        # IMEC vs BRI 경쟁
        ("China", "Belt and Road Initiative", LinkType.ALLY, "일대일로 주도국"),
        ("IMEC Corridor", "Belt and Road Initiative", LinkType.HOSTILE, "글로벌 인프라 패권 경쟁"),
        # 이란 전쟁 영향
        ("Iran", "IMEC Corridor", LinkType.IMPACTS, "전쟁으로 중동 경유지 불안정화"),
        ("Strait of Hormuz", "IMEC Corridor", LinkType.IMPACTS, "호르무즈 봉쇄로 해상 물류 차질"),
        # 기존 루트 대체
        ("IMEC Corridor", "Suez Canal", LinkType.HOSTILE, "수에즈 우회 대안 루트"),
        # 인도-중국 경쟁
        ("India", "China", LinkType.HOSTILE, "제조업 공급망 경쟁, IMEC vs BRI"),
    ]

    cnt = 0
    for src, tgt, ltype, evidence in links:
        sid, tid = eid.get(src), eid.get(tgt)
        if not sid or not tid:
            print(f"  WARN: {src} → {tgt} 스킵")
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
                                    confidence=0.9, evidence=evidence))
        cnt += 1
    print(f"  → {cnt}개 관계")

    existing = i_repo.get_many(filters={"title": "IMEC 회랑"}, limit=1)
    if not existing:
        issue = GeoIssue(title="IMEC 회랑",
                         description="인도-중동-유럽 경제 회랑. 미국+인도+사우디+이스라엘+EU 주도. "
                                     "중국 일대일로 대항. 이란 전쟁으로 핵심 경유지 불안정화.",
                         severity=Severity.CRITICAL, status=GeoIssueStatus.ACTIVE,
                         event_ids=ev_ids)
        i_repo.create(issue)
        print(f"\n  ADD: GeoIssue 'IMEC 회랑'")
    print("\nIMEC 시딩 완료!")


if __name__ == "__main__":
    print("IMEC 지정학 시딩 시작...\n")
    seed()
