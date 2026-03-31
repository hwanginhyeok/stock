"""GeoInvest 이슈 랭킹 알고리즘.

뉴스 볼륨, 가속도, severity, 이벤트 신선도를 조합하여
이슈 순위를 매일 갱신한다. AI 토큰 0.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

_RANK_HISTORY_FILE = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "data" / "cache" / "issue_rankings.json"
)


@dataclass
class IssueRank:
    """이슈 랭킹 결과."""

    issue_id: str
    title: str
    rank: int = 0
    score: float = 0.0
    news_24h: int = 0
    news_48h: int = 0
    velocity: float = 0.0  # 24h/48h 비율 (>1 = 가속)
    severity_score: float = 0.0
    recency_score: float = 0.0
    event_count: int = 0
    trend: str = ""  # "↑", "↓", "→"


_SEVERITY_WEIGHTS = {"critical": 3.0, "major": 2.0, "moderate": 1.0, "minor": 0.5}


def compute_rankings(issues: list[dict], news_counts: dict[str, dict]) -> list[IssueRank]:
    """이슈 랭킹을 계산한다.

    Args:
        issues: GeoIssue 목록 [{"id", "title", "severity", "event_ids", ...}]
        news_counts: 이슈별 뉴스 카운트 {"issue_title": {"24h": N, "48h": N}}

    Returns:
        점수 순으로 정렬된 IssueRank 리스트.
    """
    now = datetime.now(timezone.utc)
    ranks = []

    for issue in issues:
        title = issue.get("title", "")
        counts = news_counts.get(title, {"24h": 0, "48h": 0})
        n24 = counts.get("24h", 0)
        n48 = counts.get("48h", 0)

        # 뉴스 가속도 (24h / 48h)
        velocity = n24 / max(n48, 1)

        # severity 점수
        sev = issue.get("severity", "moderate")
        sev_score = _SEVERITY_WEIGHTS.get(sev, 1.0)

        # 이벤트 신선도 (최근 이벤트가 가까울수록 높음)
        recency = 0.0
        last_event_at = issue.get("last_event_at")
        if last_event_at:
            if isinstance(last_event_at, str):
                try:
                    last_event_at = datetime.fromisoformat(last_event_at.replace("Z", "+00:00"))
                except ValueError:
                    last_event_at = None
            if last_event_at:
                if last_event_at.tzinfo is None:
                    last_event_at = last_event_at.replace(tzinfo=timezone.utc)
                days_ago = (now - last_event_at).days
                recency = max(0, 10 - days_ago) / 10  # 10일 이내면 1.0, 이후 감쇠

        # 이벤트 수
        event_count = issue.get("event_count", 0)

        # 종합 점수 (0-100 스케일)
        score = (
            (n24 * 3.0) * 0.40          # 뉴스 볼륨 (40%)
            + (velocity * 10) * 0.20     # 가속도 (20%)
            + (sev_score * 10) * 0.15    # severity (15%)
            + (recency * 30) * 0.15      # 신선도 (15%)
            + (event_count * 2) * 0.10   # 이벤트 수 (10%)
        )

        # 트렌드
        if velocity > 1.3:
            trend = "↑"
        elif velocity < 0.7:
            trend = "↓"
        else:
            trend = "→"

        ranks.append(IssueRank(
            issue_id=issue["id"],
            title=title,
            score=round(score, 1),
            news_24h=n24,
            news_48h=n48,
            velocity=round(velocity, 2),
            severity_score=sev_score,
            recency_score=round(recency, 2),
            event_count=event_count,
            trend=trend,
        ))

    # 점수 순 정렬
    ranks.sort(key=lambda r: r.score, reverse=True)
    for i, r in enumerate(ranks):
        r.rank = i + 1

    return ranks


def count_news_by_issue(issue_keywords: dict[str, list[str]]) -> dict[str, dict]:
    """이슈별 24h/48h 뉴스 건수를 카운트한다.

    Args:
        issue_keywords: {"이슈명": ["keyword1", "keyword2", ...]}

    Returns:
        {"이슈명": {"24h": N, "48h": N}}
    """
    from sqlalchemy import func, or_, select

    from src.core.database import NewsItemDB, get_session

    now = datetime.now(timezone.utc)
    t24 = now - timedelta(hours=24)
    t48 = now - timedelta(hours=48)

    results = {}

    with get_session() as session:
        for issue_name, keywords in issue_keywords.items():
            if not keywords:
                results[issue_name] = {"24h": 0, "48h": 0}
                continue

            conditions = [NewsItemDB.title.ilike(f"%{kw}%") for kw in keywords[:10]]

            # 24h 카운트
            n24 = session.execute(
                select(func.count()).select_from(NewsItemDB).where(
                    or_(*conditions),
                    NewsItemDB.created_at >= t24,
                )
            ).scalar() or 0

            # 48h 카운트 (24-48h 구간)
            n48 = session.execute(
                select(func.count()).select_from(NewsItemDB).where(
                    or_(*conditions),
                    NewsItemDB.created_at >= t48,
                    NewsItemDB.created_at < t24,
                )
            ).scalar() or 0

            results[issue_name] = {"24h": n24, "48h": n48}

    return results


def save_daily_ranking(ranks: list[IssueRank]) -> None:
    """일일 랭킹을 히스토리에 저장한다."""
    _RANK_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    history = []
    if _RANK_HISTORY_FILE.exists():
        try:
            history = json.loads(_RANK_HISTORY_FILE.read_text())
        except (json.JSONDecodeError, ValueError):
            history = []

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = {
        "date": today,
        "rankings": [
            {
                "rank": r.rank,
                "title": r.title,
                "score": r.score,
                "news_24h": r.news_24h,
                "velocity": r.velocity,
                "trend": r.trend,
            }
            for r in ranks
        ],
    }

    # 같은 날짜면 덮어쓰기
    history = [h for h in history if h.get("date") != today]
    history.append(entry)

    # 최근 30일만 보존
    history = history[-30:]

    _RANK_HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2))


def get_previous_ranks() -> dict[str, int]:
    """전날 랭킹을 가져온다 (순위 변동 표시용)."""
    if not _RANK_HISTORY_FILE.exists():
        return {}
    try:
        history = json.loads(_RANK_HISTORY_FILE.read_text())
        if len(history) < 2:
            return {}
        prev = history[-2]  # 어제
        return {r["title"]: r["rank"] for r in prev.get("rankings", [])}
    except (json.JSONDecodeError, ValueError, IndexError):
        return {}
