"""유럽 주요국 Tesla 월별 신차 등록 수집기.

노르웨이 OFV, 영국 SMMT, 독일 KBA, EU 전체 ACEA 데이터를
전문 매체 RSS + Google News에서 파싱. 부분 성공 허용.

수동 실행: python3 src/collectors/delivery/eu_reg_collector.py
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
OUTPUT_FILE = DATA_DIR / "eu_monthly.json"

CONFIDENCE_ORDER = {"high": 3, "medium": 2, "low": 1}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DeliveryBot/1.0)"}
REQUEST_TIMEOUT = 15
DELAY_BETWEEN_SOURCES = 2

# 지역별 최소 대수 (버그 2)
MIN_UNITS: dict[str, int] = {
    "norway": 200,
    "uk": 1000,
    "germany": 1000,
    "eu_total": 5000,
}

# 기사 만료 기간 (초) — 6개월 (버그 3)
STALE_THRESHOLD_SEC = 6 * 30 * 24 * 3600

# 전문 매체 RSS 피드 (공통 — 모든 국가에 적용)
SPECIALIST_FEEDS: list[dict[str, str]] = [
    {"name": "Teslarati", "url": "https://www.teslarati.com/feed/"},
    {"name": "InsideEVs", "url": "https://insideevs.com/feed/"},
    {"name": "CleanTechnica", "url": "https://cleantechnica.com/feed/"},
]

# 국가별 소스 정의 (전문 매체 RSS만 사용 — Google News는 리다이렉트 URL로 본문 fetch 불가)
COUNTRY_SOURCES: dict[str, list[dict[str, str]]] = {
    "norway": [
        *SPECIALIST_FEEDS,
        {
            "name": "ACEA Feed",
            "url": "https://www.acea.auto/feed/",
        },
    ],
    "uk": [
        *SPECIALIST_FEEDS,
        {
            "name": "ACEA Feed",
            "url": "https://www.acea.auto/feed/",
        },
    ],
    "germany": [
        *SPECIALIST_FEEDS,
        {
            "name": "ACEA Feed",
            "url": "https://www.acea.auto/feed/",
        },
    ],
    "eu_total": [
        *SPECIALIST_FEEDS,
        {
            "name": "ACEA Feed",
            "url": "https://www.acea.auto/feed/",
        },
    ],
}

# 국가별 숫자 추출 정규식 (능동태 + 수동태 + 괄호형 모두 커버)
COUNTRY_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "norway": [
        # 능동태: "Tesla sold/registered 1,234 vehicles ... Norway"
        re.compile(r"Tesla\s+(?:sold|registered|delivered)\s+([\d,]+)\s*(?:vehicles?|cars?|units?)\s+.*?Norway", re.IGNORECASE),
        # 수동태: "1,234 Tesla vehicles registered ... Norway"
        re.compile(r"([\d,]+)\s+Tesla\s+(?:vehicles?|cars?|units?)\s+registered\s+.*?Norway", re.IGNORECASE),
        # 역순: "Norway ... Tesla ... 1,234 vehicles"
        re.compile(r"Norway.*?Tesla.*?([\d,]+)\s*(?:vehicles?|cars?|units?|registrations?)", re.IGNORECASE),
        # 캡슐: "Norway ... 1,234 vehicles/cars/units/registrations"
        re.compile(r"Norway[^.]*?([\d,]+)\s*(?:vehicles?|cars?|units?|registrations?)", re.IGNORECASE),
        # 괄호형: "Norway (1,234 units)"
        re.compile(r"Norway\s*\(([\d,]+)\s*(?:vehicles?|cars?|units?)?", re.IGNORECASE),
        # 느슨한: "Tesla ... 1,234 ... Norway"
        re.compile(r"Tesla[^.]{0,80}?([\d,]+)[^.]{0,80}?Norway", re.IGNORECASE),
    ],
    "uk": [
        re.compile(r"Tesla\s+(?:sold|registered)\s+([\d,]+)\s*(?:vehicles?|cars?|units?)\s+.*?(?:UK|Britain|United Kingdom)", re.IGNORECASE),
        re.compile(r"([\d,]+)\s+Tesla\s+(?:vehicles?|cars?|units?)\s+registered\s+.*?(?:UK|Britain)", re.IGNORECASE),
        re.compile(r"(?:UK|Britain).*?Tesla.*?([\d,]+)\s*(?:vehicles?|cars?|units?|registrations?)", re.IGNORECASE),
        re.compile(r"(?:UK|Britain)[^.]*?([\d,]+)\s*(?:vehicles?|cars?|units?|registrations?)", re.IGNORECASE),
        re.compile(r"Tesla[^.]{0,80}?([\d,]+)[^.]{0,80}?(?:UK|Britain)", re.IGNORECASE),
    ],
    "germany": [
        re.compile(r"Tesla\s+(?:sold|registered|Zulassungen)\s+([\d,]+)\s*(?:vehicles?|cars?|units?|Fahrzeuge?)", re.IGNORECASE),
        re.compile(r"([\d,]+)\s+Tesla\s+(?:vehicles?|cars?|units?)\s+registered\s+.*?(?:Germany|Deutschland)", re.IGNORECASE),
        re.compile(r"(?:Deutschland|Germany)[^.]*?([\d,]+)\s*(?:vehicles?|cars?|units?|Fahrzeuge?|Zulassungen)", re.IGNORECASE),
        re.compile(r"(?:Deutschland|Germany)\s*\(([\d,]+)\s*(?:vehicles?|cars?|units?)?", re.IGNORECASE),
        re.compile(r"Tesla[^.]{0,80}?([\d,]+)[^.]{0,80}?(?:Deutschland|Germany)", re.IGNORECASE),
    ],
    "eu_total": [
        re.compile(r"Tesla\s+(?:sold|registered)\s+([\d,]+)\s*(?:vehicles?|cars?|units?)\s+.*?(?:EU|Europe)", re.IGNORECASE),
        re.compile(r"([\d,]+)\s+Tesla\s+(?:vehicles?|cars?|units?)\s+registered\s+.*?(?:EU|Europe)", re.IGNORECASE),
        re.compile(r"(?:EU|Europe).*?Tesla.*?([\d,]+)\s*(?:vehicles?|cars?|units?|registrations?)", re.IGNORECASE),
        re.compile(r"(?:EU|Europe)[^.]*?([\d,]+)\s*(?:vehicles?|cars?|units?|registrations?)", re.IGNORECASE),
    ],
}

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
    # 독일어 "im Januar 2026"
    re.compile(
        r"im\s+(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+(\d{4})",
        re.IGNORECASE,
    ),
    # "2026-04", "2026/04"
    re.compile(r"(\d{4})[-/](0?[1-9]|1[0-2])"),
]

MONTH_MAP_EN = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "jun": "06", "jul": "07", "aug": "08", "sep": "09",
    "oct": "10", "nov": "11", "dec": "12",
}
MONTH_MAP_DE = {
    "januar": "01", "februar": "02", "märz": "03", "april": "04",
    "mai": "05", "juni": "06", "juli": "07", "august": "08",
    "september": "09", "oktober": "10", "november": "11", "dezember": "12",
}


def _extract_month_key(text: str, published: datetime | None = None) -> str | None:
    """기사에서 'YYYY-MM' 키 추출 (3단계 폴백).

    1) 텍스트 패턴 (영어/독일어/숫자)
    2) feedparser published_parsed
    3) None (호출부에서 직전월 fallback)
    """
    for pat in MONTH_PATTERNS:
        for m in pat.finditer(text):
            g1, g2 = m.group(1).lower(), m.group(2)
            # 영어 월명 (full + abbreviated)
            if g1 in MONTH_MAP_EN:
                return f"{g2}-{MONTH_MAP_EN[g1]}"
            # 독일어 월명
            if g1 in MONTH_MAP_DE:
                return f"{g2}-{MONTH_MAP_DE[g1]}"
            # YYYY-MM 숫자 — MM이 01~12인지 검증
            if g1.isdigit() and len(g1) == 4:
                if g2.isdigit() and 1 <= int(g2) <= 12:
                    return f"{g1}-{int(g2):02d}"
    # 2단계: published 날짜
    if published is not None:
        return f"{published.year}-{published.month:02d}"
    return None


def _default_month_key() -> str:
    """직전월 YYYY-MM 반환."""
    now = datetime.now(timezone.utc)
    if now.month == 1:
        return f"{now.year - 1}-12"
    return f"{now.year}-{now.month - 1:02d}"


def _is_valid_units(raw: str, value: int, country: str) -> bool:
    """추출된 숫자가 유효한 대수인지 검증."""
    # 연도(1800~2099) 거르기
    if 1800 <= value <= 2099:
        return False
    # 지역별 최소 대수
    min_units = MIN_UNITS.get(country, 100)
    if value < min_units:
        return False
    return True


def _extract_units(text: str, country: str) -> int | None:
    """국가별 패턴으로 Tesla 등록 대수 추출.

    퍼센트(%), 소숫점 일부, 연도 범위는 무시.
    """
    patterns = COUNTRY_PATTERNS.get(country, [])
    for pat in patterns:
        for m in pat.finditer(text):
            raw = m.group(1).replace(",", "")
            end = m.end(1)
            # "98.6%" 처럼 소숫점 일부 또는 퍼센트면 스킵
            if end < len(text) and text[end] in (".", "%"):
                continue
            try:
                val = int(raw)
            except ValueError:
                continue
            if _is_valid_units(raw, val, country):
                return val
    return None


def _confidence_for_source(source_name: str, country: str) -> str:
    """소스+국가별 신뢰도."""
    name_lower = source_name.lower()
    # 공식 기관 직접 피드
    official = {"ofv": "norway", "smmt": "uk", "kba": "germany", "acea": "eu_total"}
    for key, ctry in official.items():
        if key in name_lower and ctry == country:
            return "high"
    # 전문 매체
    specialists = {"teslarati", "electrek", "insideevs", "cleantechnica", "ev-volumes"}
    for s in specialists:
        if s in name_lower:
            return "medium"
    return "low"


def _clean_html(html: str) -> str:
    """HTML 태그 제거."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&\w+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _fetch_article_text(url: str, timeout: int = 10) -> str:
    """기사 본문 텍스트 fetch. 실패 시 빈 문자열 반환."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text)
        return text[:5000]
    except Exception:
        return ""


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
        return False
    age = (datetime.now(timezone.utc) - published).total_seconds()
    return age > STALE_THRESHOLD_SEC


def _load_existing() -> dict[str, Any]:
    """기존 JSON 로드."""
    if OUTPUT_FILE.exists():
        try:
            return json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(data: dict[str, Any]) -> None:
    """JSON 저장."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class EURegistrationCollector:
    """유럽 주요국 Tesla 월별 신차 등록 수집기."""

    def __init__(self) -> None:
        self._results: dict[str, int] = {}  # country → extracted count

    def collect(self) -> dict[str, Any]:
        """모든 국가/소스에서 등록 데이터 수집.

        Returns:
            월별·국가별 Tesla 등록 대수 딕셔너리.
        """
        data = _load_existing()

        for country, sources in COUNTRY_SOURCES.items():
            self._results[country] = 0
            for source in sources:
                try:
                    self._fetch_source(source, country, data)
                except Exception as e:
                    print(f"  [FAIL] {source['name']}: {e}")
                time.sleep(DELAY_BETWEEN_SOURCES)

        # collected_at 갱신
        for month_key in data:
            data[month_key]["collected_at"] = datetime.now(timezone.utc).isoformat()

        _save(data)
        return data

    def _fetch_source(self, source: dict[str, str], country: str, data: dict[str, Any]) -> None:
        """단일 RSS 소스에서 국가별 데이터 파싱."""
        print(f"[FETCH] {source['name']} ({country}) ...")
        resp = requests.get(source["url"], headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)

        entries = feed.get("entries", [])[:20]
        extracted = 0

        # 전문 매체 피드는 국가별 키워드 필터 적용
        country_keywords: dict[str, list[str]] = {
            "norway": ["norway", "nordic", "ofv"],
            "uk": ["uk", "britain", "united kingdom", "smmt"],
            "germany": ["germany", "deutschland", "kba", "zulassungen"],
            "eu_total": ["eu", "europe", "european", "acea"],
        }
        keywords = country_keywords.get(country, [])
        is_specialist = any(s in source["name"].lower() for s in ["teslarati", "insideevs", "cleantechnica"])

        for entry in entries:
            title = getattr(entry, "title", "").strip()
            if not title:
                continue

            # 만료 기사 스킵
            published = _parse_entry_date(entry)
            if _is_stale(published):
                continue

            summary = _clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
            content_parts = [title, summary]
            if hasattr(entry, "content") and entry.content:
                content_parts.append(_clean_html(entry.content[0].get("value", "")))
            full_text = " ".join(content_parts)

            # Tesla 관련 기사만
            if not re.search(r"\btesla\b", full_text, re.IGNORECASE):
                continue

            # 전문 매체 피드는 국가 키워드 필터 추가
            if is_specialist and not any(kw in full_text.lower() for kw in keywords):
                continue

            # 숫자 추출: RSS summary 먼저, 실패 시 기사 본문 fetch
            units = _extract_units(full_text, country)
            article_text = ""
            if units is None:
                link = getattr(entry, "link", "")
                if link:
                    article_text = _fetch_article_text(link)
                    if article_text:
                        units = _extract_units(article_text, country)
            if units is None:
                continue

            # 월 키: 텍스트+본문 → published → 직전월
            combined_text = (full_text + " " + article_text).strip() if article_text else full_text
            month_key = _extract_month_key(combined_text, published) or _default_month_key()
            confidence = _confidence_for_source(source["name"], country)

            # 기존 데이터와 비교
            if month_key not in data:
                data[month_key] = {}

            existing = data[month_key].get(country)
            existing_conf = CONFIDENCE_ORDER.get(
                existing.get("confidence", "low") if isinstance(existing, dict) else "low", 0,
            )
            new_conf = CONFIDENCE_ORDER[confidence]

            if new_conf >= existing_conf:
                data[month_key][country] = {
                    "tesla_units": units,
                    "source": source["name"],
                    "confidence": confidence,
                }

            extracted += 1
            print(f"  [{month_key}] {country}: {units:,} units — {title[:50]}... ({confidence})")

        print(f"  → {source['name']}: {extracted}건 추출")
        self._results[country] = self._results.get(country, 0) + extracted

    @property
    def results(self) -> dict[str, int]:
        """국가별 수집 건수."""
        return self._results


def main() -> None:
    """CLI 진입점."""
    print("=" * 60)
    print("유럽 Tesla 신차 등록 수집기")
    print("=" * 60)

    collector = EURegistrationCollector()
    data = collector.collect()

    print(f"\n{'=' * 60}")
    print(f"저장: {OUTPUT_FILE}")
    print(f"월별 데이터: {len(data)}개")

    countries = ["norway", "uk", "germany", "eu_total"]
    for month_key in sorted(data.keys()):
        entry = data[month_key]
        parts = []
        for c in countries:
            if c in entry and isinstance(entry[c], dict) and entry[c].get("tesla_units"):
                parts.append(f"{c}={entry[c]['tesla_units']:,}")
        if parts:
            print(f"  {month_key}: {', '.join(parts)}")

    if not data:
        print("  (수집된 데이터 없음 — RSS에 등록 관련 기사가 없을 수 있음)")

    # 국가별 요약
    print("\n국가별 수집 건수:")
    for c, cnt in collector.results.items():
        print(f"  {c}: {cnt}건")


if __name__ == "__main__":
    main()
