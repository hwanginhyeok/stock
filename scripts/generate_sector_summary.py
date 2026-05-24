#!/usr/bin/env python3
"""
2026 Q1 미국 실적 시즌 섹터별 종합 분석 HTML 생성기.

입력: docs/earnings/{TICKER}_2026Q1.html (48개)
출력: docs/earnings/2026Q1_sector_summary.html

기준: EPS surprise % = (actual - estimate) / |estimate| * 100
- 섹터별 대장: surprise % 최고
- 섹터별 약자: surprise % 최저
- 종목 < 2개면 단독 표시

GICS 11분류 영어 표준화. 한국어 자유 텍스트는 키워드 휴리스틱으로 매핑.

재실행 가능 (idempotent). cron 등록은 PM이 결정.
"""

from __future__ import annotations

import html as html_lib
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Tag

EARNINGS_DIR = Path("/home/window11/stock/docs/earnings")
OUTPUT_FILE = EARNINGS_DIR / "2026Q1_sector_summary.html"

# GICS 11 표준 분류 (영어)
GICS_SECTORS = [
    "Technology",
    "Communication Services",
    "Consumer Cyclical",
    "Consumer Defensive",
    "Healthcare",
    "Financial Services",
    "Industrials",
    "Energy",
    "Utilities",
    "Real Estate",
    "Basic Materials",
]

# 키워드 휴리스틱 — 한국어/자유 텍스트 → GICS 11
# 첫 매치 우선. 순서 중요 (좁은 키워드부터 먼저).
KOREAN_TO_GICS_RULES: list[tuple[str, str]] = [
    # Technology — 반도체, 소프트웨어, SaaS, AI/로봇
    ("반도체", "Technology"),
    ("소프트웨어", "Technology"),
    ("saas", "Technology"),
    ("ai", "Technology"),  # "AI & 로봇" 단독 시
    # Communication Services — 통신, 미디어, 소셜
    ("통신서비스", "Communication Services"),
    ("통신", "Communication Services"),
    ("소셜미디어", "Communication Services"),
    ("미디어", "Communication Services"),
    ("스트리밍", "Communication Services"),
    ("광고", "Communication Services"),
    ("검색", "Communication Services"),
    # Financial Services — 금융, 결제, 자본시장
    ("금융", "Financial Services"),
    ("결제", "Financial Services"),
    ("자본시장", "Financial Services"),
    ("보험", "Financial Services"),
    # Consumer Cyclical — 자동차, 이동성, 여행, 레스토랑
    ("자동차", "Consumer Cyclical"),
    ("이동성", "Consumer Cyclical"),
    ("여행", "Consumer Cyclical"),
    ("ota", "Consumer Cyclical"),
    ("레스토랑", "Consumer Cyclical"),
    ("커피", "Consumer Cyclical"),
    ("이커머스", "Consumer Cyclical"),
    # Consumer Defensive — 식음료
    ("음료", "Consumer Defensive"),
    ("식품", "Consumer Defensive"),
    # Industrials — 산업재, 물류, 항공우주
    ("산업재", "Industrials"),
    ("물류", "Industrials"),
    ("항공우주", "Industrials"),
    ("방산", "Industrials"),
    # Energy
    ("에너지", "Energy"),
    # Healthcare
    ("헬스케어", "Healthcare"),
    ("바이오", "Healthcare"),
    ("제약", "Healthcare"),
    # 일반 카테고리 (마지막 안전망)
    ("기술", "Technology"),
    ("클라우드", "Technology"),
    ("소비재", "Consumer Cyclical"),  # 모호하지만 일반적으로 cyclical
]

# 영어 → 영어 정규화 (이미 채워진 GICS 값)
ENGLISH_GICS_NORMALIZE = {s.lower(): s for s in GICS_SECTORS}


@dataclass
class EarningsRow:
    ticker: str
    company: str
    raw_sector: str
    sector: Optional[str]
    verdict: Optional[str]  # beat / miss / mixed
    verdict_text: str
    eps_actual: Optional[float]
    eps_estimate: Optional[float]
    eps_surprise_pct: Optional[float]
    notes: list[str] = field(default_factory=list)

    @property
    def has_eps_data(self) -> bool:
        return self.eps_surprise_pct is not None

    @property
    def file_link(self) -> str:
        return f"{self.ticker}_2026Q1.html"


def map_sector(raw: str) -> tuple[Optional[str], str]:
    """raw sector 문자열 → GICS 11 표준명 + 매핑 사유.

    Returns (gics_name, reason). gics_name이 None이면 미매핑.
    """
    if not raw or not raw.strip():
        return None, "EMPTY"

    cleaned = raw.strip()
    # HTML entity 정리
    cleaned = html_lib.unescape(cleaned)

    # 1) 영어 GICS 정확 매치
    if cleaned.lower() in ENGLISH_GICS_NORMALIZE:
        return ENGLISH_GICS_NORMALIZE[cleaned.lower()], "EXACT"

    # 2) 한국어 키워드 휴리스틱
    cl = cleaned.lower()
    for keyword, gics in KOREAN_TO_GICS_RULES:
        if keyword.lower() in cl:
            return gics, f"KEYWORD:{keyword}"

    return None, "UNMATCHED"


def parse_eps(num_card: Tag) -> tuple[Optional[float], Optional[float]]:
    """num-card 1개에서 actual EPS, estimate EPS 추출.

    형식 가정:
      <div class="label">희석 EPS</div>
      <div class="value">$0.60</div>
      <div class="compare">컨센서스: $0.52 <span class="beat-tag">BEAT</span></div>
    """
    value_div = num_card.find(class_="value")
    if not value_div:
        return None, None

    actual = _parse_dollar(value_div.get_text(strip=True))

    # compare 중 "컨센서스" 포함 라인 찾기
    estimate = None
    for cmp in num_card.find_all(class_="compare"):
        text = cmp.get_text(separator=" ", strip=True)
        if "컨센서스" in text or "Consensus" in text.lower() or "consensus" in text:
            estimate = _parse_consensus(text)
            break

    return actual, estimate


def _parse_dollar(s: str) -> Optional[float]:
    """문자열에서 첫 번째 달러 금액 추출. -$0.20, $2.78 등."""
    if not s or "N/A" in s or "None" in s:
        return None
    m = re.search(r"(-?)\$\s*(-?)([\d,]+\.?\d*)", s)
    if not m:
        # 달러 기호 없이 숫자만 있는 경우
        m2 = re.search(r"(-?[\d,]+\.?\d*)", s)
        if m2:
            try:
                return float(m2.group(1).replace(",", ""))
            except ValueError:
                return None
        return None
    sign1, sign2, num = m.group(1), m.group(2), m.group(3)
    sign = "-" if (sign1 == "-" or sign2 == "-") else ""
    try:
        return float(sign + num.replace(",", ""))
    except ValueError:
        return None


def _parse_consensus(text: str) -> Optional[float]:
    """컨센서스 라인에서 첫 숫자 추출. 범위면 중간값.

    예: "컨센서스: $0.52" → 0.52
        "컨센서스: $0.00~$0.01" → 0.005
        "컨센서스: -$0.68~-$0.75" → -0.715
        "컨센서스: $0.46 ~ $0.56" → 0.51
    """
    if "N/A" in text or "None" in text:
        return None

    # 범위 패턴 우선 (—, ~, -로 연결된 두 달러값)
    range_m = re.search(
        r"(-?\$\s*-?[\d,]+\.?\d*)\s*[~–—-]\s*(-?\$\s*-?[\d,]+\.?\d*)", text
    )
    if range_m:
        v1 = _parse_dollar(range_m.group(1))
        v2 = _parse_dollar(range_m.group(2))
        if v1 is not None and v2 is not None:
            return (v1 + v2) / 2
        return v1 if v1 is not None else v2

    # 단일 값
    return _parse_dollar(text)


def find_eps_card(soup: BeautifulSoup) -> Optional[Tag]:
    """numbers-grid 내 num-card 중 EPS 라벨 카드 찾기.

    우선순위: '희석 EPS' > '조정 EPS' > '비교 EPS' > 'EPS' 포함
    """
    candidates: list[tuple[int, Tag]] = []
    for card in soup.find_all(class_="num-card"):
        label = card.find(class_="label")
        if not label:
            continue
        label_text = label.get_text(strip=True)
        if "EPS" not in label_text:
            continue
        # next-q-item 등 가이던스 카드 제외 (num-card 클래스에만 한정되므로 OK)
        # 우선순위 점수
        if "희석 EPS" == label_text or "희석 EPS (GAAP)" == label_text:
            priority = 1
        elif "GAAP 희석 EPS" == label_text:
            priority = 1
        elif "Non-GAAP 희석 EPS" == label_text or "Adj. EPS (희석)" == label_text:
            priority = 2
        elif "조정 EPS" in label_text or "Adj. EPS" in label_text:
            priority = 3
        elif "Non-GAAP EPS" == label_text:
            priority = 3
        elif "비교 EPS" in label_text:
            priority = 4
        else:
            priority = 5
        candidates.append((priority, card))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def parse_earnings_file(path: Path) -> EarningsRow:
    ticker = path.stem.replace("_2026Q1", "")
    html_text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_text, "html.parser")

    # 회사명: <title>TICKER | Company Name Q1 2026 ...</title>
    title = soup.find("title")
    company = ""
    if title:
        m = re.match(r"^[A-Z.]+\s*\|\s*(.+?)\s*Q1 2026", title.get_text())
        if m:
            company = m.group(1).strip()
    # fallback: hero h1
    if not company:
        h1 = soup.select_one(".hero h1")
        if h1:
            company = h1.get_text(strip=True)

    # 섹터: hero meta-row 내 "섹터:" 패턴
    raw_sector = ""
    meta_row = soup.select_one(".hero .meta-row")
    if meta_row:
        for span in meta_row.find_all("span"):
            txt = span.get_text(strip=True)
            if txt.startswith("섹터:"):
                raw_sector = txt[len("섹터:"):].strip()
                break
    sector, sector_reason = map_sector(raw_sector)

    # Verdict: 첫 번째 .verdict
    verdict = None
    verdict_text = ""
    v = soup.select_one("div.verdict")
    if v:
        classes = v.get("class", [])
        for c in classes:
            if c in {"beat", "miss", "mixed"}:
                verdict = c
                break
        verdict_text = v.get_text(strip=True)

    # EPS
    eps_card = find_eps_card(soup)
    eps_actual, eps_estimate = (None, None)
    if eps_card:
        eps_actual, eps_estimate = parse_eps(eps_card)

    surprise = None
    if eps_actual is not None and eps_estimate is not None and eps_estimate != 0:
        # 분모가 매우 작으면 (|estimate| < $0.05) surprise %가 의미 없이 폭주.
        # 일관된 비교를 위해 +/- 500%로 캡. 별도 노트 추가.
        raw = (eps_actual - eps_estimate) / abs(eps_estimate) * 100
        if abs(eps_estimate) < 0.05 and abs(raw) > 500:
            surprise = 500 if raw > 0 else -500
            notes_pending = ["surprise_capped_500pct(low_estimate_base)"]
        else:
            surprise = raw
            notes_pending = []
    else:
        notes_pending = []

    notes: list[str] = []
    if not raw_sector:
        notes.append("sector_empty")
    if sector is None and raw_sector:
        notes.append(f"sector_unmatched:{raw_sector}")
    if not company:
        notes.append("company_empty")
    if eps_card is None:
        notes.append("eps_card_missing")
    elif eps_actual is None:
        notes.append("eps_actual_missing")
    elif eps_estimate is None:
        notes.append("eps_estimate_missing")
    notes.extend(notes_pending)

    return EarningsRow(
        ticker=ticker,
        company=company or "(no name)",
        raw_sector=raw_sector,
        sector=sector,
        verdict=verdict,
        verdict_text=verdict_text,
        eps_actual=eps_actual,
        eps_estimate=eps_estimate,
        eps_surprise_pct=surprise,
        notes=notes,
    )


def collect_rows() -> list[EarningsRow]:
    files = sorted(EARNINGS_DIR.glob("*_2026Q1.html"))
    rows = []
    for f in files:
        try:
            rows.append(parse_earnings_file(f))
        except Exception as e:
            print(f"  WARN: {f.name} 파싱 실패: {e}")
    return rows


def group_by_sector(rows: list[EarningsRow]) -> dict[str, list[EarningsRow]]:
    grouped: dict[str, list[EarningsRow]] = {}
    for r in rows:
        if r.sector is None:
            grouped.setdefault("(Unclassified)", []).append(r)
        else:
            grouped.setdefault(r.sector, []).append(r)
    return grouped


def pick_leader_laggard(rows: list[EarningsRow]) -> tuple[Optional[EarningsRow], Optional[EarningsRow]]:
    """EPS surprise % 기준 대장/약자.

    EPS 데이터 없는 종목은 후보에서 제외.
    """
    candidates = [r for r in rows if r.has_eps_data]
    if not candidates:
        return None, None
    sorted_rows = sorted(candidates, key=lambda r: r.eps_surprise_pct, reverse=True)
    leader = sorted_rows[0]
    laggard = sorted_rows[-1] if len(sorted_rows) > 1 else None
    return leader, laggard


def verdict_counts(rows: list[EarningsRow]) -> dict[str, int]:
    counts = {"beat": 0, "miss": 0, "mixed": 0, "unknown": 0}
    for r in rows:
        if r.verdict in counts:
            counts[r.verdict] += 1
        else:
            counts["unknown"] += 1
    return counts


def render_html(rows: list[EarningsRow], grouped: dict[str, list[EarningsRow]]) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(rows)
    with_eps = sum(1 for r in rows if r.has_eps_data)
    overall_counts = verdict_counts(rows)
    sector_count = sum(1 for k in grouped if k in GICS_SECTORS)

    # 섹터 출력 순서: GICS 정의 순서 유지, 비어있으면 생략
    ordered_sectors = [s for s in GICS_SECTORS if s in grouped and grouped[s]]
    if "(Unclassified)" in grouped:
        ordered_sectors.append("(Unclassified)")

    css = _CSS

    parts: list[str] = []
    parts.append(f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026 Q1 실적 시즌 섹터 종합 | Earnings Sector Summary</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>

<!-- ===== HERO ===== -->
<div class="hero">
  <div class="hero-inner">
    <div class="ticker">2026 Q1 EARNINGS SEASON</div>
    <h1>섹터별 종합 분석</h1>
    <div class="company-kr">US Earnings — Sector Summary</div>
    <div class="subtitle">대형주 {total}종목 · {sector_count}개 GICS 섹터 · EPS 서프라이즈 기반 대장/약자 추출</div>
    <div class="meta-row">
      <span>시즌 기간: 2026-04-29 ~ 2026-05-22</span>
      <span>|</span>
      <span>분석 종목: {total}</span>
      <span>|</span>
      <span>EPS 데이터: {with_eps}/{total}</span>
    </div>
    <div class="verdict-row">
      <span class="verdict beat">BEAT {overall_counts['beat']}</span>
      <span class="verdict mixed">MIXED {overall_counts['mixed']}</span>
      <span class="verdict miss">MISS {overall_counts['miss']}</span>
      {f'<span class="verdict unknown">UNKNOWN {overall_counts["unknown"]}</span>' if overall_counts['unknown'] else ''}
    </div>
  </div>
</div>

<div class="container">

<!-- ===== 섹터 분포 ===== -->
<div class="section">
  <div class="section-label">00 &mdash; OVERVIEW</div>
  <h2>섹터 분포</h2>
  <table>
    <thead><tr><th>섹터</th><th>종목 수</th><th>BEAT</th><th>MIXED</th><th>MISS</th><th>EPS 평균 서프라이즈</th></tr></thead>
    <tbody>
""")
    for sec in ordered_sectors:
        secrows = grouped[sec]
        c = verdict_counts(secrows)
        eps_vals = [r.eps_surprise_pct for r in secrows if r.has_eps_data]
        avg = sum(eps_vals) / len(eps_vals) if eps_vals else None
        avg_str = f"{avg:+.1f}%" if avg is not None else "—"
        avg_cls = "positive" if (avg is not None and avg > 0) else ("negative" if (avg is not None and avg < 0) else "")
        parts.append(
            f"      <tr><td><strong>{html_lib.escape(sec)}</strong></td>"
            f"<td class='mono'>{len(secrows)}</td>"
            f"<td class='mono positive'>{c['beat']}</td>"
            f"<td class='mono'>{c['mixed']}</td>"
            f"<td class='mono negative'>{c['miss']}</td>"
            f"<td class='mono {avg_cls}'>{avg_str}</td></tr>\n"
        )
    parts.append("""    </tbody>
  </table>
</div>
""")

    # 섹터별 상세
    for idx, sec in enumerate(ordered_sectors, start=1):
        secrows = grouped[sec]
        c = verdict_counts(secrows)
        leader, laggard = pick_leader_laggard(secrows)

        parts.append(f"""
<!-- ===== {sec} ===== -->
<div class="section">
  <div class="section-label">{idx:02d} &mdash; SECTOR</div>
  <h2>{html_lib.escape(sec)} <span class="count-pill">{len(secrows)} 종목</span></h2>
  <div class="badge-row">
    <span class="kw-tag bullish">BEAT {c['beat']}</span>
    <span class="kw-tag neutral-tag">MIXED {c['mixed']}</span>
    <span class="kw-tag bearish">MISS {c['miss']}</span>
  </div>
""")

        # 대장/약자 카드
        if leader is None and laggard is None:
            parts.append('  <div class="empty-note">EPS 서프라이즈 데이터 없음 — 대장/약자 판정 불가</div>\n')
        elif leader is not None and (laggard is None or laggard.ticker == leader.ticker):
            # 단독
            parts.append('  <div class="lead-grid">\n')
            parts.append(_render_lead_card(leader, "단독", "solo"))
            parts.append('  </div>\n')
        else:
            parts.append('  <div class="lead-grid">\n')
            parts.append(_render_lead_card(leader, "대장", "leader"))
            parts.append(_render_lead_card(laggard, "약자", "laggard"))
            parts.append('  </div>\n')

        # 나머지 종목 표
        other_rows = [r for r in secrows if not _is_highlighted(r, leader, laggard)]
        if other_rows:
            other_rows.sort(key=lambda r: (-(r.eps_surprise_pct or -1e9)))
            parts.append("""  <h3>섹터 내 전 종목</h3>
  <table>
    <thead><tr><th>티커</th><th>회사명</th><th>Verdict</th><th>EPS Actual</th><th>EPS Est</th><th>Surprise</th><th>링크</th></tr></thead>
    <tbody>
""")
            # 전 종목 모두 노출 (대장/약자도 포함)
            all_sorted = sorted(
                secrows,
                key=lambda r: -(r.eps_surprise_pct if r.eps_surprise_pct is not None else -1e9),
            )
            for r in all_sorted:
                parts.append(_render_table_row(r))
            parts.append("    </tbody>\n  </table>\n")
        else:
            # 종목 1~2개 — 표 생략하지 않고 모두 표시
            parts.append("""  <h3>섹터 내 전 종목</h3>
  <table>
    <thead><tr><th>티커</th><th>회사명</th><th>Verdict</th><th>EPS Actual</th><th>EPS Est</th><th>Surprise</th><th>링크</th></tr></thead>
    <tbody>
""")
            for r in secrows:
                parts.append(_render_table_row(r))
            parts.append("    </tbody>\n  </table>\n")

        parts.append("</div>\n")

    # 매핑 내역 + 누락 노트
    parts.append("""
<!-- ===== 매핑 내역 ===== -->
<div class="section">
  <div class="section-label">99 &mdash; APPENDIX</div>
  <h2>섹터 매핑 내역 (원본 → GICS)</h2>
  <table>
    <thead><tr><th>티커</th><th>원본 섹터 텍스트</th><th>GICS 매핑</th></tr></thead>
    <tbody>
""")
    for r in sorted(rows, key=lambda x: x.ticker):
        mapped = r.sector if r.sector else "<span class='negative'>UNMATCHED</span>"
        raw_display = html_lib.escape(r.raw_sector) if r.raw_sector else "<span class='text-muted'>(empty)</span>"
        parts.append(
            f"      <tr><td class='mono'>{r.ticker}</td>"
            f"<td>{raw_display}</td>"
            f"<td>{mapped}</td></tr>\n"
        )
    parts.append("    </tbody>\n  </table>\n")

    # 누락/이상 데이터
    issues = [r for r in rows if r.notes]
    if issues:
        parts.append("""
  <h3>데이터 누락 / 이상 노트</h3>
  <table>
    <thead><tr><th>티커</th><th>이슈</th></tr></thead>
    <tbody>
""")
        for r in issues:
            parts.append(
                f"      <tr><td class='mono'>{r.ticker}</td>"
                f"<td class='text-muted'>{html_lib.escape(', '.join(r.notes))}</td></tr>\n"
            )
        parts.append("    </tbody>\n  </table>\n")

    parts.append(f"""</div>

<div class="footer">
  데이터 소스: docs/earnings/*_2026Q1.html ({total}종목) &mdash;
  생성: {generated_at} &mdash;
  대장/약자 기준: EPS 서프라이즈 % &mdash;
  MACROHARD / Be:Analogue<br>
  <span style="font-size:11px;">⚠️ 면책: 본 자료는 정보 제공 목적이며 투자 권유가 아님. EPS 컨센서스/실적 수치는 각 종목 분석 HTML 기반.</span>
</div>

</div>
</body>
</html>
""")
    return "".join(parts)


def _is_highlighted(r: EarningsRow, leader, laggard) -> bool:
    if leader and r.ticker == leader.ticker:
        return True
    if laggard and r.ticker == laggard.ticker:
        return True
    return False


def _render_lead_card(r: EarningsRow, label: str, kind: str) -> str:
    """대장/약자 큰 카드.

    kind: 'leader' / 'laggard' / 'solo'
    """
    cls = {
        "leader": "lead-card leader",
        "laggard": "lead-card laggard",
        "solo": "lead-card solo",
    }[kind]
    surprise_str = f"{r.eps_surprise_pct:+.1f}%" if r.has_eps_data else "—"
    surprise_cls = "positive" if (r.eps_surprise_pct and r.eps_surprise_pct >= 0) else "negative"
    verdict_html = ""
    if r.verdict:
        verdict_html = f'<span class="verdict {r.verdict}">{r.verdict.upper()}</span>'
    comment = html_lib.escape(_truncate(r.verdict_text, 220))
    return f"""    <div class="{cls}">
      <div class="lead-label">{html_lib.escape(label)}</div>
      <div class="lead-ticker">{html_lib.escape(r.ticker)}</div>
      <div class="lead-company">{html_lib.escape(r.company)}</div>
      <div class="lead-surprise {surprise_cls}">{surprise_str}</div>
      <div class="lead-meta">
        EPS Actual: <span class="mono">{_fmt_eps(r.eps_actual)}</span> &nbsp;|&nbsp;
        Est: <span class="mono">{_fmt_eps(r.eps_estimate)}</span>
      </div>
      <div class="lead-verdict">{verdict_html}</div>
      <div class="lead-comment">{comment}</div>
      <a class="lead-link" href="{r.file_link}">→ 상세 보기</a>
    </div>
"""


def _render_table_row(r: EarningsRow) -> str:
    surprise_str = f"{r.eps_surprise_pct:+.1f}%" if r.has_eps_data else "—"
    surprise_cls = "positive" if (r.eps_surprise_pct and r.eps_surprise_pct >= 0) else ("negative" if r.has_eps_data else "")
    verdict_html = (
        f'<span class="verdict-mini {r.verdict}">{r.verdict.upper()}</span>'
        if r.verdict
        else '<span class="text-muted">—</span>'
    )
    return (
        f"      <tr>"
        f"<td class='mono'>{html_lib.escape(r.ticker)}</td>"
        f"<td>{html_lib.escape(r.company)}</td>"
        f"<td>{verdict_html}</td>"
        f"<td class='mono'>{_fmt_eps(r.eps_actual)}</td>"
        f"<td class='mono'>{_fmt_eps(r.eps_estimate)}</td>"
        f"<td class='mono {surprise_cls}'>{surprise_str}</td>"
        f"<td><a class='ticker-link' href='{r.file_link}'>상세 →</a></td>"
        f"</tr>\n"
    )


def _fmt_eps(v: Optional[float]) -> str:
    if v is None:
        return "—"
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(v):.2f}"


def _truncate(s: str, n: int) -> str:
    s = s.strip()
    if len(s) <= n:
        return s
    return s[:n].rstrip() + "…"


_CSS = """
  :root {
    --bg: #0a0a0a; --surface: #141414; --surface2: #1c1c1c;
    --border: #2a2a2a; --text: #e8e8e8; --text-dim: #888; --text-muted: #555;
    --accent: #0071CE; --accent-dim: #0071CE33;
    --red: #ff4d4d; --red-dim: #ff4d4d22;
    --yellow: #ffc107; --blue: #4da6ff;
    --purple: #b388ff; --purple-dim: #b388ff22;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--text); font-family:'IBM Plex Sans KR',-apple-system,sans-serif; font-size:15px; line-height:1.7; }
  a { color:var(--accent); text-decoration:none; }
  a:hover { text-decoration:underline; }

  .hero { background:linear-gradient(135deg,#0071CE15,#0a0a0a 60%); border-bottom:1px solid var(--border); padding:60px 40px 40px; }
  .hero-inner { max-width:1100px; margin:0 auto; }
  .hero .ticker { font-family:'IBM Plex Mono',monospace; font-size:14px; color:var(--accent); letter-spacing:2px; text-transform:uppercase; margin-bottom:8px; }
  .hero h1 { font-family:'Playfair Display',serif; font-size:48px; font-weight:900; line-height:1.2; margin-bottom:4px; }
  .hero .company-kr { font-size:20px; color:var(--text-dim); font-weight:400; margin-bottom:12px; font-family:'IBM Plex Mono',monospace; letter-spacing:1px; }
  .hero .subtitle { font-size:17px; color:var(--text-dim); font-weight:300; }
  .hero .meta-row { display:flex; gap:24px; margin-top:20px; font-size:13px; color:var(--text-muted); font-family:'IBM Plex Mono',monospace; flex-wrap:wrap; }
  .verdict { display:inline-flex; align-items:center; gap:8px; padding:6px 16px; border-radius:4px; font-size:13px; font-weight:600; font-family:'IBM Plex Mono',monospace; }
  .verdict.miss { background:var(--red-dim); color:var(--red); border:1px solid #ff4d4d44; }
  .verdict.beat { background:var(--accent-dim); color:var(--accent); border:1px solid #0071CE44; }
  .verdict.mixed { background:#ffc10722; color:var(--yellow); border:1px solid #ffc10744; }
  .verdict.unknown { background:#55555522; color:var(--text-dim); border:1px solid #55555544; }
  .verdict-row { display:flex; gap:12px; margin-top:20px; flex-wrap:wrap; }

  .container { max-width:1100px; margin:0 auto; padding:40px; }
  .section { margin-bottom:64px; }
  .section-label { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:3px; text-transform:uppercase; color:var(--accent); margin-bottom:8px; }
  .section h2 { font-family:'Playfair Display',serif; font-size:30px; font-weight:700; margin-bottom:24px; padding-bottom:12px; border-bottom:1px solid var(--border); display:flex; align-items:baseline; gap:14px; }
  .section h3 { font-size:16px; margin:28px 0 14px; color:var(--text-dim); font-weight:500; text-transform:uppercase; letter-spacing:1.5px; }

  .count-pill { font-family:'IBM Plex Mono',monospace; font-size:13px; font-weight:500; color:var(--accent); background:var(--accent-dim); padding:4px 12px; border-radius:4px; letter-spacing:.5px; }
  .badge-row { display:flex; gap:10px; margin:-8px 0 28px; flex-wrap:wrap; }

  table { width:100%; border-collapse:collapse; margin-bottom:24px; font-size:14px; }
  th { text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:1px; color:var(--text-muted); padding:10px 16px; border-bottom:1px solid var(--border); background:var(--surface); }
  td { padding:12px 16px; border-bottom:1px solid #1a1a1a; vertical-align:middle; }
  td.mono { font-family:'IBM Plex Mono',monospace; font-size:14px; }
  tr:hover { background:var(--surface); }
  .positive { color:var(--accent); }
  .negative { color:var(--red); }
  .text-muted { color:var(--text-muted); }
  .mono { font-family:'IBM Plex Mono',monospace; }

  .lead-grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; margin:8px 0 32px; }
  @media (max-width: 768px) { .lead-grid { grid-template-columns:1fr; } }

  .lead-card { background:var(--surface); border-radius:10px; padding:24px; position:relative; border:1px solid var(--border); }
  .lead-card.leader { border:1px solid var(--accent); background:linear-gradient(135deg, #0071CE12, var(--surface)); }
  .lead-card.laggard { border:1px solid var(--red); background:linear-gradient(135deg, #ff4d4d12, var(--surface)); }
  .lead-card.solo { border:1px solid var(--yellow); background:linear-gradient(135deg, #ffc10712, var(--surface)); }
  .lead-card .lead-label { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:2px; text-transform:uppercase; color:var(--text-muted); margin-bottom:6px; }
  .lead-card.leader .lead-label { color:var(--accent); }
  .lead-card.laggard .lead-label { color:var(--red); }
  .lead-card.solo .lead-label { color:var(--yellow); }
  .lead-card .lead-ticker { font-family:'IBM Plex Mono',monospace; font-size:30px; font-weight:700; letter-spacing:2px; margin-bottom:2px; }
  .lead-card .lead-company { font-size:14px; color:var(--text-dim); margin-bottom:14px; }
  .lead-card .lead-surprise { font-family:'IBM Plex Mono',monospace; font-size:40px; font-weight:700; margin:6px 0; }
  .lead-card .lead-meta { font-size:12px; color:var(--text-muted); margin-bottom:10px; }
  .lead-card .lead-verdict { margin-bottom:12px; }
  .lead-card .lead-comment { font-size:13px; color:var(--text-dim); line-height:1.6; margin-bottom:14px; }
  .lead-card .lead-link { display:inline-block; font-size:13px; font-family:'IBM Plex Mono',monospace; color:var(--accent); }

  .verdict-mini { display:inline-block; padding:2px 8px; border-radius:3px; font-size:10px; font-weight:600; font-family:'IBM Plex Mono',monospace; letter-spacing:1px; }
  .verdict-mini.beat { background:var(--accent-dim); color:var(--accent); }
  .verdict-mini.miss { background:var(--red-dim); color:var(--red); }
  .verdict-mini.mixed { background:#ffc10722; color:var(--yellow); }

  .kw-tag { font-size:11px; padding:4px 10px; border-radius:4px; font-family:'IBM Plex Mono',monospace; letter-spacing:.5px; }
  .kw-tag.bullish { background:var(--accent-dim); color:var(--accent); }
  .kw-tag.bearish { background:var(--red-dim); color:var(--red); }
  .kw-tag.neutral-tag { background:#ffc10722; color:var(--yellow); }

  .ticker-link { font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--accent); }
  .empty-note { padding:24px; background:var(--surface); border:1px dashed var(--border); border-radius:8px; color:var(--text-muted); font-size:13px; text-align:center; margin-bottom:24px; }

  .footer { border-top:1px solid var(--border); padding:32px 0; text-align:center; font-size:12px; color:var(--text-muted); line-height:1.8; }
"""


def main() -> None:
    print(f"[1/4] {EARNINGS_DIR} 스캔 중...")
    rows = collect_rows()
    print(f"  → {len(rows)}개 파싱 완료")

    grouped = group_by_sector(rows)
    print(f"[2/4] 섹터 분류: {len(grouped)}개")
    for sec, lst in sorted(grouped.items(), key=lambda x: -len(x[1])):
        print(f"    {sec}: {len(lst)} ({', '.join(r.ticker for r in lst)})")

    issues = [r for r in rows if r.notes]
    if issues:
        print(f"[3/4] 데이터 이슈 {len(issues)}건:")
        for r in issues:
            print(f"    {r.ticker}: {', '.join(r.notes)}")
    else:
        print("[3/4] 데이터 이슈 없음")

    print(f"[4/4] HTML 생성 → {OUTPUT_FILE}")
    html_out = render_html(rows, grouped)
    OUTPUT_FILE.write_text(html_out, encoding="utf-8")
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"  → {size_kb:.1f} KB")

    # 섹터별 대장/약자 출력 (보고용)
    print("\n섹터별 대장/약자:")
    for sec in [s for s in GICS_SECTORS if s in grouped]:
        leader, laggard = pick_leader_laggard(grouped[sec])
        ld = f"{leader.ticker} {leader.eps_surprise_pct:+.1f}%" if leader and leader.has_eps_data else "—"
        lg = f"{laggard.ticker} {laggard.eps_surprise_pct:+.1f}%" if laggard and laggard.has_eps_data and laggard.ticker != (leader.ticker if leader else "") else "단독" if (leader and (laggard is None or laggard.ticker == leader.ticker)) else "—"
        print(f"  {sec}: 대장 {ld} / 약자 {lg}")


if __name__ == "__main__":
    main()
