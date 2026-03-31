"""Market briefing generator — assembles facts + market data into a briefing.

Produces text output using Jinja2 templates in the style of "오선의 미국 증시 라이브".
Two schedules: morning (06:00 KST) and evening (18:00 KST).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from src.core.config import PROJECT_ROOT
from src.core.logger import get_logger
from src.core.models import NewsFact
from src.storage import NewsFactRepository

logger = get_logger(__name__)

_TEMPLATE_DIR = PROJECT_ROOT / "templates" / "briefing"

# Ticker → readable name for briefing display
_TICKER_TO_NAME: dict[str, str] = {
    # US
    "TSLA": "Tesla", "NVDA": "NVIDIA", "AAPL": "Apple",
    "MSFT": "Microsoft", "AMZN": "Amazon", "GOOGL": "Alphabet",
    "META": "Meta", "PLTR": "Palantir", "COIN": "Coinbase",
    "HOOD": "Robinhood", "AMD": "AMD", "AVGO": "Broadcom",
    "NFLX": "Netflix", "DIS": "Disney", "BA": "Boeing",
    "JPM": "JPMorgan", "GS": "Goldman", "INTC": "Intel",
    "ASML": "ASML", "TSM": "TSMC", "MU": "Micron",
    # KR
    "005930": "삼성전자", "000660": "SK하이닉스", "005380": "현대차",
    "373220": "LG에너지", "000270": "기아", "035420": "NAVER",
    "035720": "카카오", "068270": "셀트리온", "005490": "포스코",
    "352820": "하이브", "034020": "두산에너빌", "009830": "한화솔루션",
    "012450": "한화에어로", "011200": "HMM", "066570": "LG전자",
    "051910": "LG화학", "006400": "삼성SDI", "012330": "현대모비스",
    "105560": "KB금융", "055550": "신한지주", "015760": "한국전력",
    "051600": "한전KPS", "138040": "메리츠", "139480": "이마트",
    "004170": "신세계", "294870": "호반건설", "375500": "DL이앤씨",
    "143240": "사람인", "285130": "SK케미칼", "018620": "우진비앤지",
    "316140": "우리금융", "096770": "SK이노",
    # Crypto
    "BTC": "BTC", "ETH": "ETH", "XRP": "XRP", "SOL": "SOL",
}


def _ticker_label(tickers: list[str]) -> str:
    """Convert ticker list to readable label string."""
    if not tickers:
        return ""
    names = []
    for t in tickers[:3]:
        names.append(_TICKER_TO_NAME.get(t, t))
    return ", ".join(names)


def _clean_claim(claim: str) -> str:
    """Clean up a fact claim for briefing display.

    - Remove reporter bylines (기자 =, 연합뉴스)
    - Remove bracket prefixes ([속보], [마켓PRO])
    - Trim to first meaningful sentence
    - Cap at 80 chars
    """
    import re

    # Remove bylines
    text = re.sub(r"\([^)]*=[^)]*\)\s*[가-힣]+\s*기자\s*=\s*", "", claim)
    text = re.sub(r"\([^)]*뉴스\)\s*", "", text)

    # Remove bracket prefixes
    text = re.sub(r"^\[[^\]]*\]\s*", "", text)

    # Remove inline ticker references like [005930] or (NASDAQ:MSFT)
    text = re.sub(r"\[\d{6}\]", "", text)
    text = re.sub(r"\((?:NYSE|NASDAQ|KRX):[A-Z]+\)", "", text)

    # Remove trailing ellipsis artifacts
    text = re.sub(r"\.{2,}$", "", text)

    # Take first sentence only
    parts = re.split(r"(?<=[.!?。])\s", text, maxsplit=1)
    text = parts[0].strip()

    # If still too long, cut at last comma or space
    if len(text) > 70:
        cut = text[:70].rfind(" ")
        if cut > 30:
            text = text[:cut] + "..."
        else:
            text = text[:67] + "..."

    return text


@dataclass
class BriefingFact:
    """A cleaned fact ready for template display."""

    label: str  # e.g. "삼성전자" or "Tesla"
    claim: str  # cleaned claim text
    numbers: str  # e.g. "$44B, +78%"
    confidence: float


def _prepare_facts(facts: list[NewsFact]) -> list[BriefingFact]:
    """Convert raw NewsFacts to cleaned BriefingFacts."""
    result: list[BriefingFact] = []
    seen: set[str] = set()

    for f in facts:
        claim = _clean_claim(f.claim)
        if claim in seen or len(claim) < 10:
            continue
        seen.add(claim)

        label = _ticker_label(f.tickers)
        if not label and f.entities:
            label = ", ".join(f.entities[:2])

        nums = ""
        raw_vals = f.numbers.get("raw_values", [])
        if raw_vals:
            nums = ", ".join(raw_vals[:3])

        result.append(BriefingFact(
            label=label or "-",
            claim=claim,
            numbers=nums,
            confidence=f.confidence,
        ))

    return result


@dataclass
class IndexSnapshot:
    """A market index data point."""

    name: str
    value: str
    change: str


def _fetch_market_data(tickers: list[str]) -> list[IndexSnapshot]:
    """Fetch current/last market data via yfinance.

    Args:
        tickers: List of Yahoo Finance ticker symbols.

    Returns:
        List of IndexSnapshot with name, value, change.
    """
    try:
        import yfinance as yf
    except ImportError:
        logger.warning("yfinance_not_installed")
        return []

    results: list[IndexSnapshot] = []
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = info.get("lastPrice", 0)
            prev = info.get("previousClose", 0)

            if price and prev:
                change_pct = (price - prev) / prev * 100
                sign = "+" if change_pct >= 0 else ""
                results.append(IndexSnapshot(
                    name=_TICKER_LABELS.get(symbol, symbol),
                    value=f"{price:,.2f}",
                    change=f"{sign}{change_pct:.1f}%",
                ))
        except Exception as e:
            logger.warning("market_data_fetch_error", ticker=symbol, error=str(e))
    return results


# Yahoo Finance symbols → display labels
_TICKER_LABELS: dict[str, str] = {
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ",
    "^DJI": "Dow Jones",
    "^VIX": "VIX",
    "^KS11": "KOSPI",
    "^KQ11": "KOSDAQ",
    "KRW=X": "USD/KRW",
    "CL=F": "WTI 원유",
    "GC=F": "Gold",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
}

_US_INDICES = ["^GSPC", "^IXIC", "^DJI", "^VIX"]
_KR_INDICES = ["^KS11", "^KQ11", "KRW=X"]
_COMMODITIES = ["CL=F", "GC=F"]
_CRYPTO = ["BTC-USD", "ETH-USD"]


def _get_facts_by_market(
    hours: int = 12,
) -> tuple[list[NewsFact], list[NewsFact]]:
    """Get recent facts split by market.

    Returns:
        Tuple of (kr_facts, us_facts), sorted by confidence desc.
    """
    repo = NewsFactRepository()
    kr = repo.get_recent(hours=hours, market="korea", limit=200)
    us = repo.get_recent(hours=hours, market="us", limit=200)

    # Sort by confidence desc, then limit to top items
    kr.sort(key=lambda f: (-f.confidence, f.fact_type))
    us.sort(key=lambda f: (-f.confidence, f.fact_type))

    return kr[:20], us[:20]


def _group_facts_by_type(
    facts: list[NewsFact],
) -> dict[str, list[NewsFact]]:
    """Group facts by fact_type."""
    grouped: dict[str, list[NewsFact]] = {}
    for f in facts:
        grouped.setdefault(f.fact_type, []).append(f)
    return grouped


def _build_standup_section(regime_result: Any) -> str:
    """Investment Standup 섹션 마크다운을 생성한다.

    Args:
        regime_result: RegimeResult 인스턴스 (타입 임포트 순환 방지를 위해 Any).

    Returns:
        스탠드업 섹션 마크다운 문자열.
    """
    regime = regime_result.regime
    confidence_pct = int(regime_result.confidence * 100)
    drivers = regime_result.drivers
    sizing = regime_result.sizing

    regime_label = {
        "RISK_ON": "RISK_ON ✅",
        "NEUTRAL": "NEUTRAL ⚖️",
        "RISK_OFF": "RISK_OFF 🔴",
    }.get(regime, regime)

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 오늘의 레짐: {regime_label} (신뢰도 {confidence_pct}%)",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "오늘 집중할 것:",
    ]

    for i, driver in enumerate(drivers[:3], 1):
        lines.append(f"{i}. {driver}")

    if sizing:
        lines.append("")
        lines.append("포지션 사이징 가이드 (최종 결정은 사용자):")
        sizing_parts = [f"• {ticker}: {int(ratio * 100)}%" for ticker, ratio in sizing.items()]
        lines.append("  " + " | ".join(sizing_parts))

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    return "\n".join(lines)


def generate_briefing(
    schedule: str,
    hours: int = 12,
    fetch_market: bool = True,
    regime_result: Any = None,
) -> str:
    """Generate a market briefing.

    Args:
        schedule: 'morning' or 'evening'.
        hours: Lookback window for facts.
        fetch_market: Whether to fetch live market data via yfinance.
        regime_result: RegimeResult from MarketRegimeEngine. 제공 시 스탠드업
            섹션이 브리핑 맨 앞에 삽입된다. None이면 생략.

    Returns:
        Formatted briefing text.
    """
    now = datetime.now(timezone.utc)
    kr_facts, us_facts = _get_facts_by_market(hours=hours)

    # Fetch market data
    us_market: list[IndexSnapshot] = []
    kr_market: list[IndexSnapshot] = []
    extras: list[IndexSnapshot] = []

    if fetch_market:
        us_market = _fetch_market_data(_US_INDICES)
        kr_market = _fetch_market_data(_KR_INDICES)
        extras = _fetch_market_data(_COMMODITIES + _CRYPTO)

    # Combine all facts and split by category
    all_facts = kr_facts + us_facts

    # Split by type
    by_type: dict[str, list[NewsFact]] = {}
    for f in all_facts:
        by_type.setdefault(f.fact_type, []).append(f)

    # Prepare cleaned facts per category (max 5 each)
    earnings = _prepare_facts(by_type.get("earnings", []))[:5]
    policy = _prepare_facts(by_type.get("policy", []))[:5]
    deals = _prepare_facts(by_type.get("deal", []))[:5]
    events = _prepare_facts(by_type.get("event", []))[:5]
    forecasts = _prepare_facts(by_type.get("forecast", []))[:5]

    # Top movers: numerical with labels (skip noise without entities)
    numericals = _prepare_facts(by_type.get("numerical", []))
    top_movers = [f for f in numericals if f.label != "-"][:8]

    total = len(earnings) + len(policy) + len(deals) + len(events) + len(forecasts) + len(top_movers)

    # Template context
    context: dict[str, Any] = {
        "date": now.strftime("%Y-%m-%d"),
        "time": "06:00" if schedule == "morning" else "18:00",
        "total_facts": total,
        "earnings_count": len(earnings),
        "policy_count": len(policy),
        "deal_count": len(deals),
        "earnings_facts": earnings,
        "policy_facts": policy,
        "deal_facts": deals,
        "event_facts": events,
        "forecast_facts": forecasts,
        "top_movers": top_movers,
        "schedule": [],  # Economic calendar — manual or future integration
    }

    if schedule == "morning":
        context["us_market"] = us_market + extras
        context["kr_premarket"] = kr_market
    else:
        context["kr_market"] = kr_market
        context["us_premarket"] = us_market + extras

    # Render template
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(f"{schedule}.j2")
    briefing_text = template.render(**context)

    # 스탠드업 섹션: regime_result가 있으면 브리핑 맨 앞에 삽입
    if regime_result is not None:
        standup = _build_standup_section(regime_result)
        briefing_text = standup + briefing_text

    return briefing_text


def save_briefing(text: str, schedule: str) -> Path:
    """Save briefing to data/briefings/ directory.

    Args:
        text: Rendered briefing text.
        schedule: 'morning' or 'evening'.

    Returns:
        Path to saved file.
    """
    now = datetime.now(timezone.utc)
    output_dir = PROJECT_ROOT / "data" / "briefings"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{now.strftime('%Y-%m-%d')}_{schedule}.md"
    path = output_dir / filename
    path.write_text(text, encoding="utf-8")
    return path


def generate_naver_html(
    schedule: str,
    hours: int = 12,
    fetch_market: bool = True,
    regime_result: Any = None,
) -> str:
    """Generate briefing as Naver blog-ready HTML.

    Uses inline CSS only (SmartEditor ONE compatible).
    Copy from Chrome → paste into Naver blog editor.

    Args:
        schedule: 'morning' or 'evening'.
        hours: Lookback window for facts.
        fetch_market: Whether to fetch live market data.
        regime_result: RegimeResult from MarketRegimeEngine. 제공 시 스탠드업
            섹션이 HTML 맨 앞에 삽입된다.

    Returns:
        Complete HTML string.
    """
    now = datetime.now(timezone.utc)
    kr_facts, us_facts = _get_facts_by_market(hours=hours)

    # Fetch market data
    us_market: list[IndexSnapshot] = []
    kr_market: list[IndexSnapshot] = []
    extras: list[IndexSnapshot] = []

    if fetch_market:
        us_market = _fetch_market_data(_US_INDICES)
        kr_market = _fetch_market_data(_KR_INDICES)
        extras = _fetch_market_data(_COMMODITIES + _CRYPTO)

    # Prepare facts
    all_facts = kr_facts + us_facts
    by_type: dict[str, list[NewsFact]] = {}
    for f in all_facts:
        by_type.setdefault(f.fact_type, []).append(f)

    categories = [
        ("실적", _prepare_facts(by_type.get("earnings", []))[:5]),
        ("정책/매크로", _prepare_facts(by_type.get("policy", []))[:5]),
        ("딜/투자", _prepare_facts(by_type.get("deal", []))[:5]),
        ("이벤트", _prepare_facts(by_type.get("event", []))[:5]),
        ("전망", _prepare_facts(by_type.get("forecast", []))[:5]),
    ]

    numericals = _prepare_facts(by_type.get("numerical", []))
    top_movers = [f for f in numericals if f.label != "-"][:8]
    if top_movers:
        categories.append(("주요 수치", top_movers))

    # Market sections
    if schedule == "morning":
        primary_label = "미국 마감"
        primary_data = us_market + extras
        secondary_label = "한국 프리마켓"
        secondary_data = kr_market
        subtitle = "한국시장 시작 준비 + 미국시장 마감 정리"
    else:
        primary_label = "한국 마감"
        primary_data = kr_market
        secondary_label = "미국 프리마켓"
        secondary_data = us_market + extras
        subtitle = "미국시장 시작 준비 + 한국시장 마감 정리"

    # Build HTML
    S = {
        "wrap": (
            "font-size:16px; line-height:2.0; color:#333; "
            "word-break:keep-all; text-align:left; "
            "font-family:'나눔고딕','Nanum Gothic',sans-serif; "
            "max-width:720px; margin:0 auto; padding:0 16px;"
        ),
        "h1": (
            "font-size:26px; font-weight:700; color:#222; "
            "margin:48px 0 20px; padding-bottom:12px; "
            "border-bottom:2px solid #333; line-height:1.6;"
        ),
        "h2": (
            "font-size:21px; font-weight:700; color:#222; "
            "margin:40px 0 16px; line-height:1.6;"
        ),
        "h3": (
            "font-size:19px; font-weight:700; color:#333; "
            "margin:32px 0 12px; line-height:1.6;"
        ),
        "p": "margin:0 0 20px; line-height:2.0;",
        "table": (
            "border-collapse:collapse; width:100%; "
            "font-size:15px; margin:0 0 20px;"
        ),
        "th": (
            "background:#f7f8fa; font-weight:700; color:#222; "
            "text-align:left; padding:10px 14px; "
            "border:1px solid #e0e0e0;"
        ),
        "td": (
            "color:#444; padding:9px 14px; "
            "border:1px solid #e0e0e0;"
        ),
        "td_even": (
            "color:#444; padding:9px 14px; "
            "border:1px solid #e0e0e0; background:#fafbfc;"
        ),
        "hr": "border:none; border-top:1px solid #ddd; margin:36px 0;",
        "tag": (
            "display:inline-block; background:#f0f4ff; color:#4a6fa5; "
            "font-size:13px; padding:2px 8px; border-radius:4px; "
            "margin-right:4px;"
        ),
        "disc": (
            "margin-top:40px; padding:14px 18px; background:#f9f9f9; "
            "border:1px solid #eee; border-radius:6px; "
            "font-size:13px; color:#888; line-height:1.7;"
        ),
    }

    lines: list[str] = []
    lines.append('<meta charset="utf-8">')
    lines.append(f'<div style="{S["wrap"]}">')

    # Title
    date_str = now.strftime("%Y-%m-%d")
    time_str = "06:00" if schedule == "morning" else "18:00"
    lines.append(f'<h1 style="{S["h1"]}">시황 브리핑 | {date_str} {time_str}</h1>')
    lines.append(f'<p style="{S["p"]}"><strong>{subtitle}</strong></p>')

    # Primary market table
    if primary_data:
        lines.append(f'<h2 style="{S["h2"]}">▣ {primary_label}</h2>')
        lines.append(f'<table style="{S["table"]}">')
        lines.append(
            f'<tr><th style="{S["th"]}">지수</th>'
            f'<th style="{S["th"]}">현재가</th>'
            f'<th style="{S["th"]}">변동</th></tr>'
        )
        for i, idx in enumerate(primary_data):
            td = S["td_even"] if i % 2 == 1 else S["td"]
            color = "#c62828" if idx.change.startswith("-") else "#2e7d32"
            lines.append(
                f'<tr><td style="{td}">{idx.name}</td>'
                f'<td style="{td}">{idx.value}</td>'
                f'<td style="{td}; color:{color}; font-weight:700;">'
                f'{idx.change}</td></tr>'
            )
        lines.append("</table>")

    # Secondary market table
    if secondary_data:
        lines.append(f'<h2 style="{S["h2"]}">▣ {secondary_label}</h2>')
        lines.append(f'<table style="{S["table"]}">')
        lines.append(
            f'<tr><th style="{S["th"]}">지수</th>'
            f'<th style="{S["th"]}">현재가</th>'
            f'<th style="{S["th"]}">변동</th></tr>'
        )
        for i, idx in enumerate(secondary_data):
            td = S["td_even"] if i % 2 == 1 else S["td"]
            color = "#c62828" if idx.change.startswith("-") else "#2e7d32"
            lines.append(
                f'<tr><td style="{td}">{idx.name}</td>'
                f'<td style="{td}">{idx.value}</td>'
                f'<td style="{td}; color:{color}; font-weight:700;">'
                f'{idx.change}</td></tr>'
            )
        lines.append("</table>")

    # Fact categories
    for cat_name, facts in categories:
        if not facts:
            continue
        lines.append(f'<p style="{S["p"]}">&nbsp;</p>')
        lines.append(f'<h3 style="{S["h3"]}">━━ {cat_name}</h3>')
        for f in facts:
            nums = f" ({f.numbers})" if f.numbers else ""
            lines.append(
                f'<p style="{S["p"]}">'
                f'<span style="{S["tag"]}">{f.label}</span> '
                f'{f.claim}'
                f'<span style="color:#888; font-size:14px;">{nums}</span>'
                f"</p>"
            )

    # Disclaimer
    lines.append(f'<hr style="{S["hr"]}">')
    lines.append(
        f'<div style="{S["disc"]}">'
        f"이 브리핑은 자동 수집된 뉴스 팩트를 정리한 것이며, "
        f"특정 종목의 매수·매도를 권유하지 않습니다. "
        f"모든 투자 판단과 책임은 본인에게 있습니다."
        f"</div>"
    )

    lines.append("</div>")

    html = "\n".join(lines)

    # 스탠드업 섹션: regime_result가 있으면 HTML 맨 앞에 삽입
    if regime_result is not None:
        standup_md = _build_standup_section(regime_result)
        # 간단한 pre 태그로 감싸서 HTML에 삽입
        standup_html = (
            '<div style="background:#f0f7ff; border-left:4px solid #2563eb; '
            'padding:16px 20px; margin-bottom:20px; font-family:monospace; '
            'white-space:pre-wrap; font-size:14px; line-height:1.6;">'
            + standup_md.replace("<", "&lt;").replace(">", "&gt;")
            + "</div>"
        )
        html = standup_html + html

    return html


def save_naver_html(html: str, schedule: str) -> Path:
    """Save Naver HTML to data/briefings/ directory.

    Args:
        html: Rendered HTML string.
        schedule: 'morning' or 'evening'.

    Returns:
        Path to saved file.
    """
    now = datetime.now(timezone.utc)
    output_dir = PROJECT_ROOT / "data" / "briefings"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{now.strftime('%Y-%m-%d')}_{schedule}_naver.html"
    path = output_dir / filename
    path.write_text(html, encoding="utf-8")
    return path
