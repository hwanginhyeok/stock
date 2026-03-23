"""Build ontology graph from extracted news facts.

Automatically creates OntologyEntity nodes from fact entities/tickers,
clusters related facts into OntologyEvents, and links them together.
No LLM API required — purely rule-based.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from src.core.models import (
    EventStatus,
    EventType,
    LinkType,
    Market,
    NewsFact,
    OntologyEntity,
    OntologyEvent,
    OntologyLink,
    Severity,
)
from src.storage import (
    NewsFactRepository,
    OntologyEntityRepository,
    OntologyEventRepository,
    OntologyLinkRepository,
)

# Fact type → Event type mapping
_FACT_TO_EVENT_TYPE: dict[str, EventType] = {
    "earnings": EventType.EARNINGS,
    "policy": EventType.POLICY,
    "deal": EventType.DEAL,
    "event": EventType.MACRO,
    "forecast": EventType.MACRO,
    "numerical": EventType.MACRO,
}

# Fact type → default severity
_FACT_TO_SEVERITY: dict[str, Severity] = {
    "earnings": Severity.MAJOR,
    "policy": Severity.MAJOR,
    "deal": Severity.MODERATE,
    "event": Severity.MODERATE,
    "forecast": Severity.MINOR,
    "numerical": Severity.MINOR,
}


def _resolve_market(market_str: str) -> Market:
    """Convert market string to Market enum."""
    if market_str in ("korea", "kr"):
        return Market.KOREA
    return Market.US


def ensure_entities(
    facts: list[NewsFact],
    entity_repo: OntologyEntityRepository,
) -> dict[str, str]:
    """Ensure all entities from facts exist in the ontology.

    Creates new OntologyEntity for any entity not already in the DB.

    Args:
        facts: List of extracted facts.
        entity_repo: Entity repository.

    Returns:
        Dict mapping entity name (lowercase) → entity UUID.
    """
    # Build index of existing entities
    name_to_id: dict[str, str] = {}
    for ent in entity_repo.get_active():
        name_to_id[ent.name.lower()] = ent.id
        if ent.ticker:
            name_to_id[ent.ticker.lower()] = ent.id

    created = 0
    for fact in facts:
        for entity_name in fact.entities:
            key = entity_name.lower()
            if key in name_to_id:
                continue

            # Determine entity type from context
            entity_type = "company"  # default
            if entity_name in (
                "Fed", "FOMC", "한국은행", "한은", "금통위", "ECB", "BOJ",
                "SEC", "금감원", "공정위", "금융위", "기재부",
                "관세청", "Pentagon", "국방부", "의회", "Congress",
                "NATO", "OPEC", "EU",
            ):
                entity_type = "institution"
            elif entity_name in (
                "미국", "한국", "중국", "일본", "러시아",
                "이란", "Iran", "카타르", "Qatar",
                "UAE", "쿠웨이트", "요르단", "이스라엘", "Israel",
                "사우디", "Saudi", "인도", "India",
                "베트남", "Vietnam", "영국",
            ):
                entity_type = "country"
            elif entity_name in (
                "파월", "Powell", "머스크", "Musk", "트럼프", "Trump",
                "바이든", "Biden", "이재용", "정의선", "최태원",
                "젠슨황", "Jensen Huang",
                "네타냐후", "Netanyahu", "푸틴", "Putin", "시진핑",
            ):
                entity_type = "person"
            elif entity_name in (
                "비트코인", "Bitcoin", "BTC", "이더리움", "Ethereum", "ETH",
                "리플", "XRP", "솔라나", "SOL",
                "원유", "WTI", "금값", "LNG", "디젤",
            ):
                entity_type = "asset"
            elif entity_name in (
                "코스피", "코스닥", "나스닥", "S&P", "다우",
                "KOSPI", "KOSDAQ", "NASDAQ", "Dow",
            ):
                entity_type = "sector"

            # Find ticker if available
            ticker = ""
            for t in fact.tickers:
                ticker = t
                break

            entity = OntologyEntity(
                name=entity_name,
                entity_type=entity_type,
                ticker=ticker,
                market=_resolve_market(fact.market),
            )
            created_ent = entity_repo.create(entity)
            name_to_id[key] = created_ent.id
            if ticker:
                name_to_id[ticker.lower()] = created_ent.id
            created += 1

    return name_to_id


# Story clusters: keyword groups that should be merged into one event
_STORY_CLUSTERS: list[tuple[str, str, EventType, Severity, list[str]]] = [
    # (story_title, market, event_type, severity, keywords)
    (
        "미국-이란 전쟁 + 중동 긴장",
        "us",
        EventType.WAR,
        Severity.CRITICAL,
        ["이란", "Iran", "중동", "Pentagon", "카타르", "Qatar",
         "UAE", "호르무즈", "Hormuz", "LNG", "네타냐후", "Netanyahu",
         "war against Iran", "이란 공격", "이란 긴장", "확전"],
    ),
    (
        "에너지 가격 급등 + 디젤 쇼크",
        "korea",
        EventType.MACRO,
        Severity.MAJOR,
        ["유가", "WTI", "원유", "디젤", "diesel", "oil price",
         "에너지 수입", "fuel", "기름값"],
    ),
    (
        "트럼프 관세 + 무역 정책",
        "us",
        EventType.POLICY,
        Severity.MAJOR,
        ["관세", "tariff", "trade war", "무역", "16개국 조사",
         "Trump tariff", "수입 규제"],
    ),
    (
        "한국 증시 급락 + 매크로 리스크",
        "korea",
        EventType.MACRO,
        Severity.MAJOR,
        ["코스피 급락", "사이드카", "서킷브레이커", "반대매매",
         "코스피지수", "패닉", "폭락", "급락"],
    ),
    (
        "한은 통화정책 전환",
        "korea",
        EventType.POLICY,
        Severity.MAJOR,
        ["한은 총재", "금통위", "기준금리", "금리 인상", "금리 인하",
         "매파", "비둘기"],
    ),
    (
        "BTC/크립토 시장 동향",
        "us",
        EventType.MACRO,
        Severity.MODERATE,
        ["비트코인", "Bitcoin", "BTC", "이더리움", "ETH",
         "채굴", "mining", "크립토"],
    ),
]


def _match_story_cluster(fact: NewsFact) -> str | None:
    """Match a fact to a predefined story cluster.

    Returns story title if matched, None otherwise.
    """
    text = (fact.claim + " " + fact.source_quote).lower()
    for title, _, _, _, keywords in _STORY_CLUSTERS:
        if any(kw.lower() in text for kw in keywords):
            return title
    return None


def _get_or_create_event(
    title: str,
    summary: str,
    event_type: EventType,
    severity: Severity,
    market: str,
    existing: dict[str, str],
    event_repo: OntologyEventRepository,
    article_count: int = 1,
) -> str:
    """Get existing event or create new one. Returns event UUID."""
    now = datetime.now(timezone.utc)
    event_id = existing.get(title.lower())

    if not event_id:
        event = OntologyEvent(
            title=title,
            summary=summary,
            event_type=event_type,
            severity=severity,
            market=_resolve_market(market),
            started_at=now,
            last_article_at=now,
            status=EventStatus.DEVELOPING,
            article_count=article_count,
        )
        created = event_repo.create(event)
        event_id = created.id
        existing[title.lower()] = event_id
    else:
        event_repo.increment_article_count(event_id)

    return event_id


def cluster_facts_to_events(
    facts: list[NewsFact],
    event_repo: OntologyEventRepository,
) -> dict[str, list[str]]:
    """Cluster facts into events with 1:N mapping (multi-event per fact).

    Three-pass clustering:
    1. Macro stories — geopolitics, energy, policy themes
    2. Stock stories — per-ticker company events
    3. A single fact can belong to BOTH macro + stock stories

    Args:
        facts: List of extracted facts.
        event_repo: Event repository.

    Returns:
        Dict mapping fact.id → list of event UUIDs (1:N).
    """
    existing: dict[str, str] = {}
    for ev in event_repo.get_active():
        existing[ev.title.lower()] = ev.id

    # fact_id → [event_id, event_id, ...]
    fact_to_events: dict[str, list[str]] = defaultdict(list)

    story_meta = {t: (m, et, sv) for t, m, et, sv, _ in _STORY_CLUSTERS}

    # ── Pass 1: Macro story clustering ──
    for f in facts:
        story = _match_story_cluster(f)
        if story:
            market, event_type, severity = story_meta[story]
            event_id = _get_or_create_event(
                title=story,
                summary=f.claim[:200],
                event_type=event_type,
                severity=severity,
                market=market,
                existing=existing,
                event_repo=event_repo,
            )
            fact_to_events[f.id].append(event_id)

    # ── Pass 2: Stock/entity story clustering ──
    # Group by each ticker — a fact with multiple tickers creates
    # multiple stock stories
    for f in facts:
        tickers = f.tickers or []
        # Also include non-ticker entities that are companies
        company_entities = [
            e for e in f.entities
            if e not in (
                "Fed", "FOMC", "한은", "금통위", "ECB", "BOJ",
                "SEC", "금감원", "Pentagon", "Congress",
                "이란", "Iran", "카타르", "Qatar", "UAE",
                "미국", "한국", "중국", "일본", "러시아",
                "코스피", "코스닥", "나스닥", "S&P", "다우",
                "원유", "WTI", "LNG", "디젤", "호르무즈",
                "트럼프", "Trump", "파월", "Powell",
                "네타냐후", "Netanyahu",
            )
        ]

        stock_keys: set[str] = set()
        for t in tickers:
            stock_keys.add(t)
        for e in company_entities:
            if e not in stock_keys:
                stock_keys.add(e)

        for key in stock_keys:
            title = f"[종목] {key}"
            event_id = _get_or_create_event(
                title=title,
                summary=f.claim[:200],
                event_type=_FACT_TO_EVENT_TYPE.get(
                    f.fact_type, EventType.MACRO
                ),
                severity=Severity.MODERATE,
                market=f.market,
                existing=existing,
                event_repo=event_repo,
            )
            fact_to_events[f.id].append(event_id)

    # ── Pass 3: Unclustered facts (no macro match, no ticker) ──
    for f in facts:
        if not fact_to_events[f.id]:
            title = f"[{f.fact_type.upper()}] 기타"
            event_id = _get_or_create_event(
                title=title,
                summary=f.claim[:200],
                event_type=_FACT_TO_EVENT_TYPE.get(
                    f.fact_type, EventType.MACRO
                ),
                severity=Severity.MINOR,
                market=f.market,
                existing=existing,
                event_repo=event_repo,
            )
            fact_to_events[f.id].append(event_id)

    return dict(fact_to_events)


def create_links(
    facts: list[NewsFact],
    name_to_id: dict[str, str],
    fact_to_events: dict[str, list[str]],
    link_repo: OntologyLinkRepository,
) -> int:
    """Create ontology links between facts, entities, and events.

    Link types created:
    - news TRIGGERS event (fact → each event, 1:N)
    - event INVOLVES entity (event → entity)
    - macro_event IMPACTS stock_event (cross-link)

    Args:
        facts: List of extracted facts.
        name_to_id: Entity name → UUID mapping.
        fact_to_events: Fact ID → list of Event UUIDs (1:N).
        link_repo: Link repository.

    Returns:
        Number of links created.
    """
    count = 0

    # Collect macro vs stock event IDs for cross-linking
    macro_event_ids: set[str] = set()
    stock_event_ids_per_fact: dict[str, list[str]] = {}

    for fact in facts:
        event_ids = fact_to_events.get(fact.id, [])
        macro_ids = []
        stock_ids = []

        for eid in event_ids:
            # Macro events don't start with [종목]
            # We need to check, but we don't have titles here.
            # Track both and cross-link later.
            pass

        for event_id in event_ids:
            # Fact triggers event
            if not link_repo.link_exists(
                "triggers", "news", fact.news_id, "event", event_id,
            ):
                link = OntologyLink(
                    link_type=LinkType.TRIGGERS,
                    source_type="news",
                    source_id=fact.news_id,
                    target_type="event",
                    target_id=event_id,
                    confidence=fact.confidence,
                    evidence=fact.claim[:200],
                )
                link_repo.create(link)
                count += 1

            # Event involves entities
            for entity_name in fact.entities:
                entity_id = name_to_id.get(entity_name.lower())
                if not entity_id:
                    continue

                if not link_repo.link_exists(
                    "involves", "event", event_id, "entity", entity_id,
                ):
                    link = OntologyLink(
                        link_type=LinkType.INVOLVES,
                        source_type="event",
                        source_id=event_id,
                        target_type="entity",
                        target_id=entity_id,
                        confidence=fact.confidence,
                        evidence=fact.claim[:200],
                    )
                    link_repo.create(link)
                    count += 1

        # Cross-link: if fact belongs to both macro and stock events,
        # create IMPACTS link (macro → stock)
        if len(event_ids) >= 2:
            # First event is typically macro, rest are stock
            for i, eid_a in enumerate(event_ids):
                for eid_b in event_ids[i + 1:]:
                    if not link_repo.link_exists(
                        "impacts", "event", eid_a, "event", eid_b,
                    ):
                        link = OntologyLink(
                            link_type=LinkType.IMPACTS,
                            source_type="event",
                            source_id=eid_a,
                            target_type="event",
                            target_id=eid_b,
                            confidence=fact.confidence,
                            evidence=f"Cross-link via: {fact.claim[:100]}",
                        )
                        link_repo.create(link)
                        count += 1

    return count


def build_ontology_from_facts(
    hours: int = 24,
    market: str | None = None,
) -> dict[str, int]:
    """Full pipeline: facts → entities → events → links.

    Args:
        hours: Lookback window for facts.
        market: Optional market filter.

    Returns:
        Stats dict with entity_count, event_count, link_count.
    """
    fact_repo = NewsFactRepository()
    entity_repo = OntologyEntityRepository()
    event_repo = OntologyEventRepository()
    link_repo = OntologyLinkRepository()

    facts = fact_repo.get_recent(hours=hours, market=market)
    if not facts:
        return {"entity_count": 0, "event_count": 0, "link_count": 0}

    # Step 1: Ensure entities exist
    name_to_id = ensure_entities(facts, entity_repo)

    # Step 2: Cluster facts into events (1:N mapping)
    fact_to_events = cluster_facts_to_events(facts, event_repo)

    # Step 3: Create links + cross-links
    link_count = create_links(facts, name_to_id, fact_to_events, link_repo)

    all_event_ids: set[str] = set()
    for eids in fact_to_events.values():
        all_event_ids.update(eids)

    return {
        "entity_count": len(name_to_id),
        "event_count": len(all_event_ids),
        "link_count": link_count,
        "fact_count": len(facts),
    }
