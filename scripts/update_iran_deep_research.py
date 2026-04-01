#!/usr/bin/env python3
"""이란 전쟁 심층 리서치 DB 업데이트.

이스라엘 성적표(objectives/achievements/strategy/failures) +
2024-25 선행작전 이벤트 + 법적 타임라인 + 신규 엔티티 + 기존 엔티티 속성 보강.

Usage:
    python scripts/update_iran_deep_research.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.database import init_db  # noqa: E402
from src.core.models import (  # noqa: E402
    EntityType,
    EventStatus,
    EventType,
    GeoIssue,
    Market,
    OntologyEntity,
    OntologyEvent,
    Severity,
)
from src.storage import (  # noqa: E402
    GeoIssueRepository,
    OntologyEntityRepository,
    OntologyEventRepository,
)


def _parse_date(date_str: str) -> datetime:
    """날짜 문자열을 UTC datetime으로 변환."""
    return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _merge_list(existing: list, new_items: list) -> list:
    """기존 리스트에 새 항목을 중복 없이 추가."""
    existing_set = set(existing)
    merged = list(existing)
    for item in new_items:
        if item not in existing_set:
            merged.append(item)
            existing_set.add(item)
    return merged


def update_israel_properties(entity_repo: OntologyEntityRepository) -> str | None:
    """이스라엘 엔티티 속성을 심층 리서치 결과로 업데이트."""
    print("\n=== A. 이스라엘 엔티티 속성 업데이트 ===")

    israel = entity_repo.find_by_name("Israel")
    if not israel:
        print("  ERROR: Israel 엔티티 없음!")
        return None

    new_props = {
        "역할": "공격측 (Operation Roaring Lion)",
        "objectives": [
            "이란 핵 프로그램 영구 무력화",
            "프록시(헤즈볼라·하마스·후티) 해체",
            "이란 정권 교체",
            "북부 안보 확보 (주민 6만 명 귀환)",
            "미사일/드론 생산능력 제거",
            "10.7 이후 억지력 재확립",
            "사우디 정상화 (아브라함 협정 확대)",
            "네타냐후 정치적 생존 (재판 회피 + 연립 안정)",
        ],
        "strategy": [
            "미국과 합동 선제 기습 공습 (12시간 900회)",
            "지도부 참수 작전 (하메네이·나스랄라·하니예·신와르)",
            "핵시설 벙커버스터 타격 (나탄즈·포르도·이스파한)",
            "S-300 방공망 선제 파괴로 자유로운 영공 확보",
        ],
        "achievements": [
            "하메네이 참수 (2026.2.28) — 이란 건국 이래 최초",
            "핵시설 3곳 물리적 타격 (나탄즈·포르도·이스파한)",
            "S-300 방공망 전량 파괴 (2024.10 Days of Repentance)",
            "미사일 생산능력 90% 파괴 (플래니터리 믹서 12대, 발사대 190기+)",
            "이란 해군 함정 150척 파괴",
            "15,000개+ 표적 타격",
            "프록시 지도부 전멸: 나스랄라(2024.9), 하니예(2024.7), 신와르(2024.10)",
            "IRGC 장성 30명+ 제거, 핵 과학자 9명 포함",
            "이란 국내 시위 촉발 — 200개 도시, 1979년 이후 최대",
        ],
        "failures": [
            "핵 물질 제거 불가 — 60% HEU 440kg 보유 (핵무기 ~10개 분량)",
            "이스파한에 새 지하 농축시설 발견 (IAEA, 2026.3)",
            "호르무즈 봉쇄 촉발 — 유가 $166, 1970년대 이후 최대 에너지 위기",
            "프록시 재편: 후티 3/28 재참전, 헤즈볼라 3/2 공격 재개",
            "이란 체제 존속 — 모즈타바 하메네이 10일 만에 후계",
            "12개국 피격 (GCC 전체 + 요르단·이라크·아제르바이잔)",
            "이스라엘 본토 피해 — 민간 23명+군 11명 사망, 6,131명 부상",
            "사우디 정상화 후퇴 — 여론 99% 반대",
            "국방비 GDP 8.8% (458억 달러, 2023 대비 120% 증가)",
            "전쟁 종결 불가 — 5주차, 출구 전략 없음",
        ],
        "한줄평": "전술적으로 역사적 성과, 전략적으로 출구 없는 소모전 진입. 왕을 죽였지만 왕국은 살아있다.",
        "현황": "5주차 전쟁 지속. 다전선(레바논, 예멘, 가자) 동시 교전. 참모총장 '900일+ 작전 지속 불가능' 경고.",
    }

    # 기존 properties에 병합
    merged = {**israel.properties, **new_props}
    entity_repo.update(israel.id, properties=merged)
    print(f"  UPDATE: Israel (id={israel.id}) — {len(new_props)}개 필드 업데이트")
    return israel.id


def add_precedent_events(event_repo: OntologyEventRepository) -> list[str]:
    """2024-25 선행작전 + 법적 타임라인 이벤트 추가."""
    print("\n=== B. 2024-25 선행작전 + 법적 타임라인 이벤트 추가 ===")

    events_data = [
        {
            "title": "2024 | 하마스 정치지도자 하니예 테헤란에서 암살",
            "date": "2024-07-31",
            "event_type": EventType.MILITARY,
            "severity": Severity.CRITICAL,
            "summary": "이스라엘, 하마스 정치지도자 이스마일 하니예를 테헤란에서 암살. "
                       "이란 수도 한복판에서의 작전으로 이란의 안보 취약성 노출.",
        },
        {
            "title": "2024 | 페이저 폭발 — 헤즈볼라 통신망 마비",
            "date": "2024-09-17",
            "event_type": EventType.MILITARY,
            "severity": Severity.CRITICAL,
            "summary": "헤즈볼라 조직원들의 페이저/워키토키 동시 폭발. "
                       "수천 명 부상, 통신 체계 마비. 전례 없는 공급망 침투 작전.",
        },
        {
            "title": "2024 | 나스랄라 사살 — 헤즈볼라 32년 수장 제거",
            "date": "2024-09-27",
            "event_type": EventType.MILITARY,
            "severity": Severity.CRITICAL,
            "summary": "이스라엘, 베이루트 지하 벙커 폭격으로 헤즈볼라 사무총장 "
                       "하산 나스랄라 사살. 32년간 조직을 이끈 지도자 제거.",
        },
        {
            "title": "2024 | Days of Repentance — 이란 본토 F-35 100기 공습",
            "date": "2024-10-26",
            "event_type": EventType.MILITARY,
            "severity": Severity.CRITICAL,
            "summary": "이스라엘 F-35 100기 편대, 이란 본토 공습. "
                       "S-300 방공망 전량 파괴. 이란 영공 무방비 상태 노출.",
        },
        {
            "title": "2024 | 하마스 군사지도자 신와르 사살",
            "date": "2024-10-16",
            "event_type": EventType.MILITARY,
            "severity": Severity.CRITICAL,
            "summary": "이스라엘, 가자에서 하마스 군사지도자 야히야 신와르 사살. "
                       "10.7 공격 주모자 제거.",
        },
        {
            "title": "2025 | 12일 전쟁 — 핵시설 3곳 벙커버스터 타격",
            "date": "2025-06-13",
            "event_type": EventType.MILITARY,
            "severity": Severity.CRITICAL,
            "summary": "이스라엘+미국, 이란 핵시설 3곳(나탄즈·포르도·이스파한) "
                       "GBU-57 벙커버스터로 타격. 12일간 집중 공습.",
        },
        {
            "title": "2025 | IRGC 총사령관 살라미 + 참모총장 바게리 사살",
            "date": "2025-06-15",
            "event_type": EventType.MILITARY,
            "severity": Severity.CRITICAL,
            "summary": "IRGC 총사령관 호세인 살라미 및 군 참모총장 바게리 동시 사살. "
                       "이란 군 지휘체계 마비.",
        },
        {
            "title": "법적 | 의회 승인 없는 전쟁 — 트럼프 Article II 자위권만 원용",
            "date": "2026-02-28",
            "event_type": EventType.REGULATION,
            "severity": Severity.CRITICAL,
            "summary": "트럼프 대통령, 헌법 Article II 자위권만으로 이란 전쟁 개시. "
                       "의회 승인(AUMF/전쟁선포) 없이 군사작전 시작. 헌법적 논란.",
        },
        {
            "title": "법적 | 상원 전쟁권한결의안 47-53 부결",
            "date": "2026-03-04",
            "event_type": EventType.REGULATION,
            "severity": Severity.CRITICAL,
            "summary": "상원, 전쟁권한결의안(War Powers Resolution) 47-53으로 부결. "
                       "공화당 다수가 대통령 전쟁 권한 지지.",
        },
        {
            "title": "법적 | 하원 전쟁권한결의안 212-219 부결",
            "date": "2026-03-05",
            "event_type": EventType.REGULATION,
            "severity": Severity.CRITICAL,
            "summary": "하원, 전쟁권한결의안 212-219로 부결. "
                       "양원 모두 전쟁 중단 결의 실패. 전쟁 법적 견제 불가.",
        },
    ]

    new_event_ids = []
    for evt in events_data:
        # title로 dedup
        existing = event_repo.get_many(filters={"title": evt["title"]}, limit=1)
        if existing:
            new_event_ids.append(existing[0].id)
            print(f"  SKIP: {evt['title'][:50]}... (이미 존재)")
            continue

        event = OntologyEvent(
            title=evt["title"],
            summary=evt["summary"],
            event_type=evt["event_type"],
            severity=evt["severity"],
            market=Market.US,
            started_at=_parse_date(evt["date"]),
            last_article_at=_parse_date(evt["date"]),
            status=EventStatus.RESOLVED if evt["date"] < "2026-01-01" else EventStatus.ESCALATING,
        )
        event_repo.create(event)
        new_event_ids.append(event.id)
        print(f"  ADD:  {evt['title'][:60]}...")

    return new_event_ids


def add_new_entities(entity_repo: OntologyEntityRepository) -> list[str]:
    """새 엔티티 추가 (Netanyahu, Mojtaba Khamenei, Natanz, Fordow, Isfahan)."""
    print("\n=== C. 신규 엔티티 추가 ===")

    entities_data = [
        {
            "name": "Benjamin Netanyahu",
            "entity_type": EntityType.PERSON,
            "aliases": ["네타냐후", "비비", "Bibi"],
            "properties": {
                "역할": "이스라엘 총리, 전쟁 지휘",
                "정치적_생존": "부패 재판 3건 진행 중 — 전쟁 중 재판 사실상 중단",
                "연립_안정": "극우 연립 (벤 그비르, 스모트리치) — 전쟁 확대 요구",
                "전략": "안보 위기를 정치적 생존으로 전환. 전쟁 종결이 곧 정치적 위기.",
                "지지율": "전쟁 초기 72% → 현재 하락세, 그러나 대안 부재",
                "리스크": "전쟁 종결 시 재판 재개 + 연립 붕괴 가능성",
            },
        },
        {
            "name": "Mojtaba Khamenei",
            "entity_type": EntityType.PERSON,
            "aliases": ["모즈타바 하메네이", "모흐타바 하메네이", "모즈타바"],
            "properties": {
                "역할": "이란 최고지도자 후계 (2026.3.8 지정)",
                "취임": "하메네이 사망(2/28) 후 10일 만에 전문가의회 지정",
                "정통성": "의문 — 세습(아들 승계)은 이슬람 공화국 원칙에 반함",
                "도전": "IRGC 충성 확보 불확실, 개혁파 반발, 200개 도시 시위 진행 중",
                "프로필": "전임 하메네이의 비공식 수행비서 + IRGC 연락책 역할",
                "리스크": "체제 내 권력투쟁, 군부 쿠데타 가능성 거론",
            },
        },
        {
            "name": "Natanz",
            "entity_type": EntityType.ASSET,
            "aliases": ["나탄즈", "나탄즈 핵시설"],
            "properties": {
                "유형": "이란 우라늄 농축 시설 (주력)",
                "위치": "이스파한 남동 200km",
                "시설": "지하 원심분리기 시설 — 60% HEU 생산",
                "피격이력": "2025.6 벙커버스터 타격, 2024.10 Days of Repentance 타격",
                "현황": "물리적 피해 심각, 그러나 핵 물질(440kg HEU) 제거 불가",
                "IAEA": "사찰 제한 상태",
            },
        },
        {
            "name": "Fordow",
            "entity_type": EntityType.ASSET,
            "aliases": ["포르도", "포르도 핵시설"],
            "properties": {
                "유형": "이란 지하 우라늄 농축 시설",
                "위치": "쿰(Qom) 인근, 산속 깊은 지하",
                "특징": "산속 터널 시설 — 벙커버스터로도 완전 파괴 어려움",
                "피격이력": "2025.6 GBU-57 벙커버스터 타격",
                "현황": "부분적 피해, 완전 파괴 미확인",
            },
        },
        {
            "name": "Isfahan",
            "entity_type": EntityType.ASSET,
            "aliases": ["이스파한", "이스파한 핵시설"],
            "properties": {
                "유형": "이란 핵 관련 시설 (UCF + 신규 지하시설)",
                "위치": "이스파한 시",
                "피격이력": "2025.6 벙커버스터 타격",
                "발견": "2026.3 IAEA, 새 지하 농축시설 발견 — 이전에 미확인된 시설",
                "현황": "신규 시설 존재로 핵 프로그램 완전 무력화 실패 확인",
                "의의": "이스라엘 최대 전략적 실패 — 알려지지 않은 시설이 더 있을 가능성",
            },
        },
    ]

    new_entity_ids = []
    for ent in entities_data:
        existing = entity_repo.find_by_name(ent["name"])
        if existing:
            new_entity_ids.append(existing.id)
            print(f"  SKIP: {ent['name']} (이미 존재)")
            continue

        entity = OntologyEntity(
            name=ent["name"],
            entity_type=ent["entity_type"],
            market=Market.US,
            aliases=ent["aliases"],
            properties=ent["properties"],
        )
        entity_repo.create(entity)
        new_entity_ids.append(entity.id)
        print(f"  ADD:  {ent['name']} [{ent['entity_type']}]")

    return new_entity_ids


def update_iran_properties(entity_repo: OntologyEntityRepository) -> str | None:
    """이란 엔티티 속성 보강 (achievements, strategy 추가)."""
    print("\n=== D. 이란 엔티티 속성 보강 ===")

    iran = entity_repo.find_by_name("Iran")
    if not iran:
        print("  ERROR: Iran 엔티티 없음!")
        return None

    props = dict(iran.properties)

    # achievements 추가
    existing_achievements = props.get("achievements", [])
    new_achievements = [
        "미군 철수 유도",
        "후계 체제 10일 내 수립",
        "200개 도시 시위에도 체제 유지",
    ]
    props["achievements"] = _merge_list(existing_achievements, new_achievements)

    # strategy 추가
    existing_strategy = props.get("strategy", [])
    new_strategy = [
        "분산형 모자이크 방어 독트린",
        "장기 소모전 전략 — 휴전은 적이 재무장할 시간",
    ]
    props["strategy"] = _merge_list(existing_strategy, new_strategy)

    entity_repo.update(iran.id, properties=props)
    print(f"  UPDATE: Iran (id={iran.id})")
    print(f"    achievements: +{len(new_achievements)}개")
    print(f"    strategy: +{len(new_strategy)}개")
    return iran.id


def update_us_properties(entity_repo: OntologyEntityRepository) -> str | None:
    """미국 엔티티 속성 보강 (failures, achievements 추가)."""
    print("\n=== E. 미국 엔티티 속성 보강 ===")

    us = entity_repo.find_by_name("United States")
    if not us:
        print("  ERROR: United States 엔티티 없음!")
        return None

    props = dict(us.properties)

    # failures 추가
    existing_failures = props.get("failures", [])
    new_failures = [
        "의회 승인 없이 전쟁 시작 — 헌법적 논란",
    ]
    props["failures"] = _merge_list(existing_failures, new_failures)

    # achievements 추가
    existing_achievements = props.get("achievements", [])
    new_achievements = [
        "이란 방공 전량 파괴로 자유 영공 확보",
    ]
    props["achievements"] = _merge_list(existing_achievements, new_achievements)

    entity_repo.update(us.id, properties=props)
    print(f"  UPDATE: United States (id={us.id})")
    print(f"    failures: +{len(new_failures)}개")
    print(f"    achievements: +{len(new_achievements)}개")
    return us.id


def update_geo_issue(
    issue_repo: GeoIssueRepository,
    new_event_ids: list[str],
    new_entity_ids: list[str],
) -> None:
    """이란 전쟁 GeoIssue에 새 event_ids, entity_ids 추가."""
    print("\n=== F. GeoIssue '이란 전쟁' 업데이트 ===")

    existing = issue_repo.get_many(filters={"title": "이란 전쟁"}, limit=1)
    if not existing:
        print("  ERROR: GeoIssue '이란 전쟁' 없음!")
        return

    issue = existing[0]

    # event_ids 병합
    merged_event_ids = _merge_list(issue.event_ids, new_event_ids)
    added_events = len(merged_event_ids) - len(issue.event_ids)

    # entity_ids 병합
    merged_entity_ids = _merge_list(issue.entity_ids, new_entity_ids)
    added_entities = len(merged_entity_ids) - len(issue.entity_ids)

    issue_repo.update(
        issue.id,
        event_ids=merged_event_ids,
        entity_ids=merged_entity_ids,
    )
    print(f"  UPDATE: GeoIssue '이란 전쟁' (id={issue.id})")
    print(f"    event_ids: {len(issue.event_ids)} → {len(merged_event_ids)} (+{added_events})")
    print(f"    entity_ids: {len(issue.entity_ids)} → {len(merged_entity_ids)} (+{added_entities})")


def main() -> None:
    """메인 실행."""
    print("이란 전쟁 심층 리서치 DB 업데이트 시작...\n")

    init_db()

    entity_repo = OntologyEntityRepository()
    event_repo = OntologyEventRepository()
    issue_repo = GeoIssueRepository()

    # A. 이스라엘 속성 업데이트
    israel_id = update_israel_properties(entity_repo)

    # B. 2024-25 선행작전 + 법적 타임라인 이벤트
    new_event_ids = add_precedent_events(event_repo)

    # C. 신규 엔티티
    new_entity_ids = add_new_entities(entity_repo)

    # D. 이란 속성 보강
    iran_id = update_iran_properties(entity_repo)

    # E. 미국 속성 보강
    us_id = update_us_properties(entity_repo)

    # F. GeoIssue 업데이트 — 새 이벤트 + 엔티티 ID 연결
    all_new_entity_ids = new_entity_ids[:]
    # 기존 엔티티(Israel, Iran, US)는 이미 등록되어 있을 수 있으므로
    # GeoIssue에 entity_ids로 추가만 함
    for eid in [israel_id, iran_id, us_id]:
        if eid:
            all_new_entity_ids.append(eid)

    update_geo_issue(issue_repo, new_event_ids, all_new_entity_ids)

    print("\n업데이트 완료!")


if __name__ == "__main__":
    main()
