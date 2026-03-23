#!/usr/bin/env python3
"""News fact extraction CLI for rule-based and Claude Code session extraction.

Subcommands:
    unprocessed  - Print news not yet processed by the fact extractor
    auto         - Run rule-based extraction on unprocessed news
    apply        - Apply Claude Code's extraction JSON (facts list)
    briefing     - Print recent fact briefing
    export       - Export daily facts to JSON file
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Capture real stdout before anything touches it
_out = os.fdopen(os.dup(1), "w")
_devnull = open(os.devnull, "w")  # noqa: SIM115
os.dup2(_devnull.fileno(), 1)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.analyzers.fact_extractor import extract_facts_batch  # noqa: E402
from src.core.database import init_db  # noqa: E402
from src.core.models import FactType, Market, NewsFact  # noqa: E402
from src.storage import NewsFactRepository, NewsRepository  # noqa: E402


def _restore_stdout() -> None:
    """Restore real stdout after all imports and init are done."""
    os.dup2(_out.fileno(), 1)
    sys.stdout = os.fdopen(1, "w")


def cmd_unprocessed(args: argparse.Namespace) -> None:
    """Print news articles not yet processed by the fact extractor."""
    news_repo = NewsRepository()
    fact_repo = NewsFactRepository()

    processed_ids = fact_repo.get_processed_news_ids()

    market_filter = None
    if args.market != "all":
        market_filter = Market("korea" if args.market == "kr" else "us")

    if market_filter:
        all_news = news_repo.get_by_market(market_filter, limit=500)
    else:
        all_news = news_repo.get_latest(limit=500)

    unprocessed = [n for n in all_news if n.id not in processed_ids]

    output = {
        "unprocessed_count": len(unprocessed),
        "total_news": len(all_news),
        "already_processed": len(processed_ids),
        "unprocessed": [
            {
                "id": n.id,
                "title": n.title,
                "source": n.source,
                "market": n.market,
                "content_preview": (n.content or n.summary)[:400],
                "published_at": str(n.published_at or n.created_at),
            }
            for n in unprocessed
        ],
    }

    _restore_stdout()
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_auto(args: argparse.Namespace) -> None:
    """Run rule-based extraction on unprocessed news."""
    news_repo = NewsRepository()
    fact_repo = NewsFactRepository()

    processed_ids = fact_repo.get_processed_news_ids()

    market_filter = None
    if args.market != "all":
        market_filter = Market("korea" if args.market == "kr" else "us")

    if market_filter:
        all_news = news_repo.get_by_market(market_filter, limit=500)
    else:
        all_news = news_repo.get_latest(limit=500)

    unprocessed = [n for n in all_news if n.id not in processed_ids]

    _restore_stdout()

    if not unprocessed:
        print("No unprocessed news articles.")
        return

    print(f"Processing {len(unprocessed)} articles...")

    results = extract_facts_batch(unprocessed)
    total_facts = 0

    for news_id, facts in results.items():
        for fact in facts:
            if fact.confidence >= args.min_confidence:
                fact_repo.create(fact)
                total_facts += 1

    print(
        f"Extracted: {total_facts} facts from {len(results)} articles "
        f"(min confidence: {args.min_confidence})"
    )


def cmd_apply(args: argparse.Namespace) -> None:
    """Apply extraction results from JSON file or stdin.

    Expected JSON format::

        {
            "facts": [
                {
                    "news_id": "<uuid>",
                    "fact_type": "numerical",
                    "claim": "SK하이닉스 HBM4 수율 85%",
                    "entities": ["SK하이닉스"],
                    "tickers": ["000660"],
                    "numbers": {"raw_values": ["85%"], "count": 1},
                    "source_quote": "원문 인용",
                    "market": "korea",
                    "confidence": 1.0,
                    "published_at": "2026-03-23T..."
                }
            ]
        }
    """
    _MAX_INPUT_BYTES = 10 * 1024 * 1024  # 10 MB
    _MAX_FACTS = 10_000

    fact_repo = NewsFactRepository()

    _restore_stdout()

    # --- Read & validate input ---
    if args.file:
        file_path = Path(args.file).resolve()
        allowed_roots = [_PROJECT_ROOT.resolve(), Path("/tmp").resolve()]
        if not any(
            str(file_path).startswith(str(root)) for root in allowed_roots
        ):
            print(f"Error: access denied — {file_path}", file=sys.stderr)
            sys.exit(1)
        try:
            raw = file_path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, OSError) as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        raw = sys.stdin.read(_MAX_INPUT_BYTES + 1)
        if len(raw) > _MAX_INPUT_BYTES:
            print(
                f"Error: input exceeds {_MAX_INPUT_BYTES // (1024*1024)}MB",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)

    facts_data = data.get("facts", [])
    if not isinstance(facts_data, list):
        print("Error: 'facts' must be an array", file=sys.stderr)
        sys.exit(1)
    if len(facts_data) > _MAX_FACTS:
        print(f"Error: too many facts (max {_MAX_FACTS})", file=sys.stderr)
        sys.exit(1)

    # --- Process each fact ---
    count = 0
    skip_count = 0

    for i, item in enumerate(facts_data):
        if not isinstance(item, dict):
            skip_count += 1
            continue

        # Required fields
        news_id = item.get("news_id")
        claim = item.get("claim")
        if not news_id or not claim:
            skip_count += 1
            continue

        # Enum validation
        try:
            fact_type = FactType(item.get("fact_type", "numerical"))
        except ValueError:
            fact_type = FactType.NUMERICAL

        try:
            market = Market(item.get("market", "korea"))
        except ValueError:
            market = Market.KOREA

        # Confidence clamping
        confidence = item.get("confidence", 1.0)
        if not isinstance(confidence, (int, float)):
            confidence = 1.0
        confidence = max(0.0, min(1.0, float(confidence)))

        # Published at
        published_at = None
        if item.get("published_at"):
            try:
                published_at = datetime.fromisoformat(item["published_at"])
            except (ValueError, TypeError):
                pass

        fact = NewsFact(
            news_id=str(news_id),
            fact_type=fact_type,
            claim=str(claim)[:2000],
            entities=item.get("entities", []),
            tickers=item.get("tickers", []),
            numbers=item.get("numbers", {}),
            source_quote=str(item.get("source_quote", ""))[:5000],
            market=market,
            confidence=confidence,
            published_at=published_at,
            extracted_at=datetime.now(timezone.utc),
        )
        fact_repo.create(fact)
        count += 1

    msg = f"Applied: {count} facts from Claude Code session"
    if skip_count:
        msg += f" ({skip_count} skipped — missing required fields)"
    print(msg)


def cmd_briefing(args: argparse.Namespace) -> None:
    """Print recent fact briefing."""
    fact_repo = NewsFactRepository()

    market = None
    if args.market != "all":
        market = "korea" if args.market == "kr" else "us"

    facts = fact_repo.get_recent(hours=args.hours, market=market)

    _restore_stdout()

    if not facts:
        print(f"No facts in the last {args.hours} hours.")
        return

    # Group by fact_type
    by_type: dict[str, list[NewsFact]] = {}
    for f in facts:
        by_type.setdefault(f.fact_type, []).append(f)

    market_label = market.upper() if market else "ALL"
    print(f"=== Fact Briefing ({market_label}, last {args.hours}h) ===")
    print(f"Total: {len(facts)} facts\n")

    type_labels = {
        "numerical": "숫자/수치",
        "earnings": "실적",
        "policy": "정책/규제",
        "deal": "딜/계약",
        "forecast": "전망",
        "event": "이벤트",
    }

    for fact_type, items in sorted(by_type.items()):
        label = type_labels.get(fact_type, fact_type)
        print(f"--- {label} ({len(items)}) ---\n")
        for f in items[:10]:
            tickers_str = ", ".join(f.tickers) if f.tickers else "-"
            confidence_str = f"{'★' * int(f.confidence * 5)}"
            print(f"  [{tickers_str}] {f.claim[:120]}")
            print(f"    confidence={f.confidence:.1f} {confidence_str}")
            if f.numbers.get("raw_values"):
                print(f"    numbers: {', '.join(f.numbers['raw_values'][:3])}")
            print()


def cmd_enrich(args: argparse.Namespace) -> None:
    """Fetch full article content for title-only news via URL scraping.

    Respects rate limiting (2s between requests) and robots.txt conventions.
    Only fetches articles that have a URL but no content.
    """
    import time

    import requests
    from bs4 import BeautifulSoup

    news_repo = NewsRepository()

    market_filter = None
    if args.market != "all":
        market_filter = Market("korea" if args.market == "kr" else "us")

    if market_filter:
        all_news = news_repo.get_by_market(market_filter, limit=500)
    else:
        all_news = news_repo.get_latest(limit=500)

    # Filter: has URL, no content
    needs_content = [
        n for n in all_news
        if n.url and (not n.content or len(n.content) <= 50)
    ]

    _restore_stdout()

    if not needs_content:
        print("No articles need content enrichment.")
        return

    limit = min(len(needs_content), args.limit)
    print(f"Enriching {limit}/{len(needs_content)} articles...")

    enriched = 0
    failed = 0
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; StockRichBot/1.0; "
            "+research-only; rate-limited)"
        ),
    }

    for n in needs_content[:limit]:
        try:
            resp = requests.get(
                n.url, headers=headers, timeout=10, allow_redirects=True,
            )
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove script/style/nav/footer
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            # Try common article selectors
            article = (
                soup.find("article")
                or soup.find("div", class_=lambda c: c and "article" in c)
                or soup.find("div", class_=lambda c: c and "content" in c)
                or soup.find("div", id=lambda i: i and "article" in i)
            )

            if article:
                text = article.get_text(separator=" ", strip=True)
            else:
                # Fallback: all <p> tags
                paragraphs = soup.find_all("p")
                text = " ".join(p.get_text(strip=True) for p in paragraphs)

            # Clean up
            import re as _re

            text = _re.sub(r"\s+", " ", text).strip()

            if len(text) > 100:
                # Update in DB directly
                from src.core.database import NewsItemDB, get_session

                with get_session() as session:
                    row = session.get(NewsItemDB, n.id)
                    if row:
                        row.content = text[:10000]
                        if not row.summary or len(row.summary) < 50:
                            row.summary = text[:300]
                enriched += 1
                print(f"  ✓ {n.source}: {n.title[:50]}... ({len(text)}자)")
            else:
                failed += 1

        except Exception:
            failed += 1

        time.sleep(args.delay)

    print(f"\nEnriched: {enriched}, Failed: {failed}")


def cmd_export(args: argparse.Namespace) -> None:
    """Export daily facts to JSON file."""
    fact_repo = NewsFactRepository()

    market = None
    if args.market != "all":
        market = "korea" if args.market == "kr" else "us"

    facts = fact_repo.get_recent(hours=args.hours, market=market)

    _restore_stdout()

    if not facts:
        print(f"No facts to export (last {args.hours}h).")
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    market_suffix = f"_{market}" if market else ""
    output_dir = _PROJECT_ROOT / "data" / "facts"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{today}{market_suffix}.json"

    export_data = {
        "date": today,
        "market": market or "all",
        "count": len(facts),
        "facts": [
            {
                "id": f.id,
                "news_id": f.news_id,
                "fact_type": f.fact_type,
                "claim": f.claim,
                "entities": f.entities,
                "tickers": f.tickers,
                "numbers": f.numbers,
                "source_quote": f.source_quote,
                "market": f.market,
                "confidence": f.confidence,
                "published_at": str(f.published_at) if f.published_at else None,
                "extracted_at": str(f.extracted_at),
            }
            for f in facts
        ],
    }

    output_path.write_text(
        json.dumps(export_data, ensure_ascii=False, indent=2)
    )
    print(f"Exported {len(facts)} facts → {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="News fact extraction CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # unprocessed
    p_unp = sub.add_parser("unprocessed", help="Print unprocessed news")
    p_unp.add_argument("--market", choices=["kr", "us", "all"], default="all")

    # auto
    p_auto = sub.add_parser("auto", help="Run rule-based extraction")
    p_auto.add_argument("--market", choices=["kr", "us", "all"], default="all")
    p_auto.add_argument(
        "--min-confidence", type=float, default=0.5,
        help="Minimum confidence threshold (default: 0.5)",
    )

    # apply
    p_app = sub.add_parser("apply", help="Apply Claude Code extraction JSON")
    p_app.add_argument("--file", help="JSON file path (default: stdin)")

    # briefing
    p_br = sub.add_parser("briefing", help="Print recent fact briefing")
    p_br.add_argument("--market", choices=["kr", "us", "all"], default="all")
    p_br.add_argument("--hours", type=int, default=12, help="Lookback hours")

    # enrich
    p_en = sub.add_parser("enrich", help="Fetch article content from URLs")
    p_en.add_argument("--market", choices=["kr", "us", "all"], default="all")
    p_en.add_argument(
        "--limit", type=int, default=30,
        help="Max articles to fetch (default: 30)",
    )
    p_en.add_argument(
        "--delay", type=float, default=2.0,
        help="Delay between requests in seconds (default: 2.0)",
    )

    # export
    p_ex = sub.add_parser("export", help="Export facts to JSON file")
    p_ex.add_argument("--market", choices=["kr", "us", "all"], default="all")
    p_ex.add_argument("--hours", type=int, default=24, help="Lookback hours")

    args = parser.parse_args()

    try:
        init_db()
    except Exception as e:
        _restore_stdout()
        print(f"Error: database init failed — {e}", file=sys.stderr)
        sys.exit(1)

    try:
        {
            "unprocessed": cmd_unprocessed,
            "auto": cmd_auto,
            "apply": cmd_apply,
            "enrich": cmd_enrich,
            "briefing": cmd_briefing,
            "export": cmd_export,
        }[args.command](args)
    except Exception as e:
        _restore_stdout()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
