#!/usr/bin/env python3
"""야간작업: 5개 신규 이슈 + 10개 핫 종목 시딩.

신규 이슈:
  6. 러시아-우크라이나 전쟁
  7. 대만 해협 위기
  8. 유럽 정치 위기
  9. 글로벌 AI 규제 경쟁
  10. 일본 금리 전환 (BOJ)

핫 종목 (US 5 + KR 5):
  NVDA, TSLA, PLTR, LMT, XOM
  삼성전자, SK하이닉스, 한화에어로스페이스, 현대차, HD현대
"""

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


def _get_or_create_entity(repo, name, etype, ticker="", aliases=None, props=None):
    existing = repo.find_by_name(name)
    if existing:
        return existing.id
    e = OntologyEntity(name=name, entity_type=etype, ticker=ticker,
                       market=Market.US, aliases=aliases or [], properties=props or {})
    repo.create(e)
    print(f"    ADD entity: {name}")
    return e.id


def _create_event(repo, title, etype, sev, summary, date_str):
    existing = repo.get_many(filters={"title": title}, limit=1)
    if existing:
        return existing[0].id
    ev = OntologyEvent(title=title, summary=summary, event_type=etype,
                       severity=sev, market=Market.US, status=EventStatus.DEVELOPING,
                       started_at=_dt(date_str))
    repo.create(ev)
    print(f"    ADD event: {title[:50]}...")
    return ev.id


def _create_link(repo, src_id, tgt_id, ltype, evidence, issue_id):
    if not src_id or not tgt_id:
        return
    existing = repo.get_many(filters={
        "source_type": "entity", "source_id": src_id,
        "target_type": "entity", "target_id": tgt_id,
        "link_type": ltype.value, "geo_issue_id": issue_id,
    }, limit=1)
    if existing:
        return
    repo.create(OntologyLink(
        link_type=ltype, source_type="entity", source_id=src_id,
        target_type="entity", target_id=tgt_id,
        confidence=0.9, evidence=evidence, geo_issue_id=issue_id,
    ))


def seed_hot_stocks(e_repo):
    """핫 종목 10개 엔티티 등록."""
    print("\n=== 핫 종목 시딩 ===")
    stocks = [
        # US
        ("Tesla", EntityType.COMPANY, "TSLA", ["테슬라"], {
            "시총": "~$800B", "테마": "자율주행, 에너지, 로보틱스, TeraFab",
        }),
        ("Palantir", EntityType.COMPANY, "PLTR", ["팔란티어"], {
            "시총": "~$250B", "테마": "AI 플랫폼, 국방/정보기관, AIP",
        }),
        ("Lockheed Martin", EntityType.COMPANY, "LMT", ["록히드마틴"], {
            "테마": "방산 1위, F-35, 미사일 방어, 이란 전쟁 수혜",
        }),
        ("ExxonMobil", EntityType.COMPANY, "XOM", ["엑슨모빌"], {
            "테마": "석유 메이저, 유가 수혜, 이란 전쟁 영향",
        }),
        # KR
        ("Hanwha Aerospace", EntityType.COMPANY, "012450.KS", ["한화에어로스페이스", "한화에어로"], {
            "테마": "K-방산, 자주포/장갑차, 글로벌 수주 급증",
        }),
        ("Hyundai Motor", EntityType.COMPANY, "005380.KS", ["현대차", "현대자동차"], {
            "테마": "미국 관세 직격, 조지아 팹 건설 중",
        }),
        ("HD Hyundai", EntityType.COMPANY, "267250.KS", ["HD현대"], {
            "테마": "조선/해양, 호르무즈 우회 해운 수혜",
        }),
    ]
    eid = {}
    for name, etype, ticker, aliases, props in stocks:
        eid[name] = _get_or_create_entity(e_repo, name, etype, ticker, aliases, props)
    # 이미 있는 종목
    for name in ["Nvidia", "Samsung Electronics", "SK Hynix", "TSMC"]:
        e = e_repo.find_by_name(name)
        if e:
            eid[name] = e.id
    return eid


def seed_russia_ukraine(e_repo, ev_repo, l_repo, i_repo):
    """6. 러시아-우크라이나 전쟁."""
    print("\n=== 6. 러시아-우크라이나 전쟁 ===")
    eid = {}
    entities = [
        ("Russia", EntityType.COUNTRY, "", ["러시아"], {"입장": "우크라이나 침공 지속, 에너지 무기화"}),
        ("Ukraine", EntityType.COUNTRY, "", ["우크라이나"], {"입장": "NATO 가입 목표, 영토 탈환 작전"}),
        ("NATO", EntityType.INSTITUTION, "", ["나토", "북대서양조약기구"], {"역할": "우크라이나 무기 지원, 동유럽 방어 강화"}),
        ("EU", EntityType.COUNTRY, "", ["유럽연합"], {}),
        ("United States", EntityType.COUNTRY, "", ["미국"], {}),
        ("China", EntityType.COUNTRY, "", ["중국"], {}),
        ("North Korea", EntityType.COUNTRY, "", ["북한"], {"역할": "러시아에 병력+탄약 지원"}),
        ("Natural Gas", EntityType.COMMODITY, "", ["천연가스", "LNG"], {"영향": "유럽 에너지 위기 핵심"}),
        ("Wheat", EntityType.COMMODITY, "", ["밀", "곡물"], {"영향": "흑해 곡물 수출 차질"}),
    ]
    for name, etype, ticker, aliases, props in entities:
        eid[name] = _get_or_create_entity(e_repo, name, etype, ticker, aliases, props)

    ev_ids = [
        _create_event(ev_repo, "러시아 우크라이나 전면 침공", EventType.WAR, Severity.CRITICAL,
                       "2022.2.24 러시아 전면 침공. 3년 차 장기전.", "2022-02-24"),
        _create_event(ev_repo, "트럼프 종전 협상 시도", EventType.DIPLOMATIC, Severity.MAJOR,
                       "2026 트럼프 러-우 종전 딜 추진. 우크라이나 영토 양보 압박 논란.", "2026-01-15"),
        _create_event(ev_repo, "에너지 인프라 상호 공격 격화", EventType.MILITARY, Severity.MAJOR,
                       "양측 에너지 인프라 집중 타격. 유럽 천연가스 가격 불안.", "2025-12-01"),
    ]

    issue = _create_issue(i_repo, "러시아-우크라이나 전쟁",
        "2022 러시아 침공 → 3년 차 장기전. 에너지/곡물 공급 충격, NATO 확대, 트럼프 종전 딜.",
        Severity.CRITICAL, ev_ids, list(eid.values()))

    links = [
        ("Russia", "Ukraine", LinkType.HOSTILE, "전면 침공 지속"),
        ("NATO", "Ukraine", LinkType.ALLY, "무기·정보·훈련 지원"),
        ("United States", "Ukraine", LinkType.ALLY, "군사 원조 최대 공여국"),
        ("EU", "Ukraine", LinkType.ALLY, "경제 제재 + 재건 지원"),
        ("EU", "Russia", LinkType.SANCTIONS, "에너지·금융·기술 제재"),
        ("United States", "Russia", LinkType.SANCTIONS, "포괄적 경제 제재"),
        ("North Korea", "Russia", LinkType.ALLY, "병력+탄약 지원, 무기 거래"),
        ("China", "Russia", LinkType.TRADE, "석유·가스 할인 구매, 전략적 협력"),
        ("Russia", "Natural Gas", LinkType.SUPPLY, "유럽 가스 공급 무기화"),
        ("Russia", "Wheat", LinkType.SUPPLY, "흑해 곡물 수출 통제"),
    ]
    for src, tgt, lt, ev in links:
        _create_link(l_repo, eid.get(src), eid.get(tgt), lt, ev, issue)


def seed_taiwan_strait(e_repo, ev_repo, l_repo, i_repo):
    """7. 대만 해협 위기."""
    print("\n=== 7. 대만 해협 위기 ===")
    eid = {}
    entities = [
        ("China", EntityType.COUNTRY, "", ["중국"], {}),
        ("Taiwan", EntityType.COUNTRY, "", ["대만"], {}),
        ("United States", EntityType.COUNTRY, "", ["미국"], {}),
        ("Japan", EntityType.COUNTRY, "", ["일본"], {}),
        ("South Korea", EntityType.COUNTRY, "", ["한국"], {}),
        ("TSMC", EntityType.COMPANY, "TSM", ["TSMC"], {}),
        ("Nvidia", EntityType.COMPANY, "NVDA", ["엔비디아"], {}),
        ("Taiwan Strait", EntityType.ASSET, "", ["대만 해협", "타이완 해협"], {
            "역할": "세계 무역 핵심 항로, 연간 $5.3조 물동량",
        }),
    ]
    for name, etype, ticker, aliases, props in entities:
        eid[name] = _get_or_create_entity(e_repo, name, etype, ticker, aliases, props)

    ev_ids = [
        _create_event(ev_repo, "중국 대만 군사 압박 지속", EventType.MILITARY, Severity.MAJOR,
                       "PLA 해협 순찰 일상화, 군사훈련 규모 확대. 2027 시진핑 통일 시한설.", "2025-01-01"),
        _create_event(ev_repo, "TSMC 지정학 리스크 부각", EventType.MACRO, Severity.CRITICAL,
                       "세계 첨단칩 90%+ TSMC 생산. 대만 유사시 글로벌 반도체 공급 붕괴.", "2025-06-01"),
    ]

    issue = _create_issue(i_repo, "대만 해협 위기",
        "중국 군사 압박 + TSMC 집중 리스크. 유사시 세계 반도체 공급 붕괴.",
        Severity.CRITICAL, ev_ids, list(eid.values()))

    links = [
        ("China", "Taiwan", LinkType.HOSTILE, "군사 압박, 통일 압력"),
        ("United States", "Taiwan", LinkType.ALLY, "대만관계법, 무기 판매"),
        ("Japan", "Taiwan", LinkType.ALLY, "유사시 미일동맹 개입"),
        ("Taiwan", "TSMC", LinkType.SUPPLY, "TSMC 본사, 첨단 팹 집중"),
        ("TSMC", "Nvidia", LinkType.SUPPLY, "AI칩 CoWoS 독점 생산"),
        ("China", "Taiwan Strait", LinkType.HOSTILE, "해협 봉쇄 위협"),
        ("Taiwan Strait", "South Korea", LinkType.IMPACTS, "무역 항로 차단 시 수출 마비"),
    ]
    for src, tgt, lt, ev in links:
        _create_link(l_repo, eid.get(src), eid.get(tgt), lt, ev, issue)


def seed_eu_crisis(e_repo, ev_repo, l_repo, i_repo):
    """8. 유럽 정치 위기."""
    print("\n=== 8. 유럽 정치 위기 ===")
    eid = {}
    entities = [
        ("France", EntityType.COUNTRY, "", ["프랑스"], {"현황": "약한 정부, 극우·극좌 공격"}),
        ("Germany", EntityType.COUNTRY, "", ["독일"], {"현황": "연립 붕괴 후 소수 정부"}),
        ("United Kingdom", EntityType.COUNTRY, "", ["영국", "UK"], {"현황": "경제 침체, 이민 논란"}),
        ("EU", EntityType.COUNTRY, "", ["유럽연합"], {}),
        ("Russia", EntityType.COUNTRY, "", ["러시아"], {}),
        ("Euro", EntityType.COMMODITY, "", ["유로", "EUR"], {"영향": "정치 불안 → 유로 약세"}),
    ]
    for name, etype, ticker, aliases, props in entities:
        eid[name] = _get_or_create_entity(e_repo, name, etype, ticker, aliases, props)

    ev_ids = [
        _create_event(ev_repo, "프랑스 극우 약진 + 정치 마비", EventType.MACRO, Severity.MAJOR,
                       "르펜 세력 의회 확대. 마크롱 레임덕. 재정 정책 마비.", "2025-07-01"),
        _create_event(ev_repo, "독일 연립 붕괴 + 경기 침체", EventType.MACRO, Severity.MAJOR,
                       "연립정부 붕괴. 제조업 경쟁력 약화. 중국 의존 탈피 시도.", "2025-11-01"),
        _create_event(ev_repo, "러시아 유럽 하이브리드전 격화", EventType.MILITARY, Severity.MAJOR,
                       "사이버공격, 가짜뉴스, 에너지 압박. 우크라이나 지원 의지 약화 시도.", "2025-01-01"),
    ]

    issue = _create_issue(i_repo, "유럽 정치 위기",
        "프랑스·독일·영국 약한 정부. 극우 약진 + 러시아 하이브리드전. EU 결속 약화.",
        Severity.MAJOR, ev_ids, list(eid.values()))

    links = [
        ("Russia", "EU", LinkType.HOSTILE, "하이브리드전 — 사이버, 에너지, 가짜뉴스"),
        ("France", "EU", LinkType.ALLY, "EU 핵심국 but 정치 마비"),
        ("Germany", "EU", LinkType.ALLY, "EU 경제 엔진 but 침체"),
        ("United Kingdom", "EU", LinkType.TRADE, "브렉시트 후 새 무역 관계"),
        ("Russia", "France", LinkType.HOSTILE, "극우 세력 지원 의혹"),
        ("Russia", "Germany", LinkType.HOSTILE, "에너지 의존 탈피 강요"),
    ]
    for src, tgt, lt, ev in links:
        _create_link(l_repo, eid.get(src), eid.get(tgt), lt, ev, issue)


def seed_ai_regulation(e_repo, ev_repo, l_repo, i_repo):
    """9. 글로벌 AI 규제 경쟁."""
    print("\n=== 9. 글로벌 AI 규제 경쟁 ===")
    eid = {}
    entities = [
        ("EU", EntityType.COUNTRY, "", ["유럽연합"], {}),
        ("United States", EntityType.COUNTRY, "", ["미국"], {}),
        ("China", EntityType.COUNTRY, "", ["중국"], {}),
        ("United Kingdom", EntityType.COUNTRY, "", ["영국"], {}),
        ("OpenAI", EntityType.COMPANY, "", ["오픈AI"], {"역할": "GPT 시리즈, AI 선두 주자"}),
        ("Google DeepMind", EntityType.COMPANY, "GOOGL", ["구글 딥마인드"], {"역할": "Gemini, AI 연구"}),
        ("Anthropic", EntityType.COMPANY, "", ["앤트로픽"], {"역할": "Claude, AI 안전 연구"}),
        ("Meta AI", EntityType.COMPANY, "META", ["메타 AI"], {"역할": "Llama 오픈소스, AI 민주화"}),
        ("EU AI Act", EntityType.INSTITUTION, "", ["EU AI법"], {"역할": "세계 최초 포괄적 AI 규제법"}),
    ]
    for name, etype, ticker, aliases, props in entities:
        eid[name] = _get_or_create_entity(e_repo, name, etype, ticker, aliases, props)

    ev_ids = [
        _create_event(ev_repo, "EU AI Act 시행", EventType.REGULATION, Severity.CRITICAL,
                       "2024.8 발효, 2026 본격 시행. 고위험 AI 분류 + 벌금 체계.", "2024-08-01"),
        _create_event(ev_repo, "미국 AI 행정명령 vs 규제 완화", EventType.REGULATION, Severity.MAJOR,
                       "바이든 AI 행정명령 → 트럼프 폐기. 규제 완화 vs 안전 논쟁.", "2025-01-20"),
        _create_event(ev_repo, "중국 AI 규제 독자 노선", EventType.REGULATION, Severity.MAJOR,
                       "생성형 AI 서비스 규제. 사회주의 가치 준수 요구. DeepSeek 부상.", "2023-08-15"),
    ]

    issue = _create_issue(i_repo, "글로벌 AI 규제 경쟁",
        "EU 규제 선도 vs 미국 완화 vs 중국 독자 노선. AI 기업 글로벌 전략 좌우.",
        Severity.MAJOR, ev_ids, list(eid.values()))

    links = [
        ("EU AI Act", "OpenAI", LinkType.IMPACTS, "고위험 AI 분류 규제 적용"),
        ("EU AI Act", "Google DeepMind", LinkType.IMPACTS, "EU 내 서비스 규제"),
        ("EU AI Act", "Meta AI", LinkType.IMPACTS, "오픈소스 AI 규제 면제 논쟁"),
        ("United States", "OpenAI", LinkType.ALLY, "트럼프 규제 완화, AI 패권 지원"),
        ("United States", "Anthropic", LinkType.ALLY, "AI 안전 연구 지원"),
        ("China", "OpenAI", LinkType.HOSTILE, "중국 내 서비스 차단"),
        ("EU", "United States", LinkType.HOSTILE, "AI 규제 접근법 충돌"),
        ("China", "United States", LinkType.HOSTILE, "AI 패권 경쟁"),
    ]
    for src, tgt, lt, ev in links:
        _create_link(l_repo, eid.get(src), eid.get(tgt), lt, ev, issue)


def seed_boj_shift(e_repo, ev_repo, l_repo, i_repo):
    """10. 일본 금리 전환 (BOJ)."""
    print("\n=== 10. 일본 금리 전환 ===")
    eid = {}
    entities = [
        ("Japan", EntityType.COUNTRY, "", ["일본"], {}),
        ("Bank of Japan", EntityType.INSTITUTION, "", ["일본은행", "BOJ"], {
            "역할": "마이너스 금리 종료 → 금리 인상 전환",
        }),
        ("Japanese Yen", EntityType.COMMODITY, "", ["엔화", "JPY", "엔"], {
            "현황": "캐리 트레이드 역전 리스크",
        }),
        ("United States", EntityType.COUNTRY, "", ["미국"], {}),
        ("US Federal Reserve", EntityType.INSTITUTION, "", ["미국 연준", "Fed", "연준"], {}),
        ("South Korea", EntityType.COUNTRY, "", ["한국"], {}),
        ("Nikkei 225", EntityType.ASSET, "", ["닛케이", "일본 증시"], {}),
    ]
    for name, etype, ticker, aliases, props in entities:
        eid[name] = _get_or_create_entity(e_repo, name, etype, ticker, aliases, props)

    ev_ids = [
        _create_event(ev_repo, "BOJ 마이너스 금리 종료", EventType.MACRO, Severity.CRITICAL,
                       "2024.3 마이너스 금리 17년 만에 종료. 2025-26 추가 인상.", "2024-03-19"),
        _create_event(ev_repo, "엔 캐리 트레이드 역전 충격", EventType.MACRO, Severity.CRITICAL,
                       "2024.8 엔 급등 → 글로벌 캐리 트레이드 청산 → 증시 급락.", "2024-08-05"),
        _create_event(ev_repo, "BOJ 추가 금리 인상 관측", EventType.MACRO, Severity.MAJOR,
                       "2026 BOJ 추가 인상 시 엔 캐리 재청산 우려. 글로벌 유동성 영향.", "2026-01-01"),
    ]

    issue = _create_issue(i_repo, "일본 금리 전환 (BOJ)",
        "BOJ 마이너스 금리 종료 → 엔 캐리 트레이드 역전 리스크. 글로벌 유동성 충격 가능.",
        Severity.MAJOR, ev_ids, list(eid.values()))

    links = [
        ("Bank of Japan", "Japanese Yen", LinkType.IMPACTS, "금리 인상 → 엔화 강세"),
        ("Japanese Yen", "Nikkei 225", LinkType.IMPACTS, "엔 강세 → 수출주 약세 → 닛케이 하락"),
        ("Bank of Japan", "US Federal Reserve", LinkType.HOSTILE, "금리 정책 방향 반대 (BOJ 인상 vs Fed 인하)"),
        ("Japanese Yen", "South Korea", LinkType.IMPACTS, "엔 강세 → 한국 수출 경쟁력 변화"),
        ("Japan", "United States", LinkType.TRADE, "미일 금리차 축소 → 자본 흐름 변화"),
    ]
    for src, tgt, lt, ev in links:
        _create_link(l_repo, eid.get(src), eid.get(tgt), lt, ev, issue)


def seed_stock_issue_links(e_repo, l_repo, i_repo, stock_ids):
    """핫 종목을 관련 이슈에 연결."""
    print("\n=== 핫 종목 ↔ 이슈 연결 ===")

    # 이슈 ID 조회
    issues = {}
    for title in ["이란 전쟁", "트럼프 관세전쟁 2.0", "AI/반도체 패권전쟁",
                   "러시아-우크라이나 전쟁", "대만 해협 위기"]:
        found = i_repo.get_many(filters={"title": title}, limit=1)
        if found:
            issues[title] = found[0].id

    # 종목-이슈 관계
    stock_links = [
        # 이란 전쟁
        ("Lockheed Martin", "이란 전쟁", LinkType.TRADE, "방산 수주 급증, 미사일 공급"),
        ("ExxonMobil", "이란 전쟁", LinkType.TRADE, "유가 $120+ 수혜"),
        ("Hanwha Aerospace", "이란 전쟁", LinkType.TRADE, "K-방산 글로벌 수주 증가"),
        ("HD Hyundai", "이란 전쟁", LinkType.TRADE, "호르무즈 우회 → 해운 수요 급증"),
        # 관세전쟁
        ("Hyundai Motor", "트럼프 관세전쟁 2.0", LinkType.IMPACTS, "25% 자동차 관세 직격"),
        ("Tesla", "트럼프 관세전쟁 2.0", LinkType.IMPACTS, "부품 관세 영향, 미국 내 생산 우위"),
        # AI/반도체
        ("Palantir", "AI/반도체 패권전쟁", LinkType.TRADE, "AI 플랫폼, 국방 AI 수혜"),
        # 대만 해협
        ("Samsung Electronics", "대만 해협 위기", LinkType.IMPACTS, "TSMC 대안 파운드리 부상"),
        ("SK Hynix", "대만 해협 위기", LinkType.IMPACTS, "TSMC CoWoS 의존, 대체 리스크"),
    ]

    for stock_name, issue_title, lt, evidence in stock_links:
        sid = stock_ids.get(stock_name)
        issue_id = issues.get(issue_title)
        if not sid or not issue_id:
            continue

        # 이슈의 entity_ids에 종목 추가
        found = i_repo.get_many(filters={"title": issue_title}, limit=1)
        if found:
            issue = found[0]
            if sid not in (issue.entity_ids or []):
                new_eids = list(issue.entity_ids or []) + [sid]
                i_repo.update(issue.id, entity_ids=new_eids)

        _create_link(l_repo, sid, sid, lt, evidence, issue_id)  # placeholder
        # 실제로는 종목 → 이슈 핵심 엔티티 연결이 맞음
        # 이란 이슈의 핵심 엔티티(Crude Oil, US 등)와 연결


def _create_issue(i_repo, title, desc, sev, ev_ids, entity_ids):
    existing = i_repo.get_many(filters={"title": title}, limit=1)
    if existing:
        print(f"    SKIP issue: {title}")
        return existing[0].id
    issue = GeoIssue(title=title, description=desc, severity=sev,
                     status=GeoIssueStatus.ACTIVE, event_ids=ev_ids,
                     entity_ids=entity_ids)
    i_repo.create(issue)
    print(f"    ADD issue: {title}")
    return issue.id


def main():
    init_db()
    e_repo = OntologyEntityRepository()
    ev_repo = OntologyEventRepository()
    l_repo = OntologyLinkRepository()
    i_repo = GeoIssueRepository()

    # 핫 종목 시딩
    stock_ids = seed_hot_stocks(e_repo)

    # 5개 신규 이슈 시딩
    seed_russia_ukraine(e_repo, ev_repo, l_repo, i_repo)
    seed_taiwan_strait(e_repo, ev_repo, l_repo, i_repo)
    seed_eu_crisis(e_repo, ev_repo, l_repo, i_repo)
    seed_ai_regulation(e_repo, ev_repo, l_repo, i_repo)
    seed_boj_shift(e_repo, ev_repo, l_repo, i_repo)

    print("\n=== 전체 시딩 완료 ===")


if __name__ == "__main__":
    print("야간작업: 5개 신규 이슈 + 핫 종목 시딩\n")
    main()
