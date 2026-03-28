"""Build ontology graph from extracted news facts.

Automatically creates OntologyEntity nodes from fact entities/tickers,
clusters related facts into OntologyEvents, and links them together.
No LLM API required — purely rule-based.

Config-driven: story clusters and entity classification loaded from
config/ontology_config.yaml. New themes/entities can be added without code changes.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

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

_CONFIG_PATH = Path("config/ontology_config.yaml")

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

# ── Config loading ──────────────────────────────────────────────────────────

_cached_config: dict[str, Any] | None = None


def _load_config() -> dict[str, Any]:
    """Load ontology config from YAML. Cached after first load."""
    global _cached_config
    if _cached_config is not None:
        return _cached_config

    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            _cached_config = yaml.safe_load(f) or {}
    else:
        _cached_config = {}
    return _cached_config


def _get_story_clusters() -> list[tuple[str, str, EventType, Severity, list[str]]]:
    """Load story clusters from config."""
    config = _load_config()
    clusters = config.get("story_clusters", [])

    event_type_map = {
        "war": EventType.WAR,
        "macro": EventType.MACRO,
        "policy": EventType.POLICY,
        "earnings": EventType.EARNINGS,
        "deal": EventType.DEAL,
    }
    severity_map = {
        "critical": Severity.CRITICAL,
        "major": Severity.MAJOR,
        "moderate": Severity.MODERATE,
        "minor": Severity.MINOR,
    }

    result = []
    for c in clusters:
        result.append((
            c["title"],
            c.get("market", "us"),
            event_type_map.get(c.get("event_type", "macro"), EventType.MACRO),
            severity_map.get(c.get("severity", "moderate"), Severity.MODERATE),
            c.get("keywords", []),
        ))
    return result


def _get_entity_classification() -> dict[str, set[str]]:
    """Load entity classification rules from config."""
    config = _load_config()
    classification = config.get("entity_classification", {})

    result: dict[str, set[str]] = {}
    for entity_type, names in classification.items():
        result[entity_type] = set(names)
    return result


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

            # Determine entity type from config (no hardcoding)
            classification = _get_entity_classification()
            entity_type = "company"  # default
            for etype, names in classification.items():
                if entity_name in names:
                    entity_type = etype
                    break

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


# Story clusters loaded from config/ontology_config.yaml
# No hardcoded clusters — add new themes by editing the YAML file


def _match_story_cluster(fact: NewsFact) -> str | None:
    """Match a fact to a predefined story cluster.

    Returns story title if matched, None otherwise.
    """
    text = (fact.claim + " " + fact.source_quote).lower()
    for title, _, _, _, keywords in _get_story_clusters():
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

    story_meta = {t: (m, et, sv) for t, m, et, sv, _ in _get_story_clusters()}

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
        # Exclude non-company entities (loaded from config)
        classification = _get_entity_classification()
        non_company_names: set[str] = set()
        for etype in ("institution", "country", "person", "asset", "sector"):
            non_company_names.update(classification.get(etype, set()))

        company_entities = [
            e for e in f.entities
            if e not in non_company_names
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
