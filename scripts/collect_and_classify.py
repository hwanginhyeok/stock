#!/usr/bin/env python3
"""뉴스 수집 + 즉시 분류 (15분 cron용).

뉴스를 수집하고 키워드 기반으로 이슈에 분류한다.
AI 토큰 사용 없음 — 규칙 기반 분류만.

cron (15분):
    */15 * * * * cd ~/stock && python3 scripts/collect_and_classify.py >> logs/news_collect.log 2>&1
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main() -> None:
    print(f"\n[{_now()}] === 뉴스 수집 + 분류 시작 ===")

    # 1. 뉴스 수집 (모든 마켓)
    for market in ["us", "kr", "tesla", "geopolitics"]:
        try:
            result = subprocess.run(
                ["python3", "scripts/collect_news.py", "--market", market],
                capture_output=True, text=True, timeout=60,
                cwd=str(_PROJECT_ROOT),
            )
            if result.returncode == 0:
                # 수집 건수 파악
                output = result.stdout.strip()
                count = output.count("stored") if "stored" in output else "?"
                print(f"  [{market:12s}] 수집 완료")
            else:
                # 일부 소스 실패는 정상 (RSS 다운 등)
                print(f"  [{market:12s}] 일부 실패 (계속 진행)")
        except subprocess.TimeoutExpired:
            print(f"  [{market:12s}] 타임아웃 (60초)")
        except Exception as e:
            print(f"  [{market:12s}] 에러: {e}")

    # 2. 최근 뉴스 분류
    print(f"\n[{_now()}] 뉴스 분류 중...")

    from src.core.database import init_db
    from src.storage import NewsRepository
    from src.collectors.news.classifier import classify_batch, update_source_scores

    init_db()
    repo = NewsRepository()
    recent = repo.get_latest(limit=100)

    news_dicts = [
        {"title": n.title, "content": n.content or n.summary or "", "source": n.source}
        for n in recent
    ]
    classified = classify_batch(news_dicts)

    # 분류 결과 요약
    issue_counts: dict[str, int] = {}
    for c in classified:
        for issue in c.issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

    if issue_counts:
        print("  분류 결과:")
        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
            print(f"    {issue:25s} — {count}건")
    else:
        print("  관련 뉴스 없음")

    # 3. 소스 점수 갱신
    scores = update_source_scores(classified)
    top_sources = sorted(scores.values(), key=lambda s: s.score, reverse=True)[:5]
    if top_sources:
        print(f"\n  소스 TOP 5:")
        for s in top_sources:
            print(f"    {s.name:20s} — 점수: {s.score:5.1f} "
                  f"(관련: {s.relevant_articles}/{s.total_articles})")

    print(f"\n[{_now()}] === 완료 ===")


if __name__ == "__main__":
    main()
