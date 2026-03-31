"""뉴스 이슈 분류기 — 키워드 기반, AI 불필요.

뉴스 제목+본문에서 키워드를 매칭하여 GeoInvest 이슈에 분류한다.
소스 점수도 관리: 어떤 소스가 빠르고 정확한 뉴스를 주는지 추적.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_SCORE_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "cache" / "source_scores.json"

# 이슈별 키워드 (가중치 포함)
# (keyword, weight) — weight가 높을수록 해당 이슈에 강하게 매칭
ISSUE_RULES: dict[str, list[tuple[str, float]]] = {
    "이란 전쟁": [
        ("iran", 3.0), ("이란", 3.0), ("hormuz", 3.0), ("호르무즈", 3.0),
        ("hezbollah", 2.0), ("헤즈볼라", 2.0), ("houthi", 2.0), ("후티", 2.0),
        ("tehran", 2.0), ("테헤란", 2.0), ("irgc", 2.0),
        ("middle east", 1.0), ("중동", 1.0), ("gulf", 1.0), ("걸프", 1.0),
        ("oil price", 1.5), ("유가", 1.5), ("brent", 1.5),
    ],
    "비트코인 지정학": [
        ("bitcoin", 3.0), ("비트코인", 3.0), ("btc", 2.0),
        ("ethereum", 2.0), ("이더리움", 2.0), ("eth", 1.5),
        ("crypto", 2.0), ("크립토", 2.0), ("가상자산", 2.0),
        ("stablecoin", 2.5), ("스테이블코인", 2.5), ("usdt", 2.0), ("usdc", 2.0),
        ("cbdc", 2.0), ("디지털화폐", 2.0), ("digital yuan", 2.0),
        ("sec crypto", 2.5), ("coinbase", 1.5), ("binance", 1.5),
        ("defi", 1.5), ("nft", 1.0), ("web3", 1.0),
    ],
    "IMEC 회랑": [
        ("imec", 3.0), ("경제 회랑", 3.0), ("economic corridor", 3.0),
        ("belt and road", 2.0), ("일대일로", 2.0), ("bri", 1.5),
        ("haifa", 2.0), ("하이파", 2.0), ("piraeus", 2.0), ("피레우스", 2.0),
        ("suez", 1.5), ("수에즈", 1.5),
        ("india trade", 1.5), ("인도 무역", 1.5),
    ],
    "트럼프 관세전쟁 2.0": [
        ("tariff", 3.0), ("관세", 3.0), ("trade war", 2.5), ("무역전쟁", 2.5),
        ("section 301", 3.0), ("301조", 3.0), ("section 122", 2.5),
        ("reciprocal", 2.0), ("상호관세", 2.0),
        ("ustr", 2.0), ("무역대표", 2.0),
        ("ieepa", 2.0), ("supreme court tariff", 2.5),
        ("trade deal", 1.5), ("무역 협정", 1.5),
        ("import duty", 1.5), ("수입 관세", 1.5),
    ],
    "AI/반도체 패권전쟁": [
        ("nvidia", 2.5), ("엔비디아", 2.5), ("tsmc", 2.5),
        ("asml", 2.5), ("huawei", 2.0), ("화웨이", 2.0),
        ("ai chip", 3.0), ("ai칩", 3.0), ("export control", 2.5), ("수출통제", 2.5),
        ("chips act", 2.5), ("칩스법", 2.5),
        ("h100", 2.0), ("h200", 2.0), ("blackwell", 2.0),
        ("hbm", 2.0), ("cowos", 2.0), ("foundry", 1.5), ("파운드리", 1.5),
        ("semiconductor sanction", 2.0), ("반도체 제재", 2.0),
        ("ascend 910", 2.0), ("euv", 1.5),
        ("sk hynix", 1.5), ("sk하이닉스", 1.5),
        ("삼성전자 파운드리", 1.5), ("samsung foundry", 1.5),
    ],
}

# 분류 임계값
CLASSIFICATION_THRESHOLD = 2.0  # 이 점수 이상이면 분류


@dataclass
class ClassifiedNews:
    """분류된 뉴스."""

    title: str
    source: str
    issues: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    top_issue: str = ""


def classify_news(title: str, content: str = "") -> ClassifiedNews:
    """뉴스를 이슈별로 분류한다.

    Args:
        title: 뉴스 제목.
        content: 뉴스 본문 (선택).

    Returns:
        ClassifiedNews with matched issues and scores.
    """
    text = f"{title} {content[:500]}".lower()
    result = ClassifiedNews(title=title, source="")

    for issue_name, keywords in ISSUE_RULES.items():
        score = 0.0
        for keyword, weight in keywords:
            # 제목에 있으면 2배 가중
            if keyword.lower() in title.lower():
                score += weight * 2.0
            elif keyword.lower() in text:
                score += weight
        if score >= CLASSIFICATION_THRESHOLD:
            result.issues.append(issue_name)
            result.scores[issue_name] = round(score, 1)

    if result.scores:
        result.top_issue = max(result.scores, key=result.scores.get)

    return result


def classify_batch(news_items: list[dict]) -> list[ClassifiedNews]:
    """뉴스 배치를 분류한다.

    Args:
        news_items: [{"title": ..., "content": ..., "source": ...}, ...]

    Returns:
        List of ClassifiedNews.
    """
    results = []
    for item in news_items:
        c = classify_news(item.get("title", ""), item.get("content", ""))
        c.source = item.get("source", "")
        results.append(c)
    return results


# ============================================================
# 소스 점수 관리
# ============================================================


@dataclass
class SourceScore:
    """소스별 점수."""

    name: str
    total_articles: int = 0
    relevant_articles: int = 0  # 이슈에 분류된 기사 수
    relevance_rate: float = 0.0  # relevant / total
    avg_speed_rank: float = 0.0  # 같은 이슈를 몇 번째로 보도했는지 평균
    score: float = 0.0  # 종합 점수 (0-100)


def load_source_scores() -> dict[str, SourceScore]:
    """소스 점수 파일을 로드한다."""
    if not _SCORE_FILE.exists():
        return {}
    data = json.loads(_SCORE_FILE.read_text())
    return {k: SourceScore(**v) for k, v in data.items()}


def save_source_scores(scores: dict[str, SourceScore]) -> None:
    """소스 점수를 저장한다."""
    _SCORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {k: {
        "name": v.name, "total_articles": v.total_articles,
        "relevant_articles": v.relevant_articles,
        "relevance_rate": v.relevance_rate,
        "avg_speed_rank": v.avg_speed_rank, "score": v.score,
    } for k, v in scores.items()}
    _SCORE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def update_source_scores(classified: list[ClassifiedNews]) -> dict[str, SourceScore]:
    """분류 결과로 소스 점수를 갱신한다."""
    scores = load_source_scores()

    for c in classified:
        src = c.source
        if not src:
            continue
        if src not in scores:
            scores[src] = SourceScore(name=src)
        s = scores[src]
        s.total_articles += 1
        if c.issues:
            s.relevant_articles += 1

    # 점수 계산
    for s in scores.values():
        if s.total_articles > 0:
            s.relevance_rate = s.relevant_articles / s.total_articles
            # 점수 = 관련성 비율 * 100, 최소 10건 이상이면 신뢰
            confidence = min(1.0, s.total_articles / 10)
            s.score = round(s.relevance_rate * 100 * confidence, 1)

    save_source_scores(scores)
    return scores


def get_priority_sources(top_n: int = 10) -> list[str]:
    """점수 높은 소스 top_n개를 반환한다."""
    scores = load_source_scores()
    if not scores:
        return []  # 점수 데이터 없으면 전체 수집
    sorted_sources = sorted(scores.values(), key=lambda s: s.score, reverse=True)
    return [s.name for s in sorted_sources[:top_n]]
