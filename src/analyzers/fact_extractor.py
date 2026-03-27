"""Rule-based fact extractor: pulls numerical claims and facts from news text.

Extracts sentences containing numbers, percentages, currency amounts,
and matches them against known entities/tickers. No LLM API required.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from src.core.models import FactType, Market, NewsFact, NewsItem


# ============================================================
# Number patterns (Korean + English)
# ============================================================

# $1.5B, $250M, $12.3 billion, ₩1,200
_CURRENCY = re.compile(
    r"[\$₩€£]\s?\d[\d,]*\.?\d*\s?"
    r"(?:[BMKbmk](?:illion|n)?|조|억|만)?",
)

# 15%, 0.8%, -2.3%, 78.5%p
_PERCENT = re.compile(r"-?\d+\.?\d*\s?%p?")

# Plain numbers with context: 1,234, 3.5조, 120억, 15만
_NUMBER_KR = re.compile(r"\d[\d,]*\.?\d*\s?(?:조|억|만|개|대|명|건|톤|배)")

# Large numbers in English: 1.5 billion, 250 million, 12,000
_NUMBER_EN = re.compile(
    r"\d[\d,]*\.?\d*\s?(?:billion|million|thousand|trillion|units|tons)",
    re.IGNORECASE,
)

# Ratios and multiples: 22x, 1.5x, P/E 15.3
_MULTIPLE = re.compile(r"\d+\.?\d*\s?[xX배]|P/?E\s?\d+\.?\d*")

# Year references: 2024, 2025, FY2025, Q4 2025
_YEAR_QUARTER = re.compile(
    r"(?:FY|CY)?\d{4}|Q[1-4]\s?\d{4}|[1-4]분기\s?\d{4}",
)

_ALL_NUMBER_PATTERNS = [
    _CURRENCY, _PERCENT, _NUMBER_KR, _NUMBER_EN, _MULTIPLE,
]

# ============================================================
# Fact type keyword mapping
# ============================================================

# Ordered by specificity — first match wins.
# More specific types (earnings, policy) before generic ones (event, deal).
_FACT_TYPE_KEYWORDS: list[tuple[FactType, list[str]]] = [
    (FactType.EARNINGS, [
        "매출", "영업이익", "순이익", "EPS", "revenue", "earnings",
        "profit", "실적", "가이던스", "guidance", "영업손실",
        "흑자", "적자", "당기순이익", "operating income",
    ]),
    (FactType.POLICY, [
        "기준금리", "금통위", "FOMC", "금리 인하", "금리 인상",
        "관세", "tariff", "규제", "법안", "행정명령",
        "interest rate", "regulation", "basis points",
    ]),
    (FactType.FORECAST, [
        "전망", "예상", "예측", "목표가", "target price", "forecast",
        "outlook", "estimate", "상향", "하향", "projected",
    ]),
    (FactType.DEAL, [
        "인수", "합병", "M&A", "IPO", "상장", "공개매수",
        "acquisition", "merger", "deal", "partnership",
    ]),
    (FactType.EVENT, [
        "출시", "발표", "공개", "launch", "announce", "reveal",
        "파업", "중단", "재개", "급락", "급등", "폭락", "폭등",
        "사이드카", "서킷브레이커",
    ]),
]

# ============================================================
# Common tickers / entity dictionary
# ============================================================

# Hardcoded high-frequency tickers for fast matching
_TICKER_DICT: dict[str, str] = {
    # ── US Major ──
    "테슬라": "TSLA", "Tesla": "TSLA", "TSLA": "TSLA",
    "엔비디아": "NVDA", "NVIDIA": "NVDA", "NVDA": "NVDA",
    "애플": "AAPL", "Apple": "AAPL", "AAPL": "AAPL",
    "마이크로소프트": "MSFT", "Microsoft": "MSFT", "MSFT": "MSFT",
    "아마존": "AMZN", "Amazon": "AMZN", "AMZN": "AMZN",
    "구글": "GOOGL", "알파벳": "GOOGL", "Google": "GOOGL", "Alphabet": "GOOGL",
    "메타": "META", "Meta": "META", "META": "META",
    "팔란티어": "PLTR", "Palantir": "PLTR", "PLTR": "PLTR",
    "코인베이스": "COIN", "Coinbase": "COIN", "COIN": "COIN",
    "로빈후드": "HOOD", "Robinhood": "HOOD", "HOOD": "HOOD",
    "AMD": "AMD", "브로드컴": "AVGO", "Broadcom": "AVGO",
    "넷플릭스": "NFLX", "Netflix": "NFLX",
    "디즈니": "DIS", "Disney": "DIS",
    "보잉": "BA", "Boeing": "BA",
    "JP모간": "JPM", "JPMorgan": "JPM",
    "골드만삭스": "GS", "Goldman": "GS",
    "버크셔": "BRK.B", "Berkshire": "BRK.B",
    "ASML": "ASML", "TSMC": "TSM",
    "마이크론": "MU", "Micron": "MU",
    "인텔": "INTC", "Intel": "INTC",
    # ── KR Top 50 ──
    "삼성전자": "005930", "삼전": "005930",
    "SK하이닉스": "000660", "하이닉스": "000660",
    "현대차": "005380", "현대자동차": "005380",
    "LG에너지솔루션": "373220", "LG에너지": "373220",
    "기아": "000270",
    "NAVER": "035420", "네이버": "035420",
    "카카오": "035720",
    "셀트리온": "068270",
    "포스코홀딩스": "005490", "포스코": "005490",
    "하이브": "352820", "HYBE": "352820",
    "두산에너빌리티": "034020", "두산에너빌": "034020",
    "한화솔루션": "009830",
    "한화에어로스페이스": "012450", "한화에어로": "012450",
    "HMM": "011200",
    "LG전자": "066570",
    "LG화학": "051910",
    "SK이노베이션": "096770", "SK이노": "096770",
    "삼성바이오로직스": "207940", "삼바": "207940",
    "삼성SDI": "006400",
    "현대모비스": "012330",
    "KB금융": "105560",
    "신한지주": "055550", "신한금융": "055550", "신한은행": "055550",
    "하나금융": "086790",
    "우리금융": "316140",
    "메리츠금융": "138040", "메리츠증권": "138040", "메리츠": "138040",
    "한국전력": "015760", "한전": "015760",
    "한전KPS": "051600",
    "KT": "030200",
    "SK텔레콤": "017670", "SKT": "017670",
    "LG유플러스": "032640",
    "이마트": "139480", "신세계": "004170",
    "호반건설": "294870",
    "DL이앤씨": "375500",
    "대한항공": "003490",
    "사람인": "143240", "사람인HR": "143240",
    "다우키움": "055550",
    "CJ ENM": "035760",
    "엔씨소프트": "036570", "엔씨": "036570",
    "크래프톤": "259960",
    "카카오게임즈": "293490",
    "SK케미칼": "285130",
    "우진비앤지": "018620",
    # ── Crypto ──
    "비트코인": "BTC", "Bitcoin": "BTC", "BTC": "BTC",
    "이더리움": "ETH", "Ethereum": "ETH", "ETH": "ETH",
    "리플": "XRP", "Ripple": "XRP", "XRP": "XRP",
    "솔라나": "SOL", "Solana": "SOL", "SOL": "SOL",
}

# Entity names (for claim.entities field) — superset of ticker keys
_ENTITY_NAMES: set[str] = set(_TICKER_DICT.keys()) | {
    # Central banks / regulators
    "Fed", "FOMC", "연준", "한국은행", "한은", "금통위", "ECB", "BOJ",
    "SEC", "금감원", "공정위", "금융위", "기재부",
    "관세청", "Pentagon", "국방부", "의회", "Congress",
    # People
    "파월", "Powell", "머스크", "Musk", "젠슨황", "Jensen Huang",
    "트럼프", "Trump", "바이든", "Biden",
    "이재용", "정의선", "최태원",
    "네타냐후", "Netanyahu", "푸틴", "Putin", "시진핑",
    # Countries / regions
    "미국", "한국", "중국", "일본", "러시아",
    "이란", "Iran", "카타르", "Qatar",
    "UAE", "쿠웨이트", "요르단", "이스라엘", "Israel",
    "사우디", "Saudi", "인도", "India", "베트남", "Vietnam",
    "영국", "EU", "NATO", "OPEC",
    # Companies (non-public / private)
    "SpaceX", "OpenAI", "xAI", "텐센트", "Tencent",
    "골드만삭스", "Goldman Sachs",
    # Macro / market / commodities
    "코스피", "코스닥", "나스닥", "S&P", "다우",
    "KOSPI", "KOSDAQ", "NASDAQ", "Dow",
    "원유", "WTI", "금값", "LNG", "디젤",
    "호르무즈", "Hormuz",
}


# ============================================================
# Core extraction logic
# ============================================================


_HTML_TAG = re.compile(r"<[^>]+>")
_HTML_ENTITY = re.compile(r"&\w+;")
_MAX_TEXT_LEN = 1_000_000  # 1 MB


def _clean_html(text: str) -> str:
    """Remove residual HTML tags and entities."""
    text = _HTML_TAG.sub("", text)
    text = _HTML_ENTITY.sub(" ", text)
    return text


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, handling Korean and English."""
    # Split on period/question/exclamation followed by space or newline
    # Avoid splitting on decimal points (e.g., "3.14")
    raw = re.split(r"(?<=[.?!。])\s+|\n+", text)
    return [s.strip() for s in raw if s.strip() and len(s.strip()) > 5]


def _extract_numbers(sentence: str) -> list[dict[str, Any]]:
    """Extract all number patterns from a sentence.

    Deduplicates overlapping matches by keeping the longer span.

    Returns:
        List of dicts with keys: raw (str), start (int), end (int).
    """
    found: list[dict[str, Any]] = []
    for pattern in _ALL_NUMBER_PATTERNS:
        for match in pattern.finditer(sentence):
            found.append({
                "raw": match.group().strip(),
                "start": match.start(),
                "end": match.end(),
            })

    if not found:
        return found

    # Remove overlapping matches — keep the longer span
    found.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))
    deduped: list[dict[str, Any]] = [found[0]]
    for item in found[1:]:
        if item["start"] >= deduped[-1]["end"]:
            deduped.append(item)
        elif (item["end"] - item["start"]) > (
            deduped[-1]["end"] - deduped[-1]["start"]
        ):
            deduped[-1] = item
    return deduped


# Korean company name suffix patterns (dynamic entity detection)
_KR_COMPANY_SUFFIXES = re.compile(
    r"[가-힣]{1,10}"
    r"(?:전자|증권|은행|금융|건설|화학|에너지|바이오|제약|물산|중공업"
    r"|솔루션|이앤씨|텔레콤|생명|화재|캐피탈|카드|투자|자산운용"
    r"|반도체|디스플레이|모비스|오토에버|엔지니어링|홀딩스)",
)


def _match_entities(sentence: str) -> tuple[list[str], list[str]]:
    """Match known entities and tickers in a sentence.

    Uses both static dictionary and dynamic Korean company name patterns.

    Returns:
        Tuple of (entity_names, ticker_symbols).
    """
    entities: list[str] = []
    tickers: set[str] = set()

    # Static dictionary match
    for name in _ENTITY_NAMES:
        if name in sentence:
            entities.append(name)
            ticker = _TICKER_DICT.get(name)
            if ticker:
                tickers.add(ticker)

    # Dynamic Korean company pattern match
    for match in _KR_COMPANY_SUFFIXES.finditer(sentence):
        name = match.group()
        if name not in entities and len(name) >= 3:
            entities.append(name)
            ticker = _TICKER_DICT.get(name)
            if ticker:
                tickers.add(ticker)

    return entities, sorted(tickers)


def _classify_fact_type(sentence: str) -> FactType:
    """Classify the fact type based on keyword matching.

    Uses ordered list — more specific types match first.
    Returns the first matching type, defaulting to NUMERICAL.
    """
    lower = sentence.lower()
    for fact_type, keywords in _FACT_TYPE_KEYWORDS:
        for kw in keywords:
            if kw.lower() in lower:
                return fact_type
    return FactType.NUMERICAL


def _compute_confidence(
    numbers: list[dict[str, Any]],
    entities: list[str],
    tickers: list[str],
) -> float:
    """Compute extraction confidence score.

    - Numbers + entities/tickers present = 1.0
    - Numbers only = 0.7
    - Entities only = 0.5
    """
    has_numbers = len(numbers) > 0
    has_entities = len(entities) > 0 or len(tickers) > 0

    if has_numbers and has_entities:
        return 1.0
    if has_numbers:
        return 0.7
    if has_entities:
        return 0.5
    return 0.3


def extract_facts_from_news(news: NewsItem) -> list[NewsFact]:
    """Extract structured facts from a single news item.

    Args:
        news: The source news article.

    Returns:
        List of NewsFact objects extracted from the article.
    """
    text = (news.content or news.summary or news.title or "").strip()
    if not text or len(text) > _MAX_TEXT_LEN:
        return []

    text = _clean_html(text)
    sentences = _split_sentences(text)
    facts: list[NewsFact] = []
    now = datetime.now(timezone.utc)

    for sentence in sentences:
        numbers = _extract_numbers(sentence)
        if not numbers:
            continue

        entities, tickers = _match_entities(sentence)
        fact_type = _classify_fact_type(sentence)
        confidence = _compute_confidence(numbers, entities, tickers)

        # Build a concise claim from the sentence
        claim = sentence[:300]

        # Build numbers dict from first (most prominent) number
        numbers_dict: dict[str, Any] = {}
        if numbers:
            numbers_dict = {
                "raw_values": [n["raw"] for n in numbers[:5]],
                "count": len(numbers),
            }

        fact = NewsFact(
            news_id=news.id,
            fact_type=fact_type,
            claim=claim,
            entities=entities,
            tickers=tickers or news.related_tickers,
            numbers=numbers_dict,
            source_quote=sentence[:500],
            market=news.market,
            confidence=confidence,
            published_at=news.published_at,
            extracted_at=now,
        )
        facts.append(fact)

    return facts


def extract_facts_batch(
    news_items: list[NewsItem],
) -> dict[str, list[NewsFact]]:
    """Extract facts from multiple news items.

    Args:
        news_items: List of news articles to process.

    Returns:
        Dict mapping news_id to list of extracted facts.
    """
    results: dict[str, list[NewsFact]] = {}
    for news in news_items:
        facts = extract_facts_from_news(news)
        if facts:
            results[news.id] = facts
    return results
