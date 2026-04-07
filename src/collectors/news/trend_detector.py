"""신규 핫 토픽 자동 감지.

기존 이슈에 분류 안 된 뉴스에서 키워드 클러스터를 찾아
새 GeoIssue를 자동 생성한다. 토큰은 새 이슈 감지 시에만 1회 사용.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

_DETECTED_FILE = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data" / "cache" / "detected_trends.json"
)

# 너무 일반적인 단어 제외
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need",
    "of", "in", "to", "for", "with", "on", "at", "from", "by",
    "about", "as", "into", "through", "during", "before", "after",
    "and", "but", "or", "nor", "not", "no", "so", "if", "then",
    "than", "too", "very", "just", "also", "more", "most", "other",
    "new", "says", "said", "report", "reports", "news", "today",
    "year", "years", "market", "markets", "stock", "stocks",
    "that", "this", "it", "its", "they", "their", "them", "we",
    "our", "you", "your", "he", "she", "his", "her", "who",
    "what", "when", "where", "how", "why", "which", "all", "each",
    "up", "out", "over", "after", "first", "last", "next", "still",
    # 한국어 일반
    "있다", "없다", "되다", "하다", "이다", "그리고", "하는", "대한",
    "위한", "통한", "따른", "것으로", "것이", "수도", "전망",
}

# 새 이슈 감지 임계값
MIN_NEWS_COUNT = 5       # 24시간 내 최소 5건
MIN_KEYWORD_FREQ = 3     # 같은 키워드 3회 이상
MAX_AUTO_ISSUES = 3      # 한 번에 최대 3개 자동 생성


def extract_keywords(title: str) -> list[str]:
    """제목에서 의미있는 키워드를 추출한다."""
    # 영어: 2글자 이상 단어
    en_words = re.findall(r"[A-Za-z]{2,}", title)
    # 한글: 2글자 이상 단어
    ko_words = re.findall(r"[가-힣]{2,}", title)

    keywords = []
    for w in en_words:
        wl = w.lower()
        if wl not in _STOPWORDS and len(wl) >= 3:
            keywords.append(wl)
    for w in ko_words:
        if w not in _STOPWORDS and len(w) >= 2:
            keywords.append(w)

    return keywords


def detect_emerging_topics(
    unclassified_news: list[dict],
) -> list[dict]:
    """분류 안 된 뉴스에서 새로운 핫 토픽을 감지한다.

    Args:
        unclassified_news: 기존 이슈에 매칭 안 된 뉴스 리스트
            [{"title": ..., "source": ..., "content": ...}, ...]

    Returns:
        감지된 토픽 리스트
        [{"keywords": [...], "count": N, "sample_titles": [...], "top_keyword": "..."}, ...]
    """
    if len(unclassified_news) < MIN_NEWS_COUNT:
        return []

    # 1. 모든 뉴스에서 키워드 추출
    keyword_counter = Counter()
    keyword_to_titles: dict[str, list[str]] = {}

    for news in unclassified_news:
        title = news.get("title", "")
        keywords = extract_keywords(title)
        for kw in set(keywords):  # 같은 뉴스 내 중복 제거
            keyword_counter[kw] += 1
            if kw not in keyword_to_titles:
                keyword_to_titles[kw] = []
            keyword_to_titles[kw].append(title)

    # 2. 빈도 높은 키워드 클러스터 찾기
    hot_keywords = [
        (kw, count) for kw, count in keyword_counter.most_common(50)
        if count >= MIN_KEYWORD_FREQ
    ]

    if not hot_keywords:
        return []

    # 3. 키워드를 클러스터로 묶기 (같은 뉴스에 동시 등장하는 키워드)
    clusters = []
    used_keywords = set()

    for kw, count in hot_keywords:
        if kw in used_keywords:
            continue

        # 이 키워드와 동시 등장하는 키워드 찾기
        co_occurring = Counter()
        titles_with_kw = keyword_to_titles.get(kw, [])
        for title in titles_with_kw:
            for other_kw in extract_keywords(title):
                if other_kw != kw and other_kw not in used_keywords:
                    co_occurring[other_kw] += 1

        cluster_keywords = [kw]
        for co_kw, co_count in co_occurring.most_common(5):
            if co_count >= 2:
                cluster_keywords.append(co_kw)
                used_keywords.add(co_kw)

        used_keywords.add(kw)

        clusters.append({
            "keywords": cluster_keywords,
            "count": count,
            "top_keyword": kw,
            "sample_titles": titles_with_kw[:5],
        })

    # 4. 건수 순 정렬, 최대 MAX_AUTO_ISSUES개
    clusters.sort(key=lambda c: c["count"], reverse=True)
    return clusters[:MAX_AUTO_ISSUES]


def _strip_code_block(text: str) -> str:
    """마크다운 코드블록(```json ... ```)을 제거한다."""
    if "```" in text:
        start = text.find("```")
        first_nl = text.find("\n", start)
        end = text.find("```", first_nl)
        if end > first_nl:
            return text[first_nl:end].strip()
    return text.strip()


def _call_gemini(prompt: str) -> str | None:
    """Gemini CLI를 headless 모드로 호출한다."""
    import subprocess

    try:
        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if result.returncode != 0:
            print(f"    Gemini 종료 코드 {result.returncode}: {result.stderr[:100]}")
            return None
        return result.stdout.strip()
    except FileNotFoundError:
        print("    Gemini CLI 미설치")
        return None
    except subprocess.TimeoutExpired:
        print("    Gemini 타임아웃 (90초)")
        return None
    except Exception as e:
        print(f"    Gemini 호출 실패: {e}")
        return None


def _call_ollama(prompt: str) -> str | None:
    """Ollama 로컬 LLM을 호출한다 (fallback)."""
    import requests as _req

    try:
        resp = _req.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma3:4b", "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"    Ollama 호출 실패: {e}")
        return None


def create_issue_from_trend(
    trend: dict,
    unclassified_news: list[dict],
) -> dict | None:
    """감지된 트렌드에서 GeoIssue를 자동 생성한다.

    1차: Gemini CLI (gemini -p), 2차: Ollama (fallback).

    Returns:
        생성된 이슈 정보 또는 None.
    """
    # 관련 뉴스 제목들
    sample = "\n".join(f"- {t}" for t in trend["sample_titles"][:10])
    keywords = ", ".join(trend["keywords"][:5])

    prompt = f"""Based on these news headlines sharing the keywords [{keywords}]:

{sample}

Create a geopolitical/market issue entry. Output ONLY valid JSON (no markdown, no explanation):
{{
  "title": "<Korean issue name, max 20 chars>",
  "description": "<Korean 1-2 sentence description>",
  "severity": "<critical|major|moderate>",
  "entities": [
    {{"name": "<English canonical>", "entity_type": "<country|company|commodity|institution>", "aliases": ["<Korean>"]}}
  ],
  "keywords": ["<keyword for news matching>", ...]
}}"""

    # 1차: Gemini CLI
    content = _call_gemini(prompt)
    source = "Gemini"

    # 2차: Ollama fallback
    if not content:
        print("    → Ollama fallback 시도")
        content = _call_ollama(prompt)
        source = "Ollama"

    if not content:
        return None

    try:
        content = _strip_code_block(content)
        result = json.loads(content)
        print(f"    ✓ 이슈 생성 ({source}): {result.get('title', '?')}")
        return result
    except (json.JSONDecodeError, ValueError) as e:
        print(f"    JSON 파싱 실패 ({source}): {e}")
        print(f"    원본: {content[:200]}")
        return None


def get_already_detected() -> set[str]:
    """이미 감지된 토픽 키워드를 로드한다 (중복 생성 방지)."""
    if not _DETECTED_FILE.exists():
        return set()
    try:
        data = json.loads(_DETECTED_FILE.read_text())
        return {d.get("top_keyword", "") for d in data}
    except (json.JSONDecodeError, ValueError):
        return set()


def save_detected(trends: list[dict]) -> None:
    """감지된 토픽을 저장한다."""
    _DETECTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if _DETECTED_FILE.exists():
        try:
            existing = json.loads(_DETECTED_FILE.read_text())
        except (json.JSONDecodeError, ValueError):
            existing = []

    for t in trends:
        existing.append({
            "top_keyword": t["top_keyword"],
            "keywords": t["keywords"],
            "detected_at": datetime.now(timezone.utc).isoformat(),
        })

    # 최근 100개만 보존
    existing = existing[-100:]
    _DETECTED_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
