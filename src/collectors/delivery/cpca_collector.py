"""중국 CPCA(乘联会) Tesla 월별 판매량 수집기.

RSS 기사에서 정규식으로 Tesla China 판매/인도 숫자를 추출한다.
부분 성공 허용 — 한 소스 실패해도 다음 소스 계속 시도.

수동 실행: python3 src/collectors/delivery/cpca_collector.py
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import feedparser
import requests

# ── 상수 ──────────────────────────────────────────────────────────────
DATA_DIR = Path(
    os.getenv(
        "DELIVERY_DATA_DIR",
        str(Path(__file__).resolve().parents[3] / "data" / "research" / "stocks" / "tesla" / "delivery_signals"),
    ),
)
OUTPUT_FILE = DATA_DIR / "china_monthly.json"

CONFIDENCE_ORDER = {"high": 3, "medium": 2, "low": 1}

# RSS 소스 (우선순위 순)
RSS_SOURCES: list[dict[str, str]] = [
    {
        "name": "Google News CPCA",
        "url": "https://news.google.com/rss/search?q=CPCA+Tesla+China+deliveries+OR+sales&hl=en&gl=US&ceid=US:en",
    },
    {
        "name": "Google News Tesla China",
        "url": "https://news.google.com/rss/search?q=%22Tesla+China%22+wholesale+OR+deliveries+OR+sales&hl=en&gl=US&ceid=US:en",
    },
    {
        "name": "Reuters Tesla China",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+Tesla+China+sales+OR+deliveries&hl=en&gl=US&ceid=US:en",
    },
    {
        "name": "Teslarati",
        "url": "https://www.teslarati.com/feed/",
    },
    {
        "name": "Electrek Tesla",
        "url": "https://electrek.co/guides/tesla/feed/",
    },
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DeliveryBot/1.0)"}
REQUEST_TIMEOUT = 15
DELAY_BETWEEN_SOURCES = 2

# 숫자 추출 정규식 (우선순위 순)
PATTERNS: list[re.Pattern[str]] = [
    # "Tesla sold/delivered 78,000 vehicles/cars/units in China"
    re.compile(
        r"Tesla\s+(?:sold|delivered|shipped|produced)\s+([\d,]+)\s*(?:vehicles?|cars?|units?|deliveries)",
        re.IGNORECASE,
    ),
    # "78,000 Tesla vehicles/cars/units ... China"
    re.compile(
        r"([\d,]+)\s*(?:vehicles?|cars?|units?)\s+.*?Tesla.*?China",
        re.IGNORECASE,
    ),
    # "Tesla China ... 78,000"
    re.compile(
        r"Tesla.*?China.*?([\d,]+)\s*(?:vehicles?|cars?|units?|deliveries)",
        re.IGNORECASE,
    ),
    # "China ... Tesla ... 78,000 vehicles"
    re.compile(
        r"China.*?Tesla.*?([\d,]+)\s*(?:vehicles?|cars?|units?)",
        re.IGNORECASE,
    ),
]

# 최소 대수 (지역별)
MIN_UNITS = 20_000  # 중국 CPCA 월별 최소치

# 기사 만료 기간 (초)
STALE_THRESHOLD_SEC = 6 * 30 * 24 * 3600  # 6개월

# 월 키 추출 패턴 (우선순위 순)
MONTH_PATTERNS: list[re.Pattern[str]] = [
    # "January 2026", "Jan 2026", "Jan. 2026"
    re.compile(
        r"(?:in|for|of)\s+"
        r"(January|February|March|April|May|June|July|August|September|October|November|December"
        r"|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]*\.?\s+(\d{4})",
        re.IGNORECASE,
    ),
    # "2026-04", "2026/04"
    re.compile(r"(\d{4})[-/](0?[1-9]|1[0-2])"),
]

MONTH_MAP = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "jun": "06", "jul": "07", "aug": "08", "sep": "09",
    "oct": "10", "nov": "11", "dec": "12",
}

# 신뢰도 소스 매핑
HIGH_CONFIDENCE_SOURCES = {"reuters", "bloomberg", "cnbc", "south china morning post"}
MEDIUM_CONFIDENCE_SOURCES = {"teslarati", "electrek", "insideevs", "cleantechnica"}


def _extract_month_key(text: str, published: datetime | None = None) -> str | None:
    """기사에서 'YYYY-MM' 키를 추출 (3단계 폴백).

    1) 텍스트에서 "January 2026" / "Jan 2026" / "2026-04" 패턴 매칭
    2) 실패 시 feedparser published_parsed에서 추출
    3) 그래도 없으면 None (호출부에서 직전월 fallback)
    """
    # 1단계: 텍스트 패턴 매칭
    for pat in MONTH_PATTERNS:
        for m in pat.finditer(text):
            g1, g2 = m.group(1).lower(), m.group(2)
            # "January 2026" / "Jan 2026" 형식
            if g2.isdigit() and len(g2) == 4 and g1 in MONTH_MAP:
                return f"{g2}-{MONTH_MAP[g1]}"
            # "2026-04" 형식 — MM이 01~12인지 검증
            if g1.isdigit() and len(g1) == 4:
                if g2.isdigit() and 1 <= int(g2) <= 12:
                    return f"{g1}-{int(g2):02d}"
    # 2단계: published 날짜
    if published is not None:
        return f"{published.year}-{published.month:02d}"
    return None


def _default_month_key() -> str:
    """직전월 YYYY-MM 반환 (CPCA 발표는 보통 직전월 데이터)."""
    now = datetime.now(timezone.utc)
    # 직전월: 현재 1일 - 1일 = 전월 마지막날
    if now.month == 1:
        return f"{now.year - 1}-12"
    return f"{now.year}-{now.month - 1:02d}"


def _is_valid_units(raw: str, value: int, min_units: int = MIN_UNITS) -> bool:
    """추출된 숫자가 유효한 대수인지 검증."""
    # 연도(1800~2099) 거르기
    if 1800 <= value <= 2099:
        return False
    # 지역별 최소 대수
    if value < min_units:
        return False
    return True


def _extract_units(text: str) -> int | None:
    """기사 텍스트에서 Tesla 판매/인도 대수 추출.

    퍼센트(%) 컨텍스트, 소숫점 일부, 연도 범위(1800~2099)는 무시.
    """
    for pat in PATTERNS:
        for m in pat.finditer(text):
            raw = m.group(1).replace(",", "")
            end = m.end(1)
            # "98.6%" 처럼 소숫점 일부면 스킵
            if end < len(text) and text[end] in (".", "%"):
                continue
            try:
                value = int(raw)
            except ValueError:
                continue
            if _is_valid_units(raw, value):
                return value
    return None


def _confidence_for_source(source_name: str, headline: str) -> str:
    """소스별 신뢰도 판정."""
    name_lower = source_name.lower()
    headline_lower = headline.lower()
    for src in HIGH_CONFIDENCE_SOURCES:
        if src in name_lower or src in headline_lower:
            return "high"
    for src in MEDIUM_CONFIDENCE_SOURCES:
        if src in name_lower or src in headline_lower:
            return "medium"
    return "low"


def _clean_html(html: str) -> str:
    """HTML 태그 제거 + 공백 정리."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&\w+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_entry_date(entry: Any) -> datetime | None:
    """feedparser entry에서 published 날짜 추출."""
    published_parsed = getattr(entry, "published_parsed", None)
    if published_parsed:
        try:
            return datetime(*published_parsed[:6], tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pass
    return None


def _is_stale(published: datetime | None) -> bool:
    """기사가 6개월 이상 지났는지 확인."""
    if published is None:
        return False  # 날짜 모르면 스킵 안 함
    age = (datetime.now(timezone.utc) - published).total_seconds()
    return age > STALE_THRESHOLD_SEC


def _load_existing() -> dict[str, Any]:
    """기존 JSON 로드 (없으면 빈 dict)."""
    if OUTPUT_FILE.exists():
        try:
            return json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(data: dict[str, Any]) -> None:
    """JSON 저장 (디렉토리 자동 생성)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class CPCACollector:
    """중국 CPCA Tesla 월별 판매량 수집기."""

    def __init__(self) -> None:
        self._results: list[dict[str, Any]] = []

    def collect(self) -> dict[str, Any]:
        """모든 RSS 소스에서 CPCA 데이터 수집.

        Returns:
            월별 Tesla China 판매량 딕셔너리.
        """
        data = _load_existing()

        for source in RSS_SOURCES:
            try:
                self._fetch_source(source, data)
            except Exception as e:
                print(f"  [FAIL] {source['name']}: {e}")
            time.sleep(DELAY_BETWEEN_SOURCES)

        _save(data)
        return data

    def _fetch_source(self, source: dict[str, str], data: dict[str, Any]) -> None:
        """단일 RSS 소스에서 기사 파싱."""
        print(f"[FETCH] {source['name']} ...")
        resp = requests.get(source["url"], headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)

        entries = feed.get("entries", [])[:20]
        extracted = 0

        for entry in entries:
            title = getattr(entry, "title", "").strip()
            if not title:
                continue

            # 만료 기사 스킵 (버그 3)
            published = _parse_entry_date(entry)
            if _is_stale(published):
                continue

            # 본문 합치기
            summary = _clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
            content_parts = [title, summary]
            if hasattr(entry, "content") and entry.content:
                content_parts.append(_clean_html(entry.content[0].get("value", "")))
            full_text = " ".join(content_parts)

            # Tesla + China 관련 기사만
            if not (re.search(r"\btesla\b", full_text, re.IGNORECASE) and re.search(r"\bchina\b", full_text, re.IGNORECASE)):
                continue

            # 숫자 추출
            units = _extract_units(full_text)
            if units is None:
                continue

            # 월 키 추출: 텍스트 → published → 직전월 (버그 1)
            month_key = _extract_month_key(full_text, published) or _default_month_key()
            confidence = _confidence_for_source(source["name"], title)

            # 기존 데이터보다 신뢰도 높으면 업데이트
            existing = data.get(month_key, {})
            existing_conf = CONFIDENCE_ORDER.get(existing.get("confidence", "low"), 0)
            new_conf = CONFIDENCE_ORDER[confidence]

            if new_conf >= existing_conf:
                data[month_key] = {
                    "tesla_units": units,
                    "source": source["name"],
                    "headline": title,
                    "confidence": confidence,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                }

            extracted += 1
            print(f"  [{month_key}] {units:,} units — {title[:60]}... ({confidence})")

        print(f"  → {source['name']}: {extracted}건 추출")
        self._results.append({"source": source["name"], "extracted": extracted})

    @property
    def results(self) -> list[dict[str, Any]]:
        """소스별 수집 결과."""
        return self._results


def main() -> None:
    """CLI 진입점."""
    print("=" * 60)
    print("CPCA Tesla China 판매량 수집기")
    print("=" * 60)

    collector = CPCACollector()
    data = collector.collect()

    print(f"\n{'=' * 60}")
    print(f"저장: {OUTPUT_FILE}")
    print(f"월별 데이터: {len(data)}개")

    for month_key in sorted(data.keys()):
        entry = data[month_key]
        print(f"  {month_key}: {entry['tesla_units']:,} units ({entry['confidence']}) from {entry['source']}")

    if not data:
        print("  (수집된 데이터 없음 — RSS에 CPCA 관련 기사가 없을 수 있음)")


if __name__ == "__main__":
    main()
