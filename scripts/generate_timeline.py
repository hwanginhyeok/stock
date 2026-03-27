#!/usr/bin/env python3
"""Generate ontology event timeline as matplotlib PNG.

Usage::

    python scripts/generate_timeline.py --market kr --days 7
    python scripts/generate_timeline.py --market all --days 30 --output timeline.png
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.database import init_db  # noqa: E402
from src.storage import OntologyEventRepository, OntologyLinkRepository  # noqa: E402

# ── Font setup ──
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT_PATH):
    fm.fontManager.addfont(_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# ── Color scheme (project standard) ──
BG = "#0d1117"
CARD_BG = "#161b22"
TEXT = "#e2e8f0"
TEXT_DIM = "#6e7681"
BORDER = "#30363d"

SEVERITY_COLORS = {
    "critical": "#f85149",
    "major": "#d29922",
    "moderate": "#58a6ff",
    "minor": "#6e7681",
}

EVENT_TYPE_ICONS = {
    "earnings": "E",
    "policy": "P",
    "deal": "D",
    "war": "W",
    "product": "R",
    "regulation": "G",
    "macro": "M",
}


def generate_timeline(
    market: str | None = None,
    days: int = 7,
    output: str | None = None,
) -> Path:
    """Generate a timeline PNG from ontology events.

    Args:
        market: Optional market filter ('korea' or 'us').
        days: Number of days to look back.
        output: Output file path (default: data/timelines/{date}.png).

    Returns:
        Path to generated PNG.
    """
    event_repo = OntologyEventRepository()
    link_repo = OntologyLinkRepository()

    # Get events
    events = event_repo.get_active(market)
    if not events:
        print("No active events to plot.")
        sys.exit(0)

    # Sort by started_at
    events.sort(key=lambda e: e.started_at)

    # Filter by date range (handle naive datetimes from DB)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    filtered = []
    for e in events:
        started = e.started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        if started >= cutoff:
            filtered.append(e)
    events = filtered

    if not events:
        print(f"No events in the last {days} days.")
        sys.exit(0)

    # ── Build figure ──
    n = len(events)
    fig_height = max(6, n * 0.6 + 2)
    fig, ax = plt.subplots(figsize=(14, fig_height))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # Y positions (bottom to top = oldest to newest)
    y_positions = list(range(n))

    for i, event in enumerate(events):
        y = y_positions[i]
        color = SEVERITY_COLORS.get(event.severity, "#6e7681")
        icon = EVENT_TYPE_ICONS.get(event.event_type, "?")

        # Timeline dot
        ax.scatter(
            event.started_at, y,
            s=120, c=color, zorder=5, edgecolors=BG, linewidth=2,
        )

        # Icon text on dot
        ax.text(
            event.started_at, y, icon,
            ha="center", va="center", fontsize=7, fontweight="bold",
            color=BG, zorder=6,
        )

        # Event title (right of dot)
        title = event.title[:60]
        if len(event.title) > 60:
            title += "..."

        ax.text(
            event.started_at + timedelta(hours=3), y,
            f"  {title}",
            va="center", fontsize=9, color=TEXT,
            fontweight="bold" if event.severity in ("critical", "major") else "normal",
        )

        # Article count badge
        if event.article_count > 1:
            ax.text(
                event.started_at + timedelta(hours=2), y + 0.3,
                f"{event.article_count} facts",
                va="center", fontsize=7, color=TEXT_DIM,
            )

    # Vertical timeline line
    if len(events) >= 2:
        ax.plot(
            [events[0].started_at, events[-1].started_at],
            [0, n - 1],
            color=BORDER, linewidth=2, zorder=1,
        )

    # Formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.tick_params(axis="x", colors=TEXT_DIM, labelsize=9)
    ax.tick_params(axis="y", left=False, labelleft=False)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(axis="x", color=BORDER, alpha=0.3, linestyle="--")

    # Title
    market_label = market.upper() if market else "ALL"
    ax.set_title(
        f"Ontology Timeline — {market_label} (last {days}d)",
        color=TEXT, fontsize=14, fontweight="bold", pad=20,
    )

    # Legend
    legend_y = -0.08
    legend_items = [
        ("critical", "Critical"), ("major", "Major"),
        ("moderate", "Moderate"), ("minor", "Minor"),
    ]
    for j, (sev, label) in enumerate(legend_items):
        ax.text(
            0.02 + j * 0.12, legend_y, f"● {label}",
            transform=ax.transAxes, fontsize=8,
            color=SEVERITY_COLORS[sev],
        )

    type_items = [
        ("E", "Earnings"), ("P", "Policy"), ("D", "Deal"), ("M", "Macro"),
    ]
    for j, (icon, label) in enumerate(type_items):
        ax.text(
            0.55 + j * 0.12, legend_y, f"[{icon}] {label}",
            transform=ax.transAxes, fontsize=8, color=TEXT_DIM,
        )

    plt.tight_layout()

    # Save
    if output:
        out_path = Path(output)
    else:
        out_dir = _PROJECT_ROOT / "data" / "timelines"
        out_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        market_suffix = f"_{market}" if market else ""
        out_path = out_dir / f"{today}{market_suffix}_timeline.png"

    fig.savefig(out_path, dpi=180, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ontology event timeline")
    parser.add_argument("--market", choices=["kr", "us", "all"], default="all")
    parser.add_argument("--days", type=int, default=7, help="Lookback days")
    parser.add_argument("--output", help="Output PNG path (default: data/timelines/)")

    args = parser.parse_args()

    try:
        init_db()
    except Exception as e:
        print(f"Error: database init failed — {e}", file=sys.stderr)
        sys.exit(1)

    market = None if args.market == "all" else (
        "korea" if args.market == "kr" else "us"
    )

    path = generate_timeline(market=market, days=args.days, output=args.output)
    print(f"Timeline saved → {path}")


if __name__ == "__main__":
    main()
