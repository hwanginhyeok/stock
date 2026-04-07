"""엔티티 노이즈 필터 — 추출 시 + 리뷰 시 공통으로 사용.

금액, 수량, 도메인, 단순 숫자, 노이즈 단어를 걸러낸다.
False positive 방지를 위해 패턴은 보수적으로 설계.
"""

from __future__ import annotations

import re

# URL/도메인 패턴
_DOMAIN_RE = re.compile(
    r"^https?://|^www\.|\.com$|\.org$|\.net$|\.co\.kr$|\.io$",
    re.IGNORECASE,
)

# 금액 패턴: $290 million, $2.9B, 40억 달러, 6조200억 원
_MONEY_RE = re.compile(
    r"(?i)"
    r"^\$[\d,.\s]+(million|billion|trillion|[BMK])?\s*$"
    r"|^\d[\d,.\s억조만]*(원|달러|Won|Dollar).*$"
    r"|^(billion|million|trillion)\s+dollars?\s*$",
)

# 수량 패턴: 17,954 vehicles, 100 GW, 140 years
_QTY_RE = re.compile(
    r"(?i)"
    r"^\d[\d,.\s]*(vehicles?|years?|units?|[GTM]W|barrels?)\s*$"
    r"|^\d[\d,.\s]*(건|개|명|배|주|채)\s.*$",
)

# 비자 코드: E-9 visa, H-1B 비자 (반드시 비자/visa 키워드 포함)
_VISA_CODE_RE = re.compile(r"^[A-Z]-\d+[A-Z]?\s+(비자|visa)\s*$", re.IGNORECASE)

# 비율/레비 패턴: 15% levy, 25% tariff
_PERCENT_RE = re.compile(r"^\d+(\.\d+)?%\s+\w+\s*$")

# 노이즈 단어 (소문자로 비교)
_NOISE_NAMES = {
    "metadata", "capabilities", "endpoints", "operational details",
    "war", "conflict", "news", "report", "article", "source",
    "the post", "the report", "billion dollars", "million dollars",
    "균형", "추세", "시장", "경제", "성장", "하락", "상승",
}

# 숫자/통화 문자 제거용 (남는 게 없으면 노이즈)
_NUMERIC_STRIP_RE = re.compile(r"[\d$€₩¥£%,.~\-–—·주년월일개건조억만천원]")


def is_noise_entity(name: str) -> bool:
    """노이즈 엔티티 여부를 판별한다.

    Args:
        name: 엔티티 이름

    Returns:
        True면 노이즈 → 필터링 대상
    """
    if not name or len(name) < 2:
        return True

    # URL/도메인
    if _DOMAIN_RE.search(name):
        return True

    # 노이즈 단어
    if name.lower().strip() in _NOISE_NAMES:
        return True

    # 금액 패턴
    if _MONEY_RE.match(name):
        return True

    # 수량 패턴
    if _QTY_RE.match(name):
        return True

    # 비자/규격 코드
    if _VISA_CODE_RE.match(name):
        return True

    # 비율+명사 패턴
    if _PERCENT_RE.match(name):
        return True

    # 숫자/통화만으로 구성 ($71,500, 140주년, 2월 등)
    cleaned = _NUMERIC_STRIP_RE.sub("", name).strip()
    if not cleaned:
        return True

    return False
