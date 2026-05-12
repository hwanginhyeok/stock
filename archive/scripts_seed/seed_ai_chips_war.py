#!/usr/bin/env python3
"""AI/반도체 패권전쟁 GeoIssue 시딩."""

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
        ("China", EntityType.COUNTRY, "", ["중국"], {}),
        ("Taiwan", EntityType.COUNTRY, "", ["대만"], {}),
        ("South Korea", EntityType.COUNTRY, "", ["한국"], {}),
        ("Japan", EntityType.COUNTRY, "", ["일본"], {}),
        ("Netherlands", EntityType.COUNTRY, "", ["네덜란드"], {
            "역할": "ASML 본사 소재국, 미국 수출통제 동참",
        }),
        # 기업
        ("TSMC", EntityType.COMPANY, "TSM", ["TSMC", "대만반도체"], {
            "역할": "세계 최대 파운드리, 첨단 칩 독점 생산",
            "CoWoS": "미국 AI칩 패키징 사실상 독점",
        }),
        ("Nvidia", EntityType.COMPANY, "NVDA", ["엔비디아"], {
            "역할": "AI GPU 시장 지배자 (H100/H200/Blackwell)",
        }),
        ("AMD", EntityType.COMPANY, "AMD", ["AMD"], {
            "역할": "AI GPU 2위 (MI300X/MI325X)",
        }),
        ("ASML", EntityType.COMPANY, "ASML", ["ASML"], {
            "역할": "EUV 노광기 세계 유일 공급사",
            "수출통제": "중국 향 EUV 판매 금지",
        }),
        ("Samsung Electronics", EntityType.COMPANY, "005930.KS", ["삼성전자"], {
            "역할": "파운드리 2위 + HBM 메모리 공급",
        }),
        ("SK Hynix", EntityType.COMPANY, "000660.KS", ["SK하이닉스"], {
            "역할": "HBM3E 시장 점유율 1위, Nvidia 핵심 공급사",
        }),
        ("Huawei", EntityType.COMPANY, "", ["화웨이"], {
            "역할": "Ascend 910C AI칩 자체 개발, 미국 제재 대상",
            "성능": "H100 대비 60% 추론 성능 (2026.2 기준)",
        }),
        ("Intel", EntityType.COMPANY, "INTC", ["인텔"], {
            "역할": "미국 파운드리 육성 대상, CHIPS Act 보조금",
        }),
        ("US Commerce Dept", EntityType.INSTITUTION, "", ["미국 상무부", "BIS"], {
            "역할": "반도체 수출통제 집행, Entity List 관리",
        }),
        ("CHIPS Act", EntityType.INSTITUTION, "", ["칩스법", "CHIPS and Science Act"], {
            "역할": "$527억 반도체 보조금, 미국 내 생산 유인",
        }),
        ("Broadcom", EntityType.COMPANY, "AVGO", ["브로드컴"], {
            "역할": "커스텀 AI칩 (Google TPU 생산), 네트워킹",
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
        ("미국 AI칩 수출통제 신규 규정", EventType.REGULATION, Severity.CRITICAL,
         "2026.1 상무부 신규 규정. H200 중국 판매 허용 but 100만개 cap. "
         "25% AI칩 관세. 3단계 국가 분류 (동맹/중립/제재).",
         "2026-01-15"),
        ("AI OVERWATCH Act 하원 통과", EventType.REGULATION, Severity.MAJOR,
         "2026.1 하원 외교위 통과. 첨단 반도체 수출을 무기급 통제로 격상. "
         "Blackwell 칩 2년간 적성국 판매 금지.",
         "2026-01-20"),
        ("Huawei Ascend 910C 성능 공개", EventType.MACRO, Severity.MAJOR,
         "2026.2 벤치마크. H100 추론 성능 60% 도달. "
         "중국 AI 자급 가속. 미국 수출통제 효과 의문.",
         "2026-02-15"),
        ("TSMC 미국 애리조나 팹 가동", EventType.MACRO, Severity.MAJOR,
         "TSMC Arizona Fab 2 가동 시작. 4nm 공정. "
         "미국 내 첨단칩 생산 첫 시작. CHIPS Act 보조금 투입.",
         "2025-12-01"),
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
        # 수출통제 (미국 → 중국 차단)
        ("US Commerce Dept", "Nvidia", LinkType.IMPACTS, "수출통제 규정으로 중국향 판매 제한"),
        ("US Commerce Dept", "AMD", LinkType.IMPACTS, "MI325X 중국향 판매 제한"),
        ("US Commerce Dept", "ASML", LinkType.IMPACTS, "EUV 중국 판매 금지 동참 요구"),
        ("US Commerce Dept", "Huawei", LinkType.HOSTILE, "Entity List, 수출 전면 금지"),
        ("United States", "China", LinkType.HOSTILE, "AI칩 수출통제, 디커플링 가속"),
        # 공급망
        ("TSMC", "Nvidia", LinkType.SUPPLY, "CoWoS 패키징 사실상 독점 공급"),
        ("TSMC", "AMD", LinkType.SUPPLY, "첨단 공정 파운드리"),
        ("TSMC", "Broadcom", LinkType.SUPPLY, "Google TPU 등 커스텀 칩 생산"),
        ("SK Hynix", "Nvidia", LinkType.SUPPLY, "HBM3E 핵심 공급사"),
        ("Samsung Electronics", "Nvidia", LinkType.SUPPLY, "HBM + 파운드리 공급"),
        ("ASML", "TSMC", LinkType.SUPPLY, "EUV 노광기 독점 공급"),
        ("ASML", "Samsung Electronics", LinkType.SUPPLY, "EUV 노광기 공급"),
        # 미국 자국 생산 육성
        ("CHIPS Act", "Intel", LinkType.SUPPLY, "파운드리 보조금 지원"),
        ("CHIPS Act", "TSMC", LinkType.SUPPLY, "애리조나 팹 보조금 지원"),
        ("CHIPS Act", "Samsung Electronics", LinkType.SUPPLY, "텍사스 팹 보조금 지원"),
        # 중국 자급 시도
        ("China", "Huawei", LinkType.ALLY, "Ascend 910C 자체 개발 지원"),
        ("Huawei", "Nvidia", LinkType.HOSTILE, "AI칩 경쟁자, 자급 대체 시도"),
        # 지정학적 리스크
        ("Taiwan", "TSMC", LinkType.SUPPLY, "TSMC 본사, 대만 해협 리스크"),
        ("China", "Taiwan", LinkType.HOSTILE, "군사 압박 지속, 통일 압력"),
        # 동맹 수출통제 협력
        ("Netherlands", "ASML", LinkType.IMPACTS, "정부 수출통제 동참, EUV 중국 판매 금지"),
        ("Japan", "United States", LinkType.ALLY, "반도체 장비 대중국 수출통제 동참"),
        ("South Korea", "United States", LinkType.ALLY, "반도체 동맹, but 중국 시장 의존"),
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
                                    confidence=0.9, evidence=evidence))
        cnt += 1
    print(f"  → {cnt}개 관계")

    existing = i_repo.get_many(filters={"title": "AI/반도체 패권전쟁"}, limit=1)
    if not existing:
        issue = GeoIssue(title="AI/반도체 패권전쟁",
                         description="미국 AI칩 수출통제 vs 중국 자급 시도. "
                                     "TSMC/Nvidia/ASML 공급망 지정학. Huawei Ascend 대항마. "
                                     "CHIPS Act 미국 내 생산 유인.",
                         severity=Severity.CRITICAL, status=GeoIssueStatus.ACTIVE,
                         event_ids=ev_ids, entity_ids=list(eid.values()))
        i_repo.create(issue)
        print(f"\n  ADD: GeoIssue 'AI/반도체 패권전쟁'")
    print("\nAI/반도체 시딩 완료!")


if __name__ == "__main__":
    print("AI/반도체 패권전쟁 시딩 시작...\n")
    seed()
