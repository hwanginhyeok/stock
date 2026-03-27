#!/usr/bin/env python3
"""Ontology I/O helper for Claude Code session-based entity/event extraction.

Subcommands:
    unprocessed  - Print news not yet processed by the ontology extractor
    apply        - Apply Claude's extraction JSON (entities, events, links)
    briefing     - Print current ontology state briefing
    graph        - Print entity-event relationship graph
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Capture real stdout before anything touches it, then redirect stdout to devnull
# so all structlog/print during import goes nowhere.
_out = os.fdopen(os.dup(1), "w")  # fd 1 = real stdout
_devnull = open(os.devnull, "w")  # noqa: SIM115
os.dup2(_devnull.fileno(), 1)  # stdout fd now points to /dev/null

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.database import init_db  # noqa: E402
from src.core.models import (  # noqa: E402
    EventStatus,
    EventType,
    LinkType,
    Market,
    OntologyEntity,
    OntologyEvent,
    OntologyLink,
    Severity,
)
from src.storage import (  # noqa: E402
    NewsRepository,
    OntologyEntityRepository,
    OntologyEventRepository,
    OntologyLinkRepository,
)


def _restore_stdout() -> None:
    """Restore real stdout after all imports and init are done."""
    os.dup2(_out.fileno(), 1)
    sys.stdout = os.fdopen(1, "w")


def cmd_unprocessed(args: argparse.Namespace) -> None:
    """Print news articles not yet processed by the ontology extractor."""
    news_repo = NewsRepository()
    link_repo = OntologyLinkRepository()
    entity_repo = OntologyEntityRepository()
    event_repo = OntologyEventRepository()

    processed_ids = link_repo.get_processed_news_ids()

    market_filter = None
    if args.market != "all":
        market_filter = Market("korea" if args.market == "kr" else "us")

    if market_filter:
        all_news = news_repo.get_by_market(market_filter, limit=500)
    else:
        all_news = news_repo.get_latest(limit=500)

    unprocessed = [n for n in all_news if n.id not in processed_ids]

    market_str = market_filter.value if market_filter else None
    active_entities = entity_repo.get_summaries(market_str)
    active_events = event_repo.get_summaries(market_str)

    output = {
        "unprocessed_count": len(unprocessed),
        "unprocessed": [
            {
                "id": n.id,
                "title": n.title,
                "source": n.source,
                "market": n.market,
                "summary": (n.summary or n.content)[:300],
                "published_at": str(n.published_at or n.created_at),
            }
            for n in unprocessed
        ],
        "existing_entities": active_entities,
        "existing_events": active_events,
    }

    _restore_stdout()
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_apply(args: argparse.Namespace) -> None:
    """Apply extraction results from JSON.

    Expected JSON format::

        {
            "entities": [
                {"name": "Tesla", "entity_type": "company", "ticker": "TSLA",
                 "market": "us"}
            ],
            "events": [
                {"title": "...", "summary": "...", "event_type": "war",
                 "severity": "critical", "market": "korea",
                 "alias": "__mideast__"}
            ],
            "links": [
                {"link_type": "mentions", "source_type": "news",
                 "source_id": "<news_uuid>",
                 "target_type": "entity", "target_id": "<entity_uuid or name>",
                 "confidence": 0.9, "evidence": "..."}
            ]
        }

    Entity target_id in links can be:
    - An existing entity UUID
    - An entity name (will be resolved to existing entity)
    - A new entity name from the same batch

    Event target_id in links can be:
    - An existing event UUID
    - An alias placeholder (e.g. "__mideast__") referencing a new event
    """
    entity_repo = OntologyEntityRepository()
    event_repo = OntologyEventRepository()
    link_repo = OntologyLinkRepository()

    _restore_stdout()

    if args.file:
        data = json.loads(Path(args.file).read_text())
    else:
        data = json.loads(sys.stdin.read())

    now = datetime.now(timezone.utc)
    entity_count = 0
    event_count = 0
    link_count = 0
    skip_count = 0

    # Phase 1: Create/resolve entities
    entity_name_to_id: dict[str, str] = {}

    # Index existing entities by name for dedup
    for ent in entity_repo.get_active():
        entity_name_to_id[ent.name.lower()] = ent.id
        if ent.ticker:
            entity_name_to_id[ent.ticker.lower()] = ent.id

    for item in data.get("entities", []):
        name = item["name"]
        name_lower = name.lower()

        # Skip if entity already exists (by name or ticker)
        ticker = item.get("ticker", "")
        existing_id = entity_name_to_id.get(name_lower)
        if not existing_id and ticker:
            existing_id = entity_name_to_id.get(ticker.lower())

        if existing_id:
            entity_name_to_id[name_lower] = existing_id
            if ticker:
                entity_name_to_id[ticker.lower()] = existing_id
            continue

        entity = OntologyEntity(
            name=name,
            entity_type=item.get("entity_type", "company"),
            ticker=ticker,
            market=Market(item.get("market", "korea")),
            properties=item.get("properties", {}),
        )
        created = entity_repo.create(entity)
        entity_name_to_id[name_lower] = created.id
        if ticker:
            entity_name_to_id[ticker.lower()] = created.id
        entity_count += 1

    # Phase 2: Create events and build alias map
    event_alias_map: dict[str, str] = {}

    # Index existing developing events by title for dedup
    event_title_to_id: dict[str, str] = {}
    for ev in event_repo.get_active():
        event_title_to_id[ev.title.lower()] = ev.id

    for item in data.get("events", []):
        title = item["title"]
        existing_id = event_title_to_id.get(title.lower())

        if existing_id:
            # Reuse existing event
            if "alias" in item:
                event_alias_map[item["alias"]] = existing_id
            continue

        event = OntologyEvent(
            title=title,
            summary=item.get("summary", ""),
            event_type=EventType(item.get("event_type", "macro")),
            severity=Severity(item.get("severity", "moderate")),
            market=Market(item.get("market", "korea")),
            started_at=now,
            status=EventStatus.DEVELOPING,
            article_count=0,
        )
        created = event_repo.create(event)
        event_count += 1
        event_title_to_id[title.lower()] = created.id

        if "alias" in item:
            event_alias_map[item["alias"]] = created.id

    # Phase 3: Create links with ID resolution
    for item in data.get("links", []):
        link_type = item["link_type"]
        source_type = item["source_type"]
        source_id = item["source_id"]
        target_type = item["target_type"]
        target_id = item["target_id"]
        confidence = item.get("confidence", 1.0)
        evidence = item.get("evidence", "")

        # Resolve source aliases/names
        if source_type == "entity" and not _is_uuid(source_id):
            resolved = entity_name_to_id.get(source_id.lower())
            if not resolved:
                skip_count += 1
                continue
            source_id = resolved
        if source_type == "event" and source_id.startswith("__"):
            resolved = event_alias_map.get(source_id)
            if not resolved:
                skip_count += 1
                continue
            source_id = resolved

        # Resolve target aliases/names
        if target_type == "entity" and not _is_uuid(target_id):
            resolved = entity_name_to_id.get(target_id.lower())
            if not resolved:
                skip_count += 1
                continue
            target_id = resolved
        if target_type == "event" and target_id.startswith("__"):
            resolved = event_alias_map.get(target_id)
            if not resolved:
                skip_count += 1
                continue
            target_id = resolved

        # Skip duplicate links
        if link_repo.link_exists(link_type, source_type, source_id, target_type, target_id):
            continue

        link = OntologyLink(
            link_type=LinkType(link_type),
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            confidence=confidence,
            evidence=evidence,
        )
        link_repo.create(link)
        link_count += 1

        # Side effect: increment article_count on events for triggers links
        if link_type == "triggers" and target_type == "event":
            event_repo.increment_article_count(target_id)

    # Side effect: mark stale events
    stale = event_repo.mark_stale(hours=48)

    msg = (
        f"Applied: {entity_count} new entities, {event_count} new events, "
        f"{link_count} new links"
    )
    if skip_count:
        msg += f", {skip_count} skipped (unresolved ID)"
    if stale:
        msg += f", {stale} events marked stale"
    print(msg)


def cmd_briefing(args: argparse.Namespace) -> None:
    """Print current ontology state briefing."""
    entity_repo = OntologyEntityRepository()
    event_repo = OntologyEventRepository()
    link_repo = OntologyLinkRepository()

    market = None
    if args.market != "all":
        market = "korea" if args.market == "kr" else "us"

    entities = entity_repo.get_active(market)
    events = event_repo.get_active(market)
    link_counts = link_repo.count_by_type()

    _restore_stdout()

    total_links = sum(link_counts.values())
    print(f"=== Ontology Briefing ===\n")
    print(f"Entities: {len(entities)} active")
    print(f"Events: {len(events)} developing")
    print(f"Links: {total_links} total ({', '.join(f'{k}={v}' for k, v in link_counts.items() if v > 0)})")
    print()

    if events:
        print(f"--- Developing Events ({len(events)}) ---\n")
        for i, e in enumerate(events, 1):
            # Get involved entities via links
            involves = link_repo.get_links_from("event", e.id, "involves")
            impacts = link_repo.get_links_from("event", e.id, "impacts")
            involved_ids = {lk.target_id for lk in involves + impacts}
            involved_names = [
                ent.name for ent in entities if ent.id in involved_ids
            ]
            names_str = ", ".join(involved_names[:5]) if involved_names else "-"

            print(
                f"{i}. [{e.severity.upper()}] [{e.event_type}] {e.title}\n"
                f"   {e.summary[:120]}\n"
                f"   Market: {e.market} | Articles: {e.article_count}\n"
                f"   Entities: {names_str}"
            )
            print()

    if entities:
        print(f"--- Active Entities ({len(entities)}) ---\n")
        by_type: dict[str, list[OntologyEntity]] = {}
        for ent in entities:
            by_type.setdefault(ent.entity_type, []).append(ent)

        for etype, ents in sorted(by_type.items()):
            names = [f"{e.name}" + (f" ({e.ticker})" if e.ticker else "") for e in ents[:10]]
            print(f"  {etype}: {', '.join(names)}")
            if len(ents) > 10:
                print(f"    ... +{len(ents) - 10} more")
        print()


def cmd_graph(args: argparse.Namespace) -> None:
    """Print entity-event relationship graph as text."""
    entity_repo = OntologyEntityRepository()
    event_repo = OntologyEventRepository()
    link_repo = OntologyLinkRepository()

    market = None
    if args.market != "all":
        market = "korea" if args.market == "kr" else "us"

    entities = entity_repo.get_active(market)
    events = event_repo.get_active(market)

    _restore_stdout()

    if not entities and not events:
        print("Empty ontology. Run 'unprocessed' then 'apply' first.")
        return

    # Build lookup maps
    entity_map = {e.id: e for e in entities}
    event_map = {e.id: e for e in events}

    print("=== Ontology Graph ===\n")

    for event in events:
        severity_icon = {
            "critical": "!!!",
            "major": "!! ",
            "moderate": "!  ",
            "minor": ".  ",
        }.get(event.severity, "   ")

        print(f"[{severity_icon}] EVENT: {event.title}")
        print(f"       type={event.event_type} status={event.status} articles={event.article_count}")

        # involves links
        involves = link_repo.get_links_from("event", event.id, "involves")
        if involves:
            names = []
            for lk in involves:
                ent = entity_map.get(lk.target_id)
                names.append(ent.name if ent else lk.target_id[:8])
            print(f"  involves -> {', '.join(names)}")

        # impacts links
        impacts = link_repo.get_links_from("event", event.id, "impacts")
        if impacts:
            names = []
            for lk in impacts:
                ent = entity_map.get(lk.target_id)
                names.append(ent.name if ent else lk.target_id[:8])
            print(f"  impacts  -> {', '.join(names)}")

        # triggers (news -> event)
        triggers = link_repo.get_links_to("event", event.id, "triggers")
        if triggers:
            print(f"  triggered by {len(triggers)} news article(s)")

        print()

    # Entities not connected to any event
    connected_entity_ids: set[str] = set()
    for event in events:
        involves = link_repo.get_links_from("event", event.id, "involves")
        impacts = link_repo.get_links_from("event", event.id, "impacts")
        for lk in involves + impacts:
            connected_entity_ids.add(lk.target_id)

    orphan_entities = [e for e in entities if e.id not in connected_entity_ids]
    if orphan_entities:
        print(f"--- Unconnected Entities ({len(orphan_entities)}) ---")
        for e in orphan_entities:
            ticker_str = f" ({e.ticker})" if e.ticker else ""
            print(f"  {e.entity_type}: {e.name}{ticker_str}")
        print()


def _is_uuid(s: str) -> bool:
    """Check if a string looks like a UUID (36 chars with dashes)."""
    return len(s) == 36 and s.count("-") == 4


def main() -> None:
    parser = argparse.ArgumentParser(description="Ontology I/O helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_unp = sub.add_parser("unprocessed", help="Print unprocessed news for ontology extraction")
    p_unp.add_argument("--market", choices=["kr", "us", "all"], default="all")

    p_app = sub.add_parser("apply", help="Apply extraction JSON (entities + events + links)")
    p_app.add_argument("--file", help="JSON file path (default: stdin)")

    p_br = sub.add_parser("briefing", help="Print ontology state briefing")
    p_br.add_argument("--market", choices=["kr", "us", "all"], default="all")

    p_gr = sub.add_parser("graph", help="Print entity-event relationship graph")
    p_gr.add_argument("--market", choices=["kr", "us", "all"], default="all")

    args = parser.parse_args()
    init_db()

    {"unprocessed": cmd_unprocessed, "apply": cmd_apply,
     "briefing": cmd_briefing, "graph": cmd_graph}[args.command](args)


if __name__ == "__main__":
    main()
