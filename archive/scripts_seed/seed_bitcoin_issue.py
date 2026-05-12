#!/usr/bin/env python3
"""비트코인 지정학 GeoIssue 시딩."""

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
        ("Bitcoin", EntityType.COMMODITY, "BTC", ["비트코인", "BTC"], {
            "현재가": "~$87,000", "성격": "디지털 금, 희소성 자산",
        }),
        ("Ethereum", EntityType.COMMODITY, "ETH", ["이더리움", "ETH"], {
            "현재가": "~$2,000", "성격": "탈중앙화 플랫폼",
        }),
        ("United States", EntityType.COUNTRY, "", ["미국", "USA"], {}),
        ("US SEC", EntityType.INSTITUTION, "", ["미국 증권거래위원회", "SEC"], {
            "역할": "크립토 규제 주도 기관",
        }),
        ("US Treasury", EntityType.INSTITUTION, "", ["미국 재무부"], {
            "역할": "스테이블코인 규제, 제재 집행",
        }),
        ("China", EntityType.COUNTRY, "", ["중국"], {
            "입장": "2021 크립토 전면 금지, CBDC(디지털 위안) 추진",
        }),
        ("El Salvador", EntityType.COUNTRY, "", ["엘살바도르"], {
            "역할": "세계 최초 비트코인 법정통화 채택 (2021)",
        }),
        ("MicroStrategy", EntityType.COMPANY, "MSTR", ["마이크로스트래티지"], {
            "보유량": "BTC 500,000+ 개", "역할": "기업 비트코인 최대 보유",
        }),
        ("Coinbase", EntityType.COMPANY, "COIN", ["코인베이스"], {
            "역할": "미국 최대 크립토 거래소, SEC 소송 대상",
        }),
        ("Tether", EntityType.COMPANY, "", ["테더", "USDT"], {
            "역할": "최대 스테이블코인 발행사",
        }),
        ("Circle", EntityType.COMPANY, "", ["서클", "USDC"], {
            "역할": "USDC 발행사, 디지털 달러 인프라",
        }),
        ("Russia", EntityType.COUNTRY, "", ["러시아"], {
            "입장": "제재 우회 수단으로 크립토 활용, 채굴 허용",
        }),
        ("EU", EntityType.COUNTRY, "", ["유럽연합"], {
            "규제": "MiCA (Markets in Crypto-Assets) 시행",
        }),
        ("South Korea", EntityType.COUNTRY, "", ["한국", "대한민국"], {
            "규제": "가상자산이용자보호법, 거래소 규제 강화",
        }),
        ("Japan", EntityType.COUNTRY, "", ["일본"], {
            "입장": "Web3 친화 정책, 스테이블코인 규제 프레임워크",
        }),
        ("Digital Yuan", EntityType.COMMODITY, "", ["디지털 위안", "e-CNY", "CBDC"], {
            "역할": "중국 중앙은행 디지털화폐, 달러 패권 도전",
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
        ("비트코인 ETF 승인 + 기관 자금 유입", EventType.REGULATION, Severity.CRITICAL,
         "2024 비트코인 현물 ETF 승인 → 기관 자금 대거 유입. 2025 이더리움 ETF 승인."),
        ("미국 크립토 규제 전쟁 (SEC vs 업계)", EventType.REGULATION, Severity.MAJOR,
         "SEC의 Coinbase/Binance 소송. 스테이블코인 규제 법안 추진."),
        ("CBDC 경쟁 — 디지털 위안 vs 디지털 달러", EventType.DIPLOMATIC, Severity.MAJOR,
         "중국 디지털 위안 국제화 시도. 미국 디지털 달러 대응. 달러 패권 경쟁."),
        ("러시아 제재 우회 크립토 활용", EventType.SANCTIONS, Severity.MODERATE,
         "러시아 제재 우회 수단으로 크립토 활용. 미국/EU 대응 강화."),
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
        ("US SEC", "Coinbase", LinkType.HOSTILE, "SEC 소송 진행 중"),
        ("US SEC", "Bitcoin", LinkType.IMPACTS, "ETF 승인으로 기관 자금 유입"),
        ("United States", "Bitcoin", LinkType.IMPACTS, "규제 환경이 가격에 직접 영향"),
        ("China", "Bitcoin", LinkType.HOSTILE, "2021 채굴+거래 전면 금지"),
        ("China", "Digital Yuan", LinkType.SUPPLY, "CBDC 개발 및 국제화 추진"),
        ("Digital Yuan", "Bitcoin", LinkType.HOSTILE, "CBDC가 크립토 대체 시도"),
        ("El Salvador", "Bitcoin", LinkType.ALLY, "법정통화 채택, 국가 보유"),
        ("MicroStrategy", "Bitcoin", LinkType.TRADE, "500,000+ BTC 보유"),
        ("Coinbase", "Bitcoin", LinkType.TRADE, "미국 최대 거래소"),
        ("Tether", "Bitcoin", LinkType.SUPPLY, "USDT 크립토 시장 유동성 공급"),
        ("Circle", "United States", LinkType.ALLY, "디지털 달러 인프라 파트너"),
        ("Russia", "Bitcoin", LinkType.TRADE, "제재 우회 수단 활용"),
        ("EU", "Bitcoin", LinkType.IMPACTS, "MiCA 규제 시행"),
        ("South Korea", "Bitcoin", LinkType.IMPACTS, "가상자산이용자보호법 시행"),
        ("Japan", "Bitcoin", LinkType.ALLY, "Web3 친화 정책"),
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

    existing = i_repo.get_many(filters={"title": "비트코인 지정학"}, limit=1)
    if not existing:
        issue = GeoIssue(title="비트코인 지정학",
                         description="크립토 규제 전쟁, CBDC 경쟁, 제재 우회, "
                                     "ETF 기관 자금 유입 — 비트코인을 둘러싼 글로벌 지정학.",
                         severity=Severity.MAJOR, status=GeoIssueStatus.ACTIVE,
                         event_ids=ev_ids)
        i_repo.create(issue)
        print(f"\n  ADD: GeoIssue '비트코인 지정학'")
    print("\n비트코인 시딩 완료!")


if __name__ == "__main__":
    print("비트코인 지정학 시딩 시작...\n")
    seed()
