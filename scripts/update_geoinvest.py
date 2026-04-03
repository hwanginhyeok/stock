#!/usr/bin/env python3
"""GeoInvest 자동 업데이트 — 뉴스 수집 + 키워드 매칭 (AI 호출 없음).

cron으로 10분마다 실행:
    */10 * * * * cd ~/stock && python3 scripts/update_geoinvest.py --skip-collect >> logs/geoinvest_update.log 2>&1

뉴스 수집 포함 (15분 cron에서 이미 돌고 있으므로 보통 --skip-collect 사용):
    python scripts/update_geoinvest.py

엔티티/관계 추출은 Claude Code 세션에서 직접 수행 (API 비용 0원).
이 스크립트는 뉴스 수집 + 이슈별 관련 뉴스 필터링 + 요약만 담당.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# 이슈별 키워드 (뉴스 필터링용)
ISSUE_KEYWORDS = {
    "이란 전쟁": [
        "iran", "이란", "호르무즈", "hormuz", "hezbollah", "헤즈볼라",
        "후티", "houthi", "중동", "middle east", "이스라엘 전쟁",
    ],
    "비트코인 지정학": [
        "bitcoin", "비트코인", "crypto", "크립토", "가상자산", "stablecoin",
        "스테이블코인", "SEC crypto", "ETF 비트코인", "CBDC", "디지털화폐",
        "USDT", "USDC", "tether", "테더",
    ],
    "IMEC 회랑": [
        "IMEC", "인도 중동 유럽", "경제 회랑", "일대일로", "belt and road",
        "BRI", "하이파", "피레우스", "suez", "수에즈",
    ],
    "트럼프 관세전쟁 2.0": [
        "tariff", "관세", "trade war", "무역전쟁", "301조", "section 301",
        "상호관세", "reciprocal", "USTR", "무역대표", "관세 위헌",
        "section 122", "무역 협정",
    ],
    "AI/반도체 패권전쟁": [
        "AI chip", "AI칩", "export control", "수출통제", "nvidia",
        "엔비디아", "TSMC", "huawei", "화웨이", "ASML",
        "반도체 제재", "chips act", "칩스법", "H100", "H200",
        "ascend", "CoWoS", "HBM",
    ],
    "러시아-우크라이나 전쟁": [
        "russia", "러시아", "ukraine", "우크라이나", "nato", "나토",
        "zelensky", "젤렌스키", "putin", "푸틴", "crimea", "크림",
        "donbas", "돈바스",
    ],
    "대만 해협 위기": [
        "taiwan strait", "대만 해협", "taiwan china", "대만 중국",
        "cross-strait", "양안", "PLA taiwan", "대만 군사",
    ],
    "유럽 정치 위기": [
        "france politics", "프랑스 정치", "germany coalition", "독일 연립",
        "le pen", "르펜", "macron", "마크롱", "scholz", "숄츠",
        "EU crisis", "유럽 위기", "populism europe",
    ],
    "글로벌 AI 규제 경쟁": [
        "AI regulation", "AI 규제", "EU AI Act", "AI법",
        "openai regulation", "AI safety", "AI 안전",
        "deepfake law", "AI governance",
    ],
    "일본 금리 전환 (BOJ)": [
        "BOJ", "bank of japan", "일본은행", "일본 금리",
        "yen carry", "엔 캐리", "japanese yen", "엔화",
        "japan rate", "ueda", "우에다",
    ],
}


def collect_news() -> None:
    """뉴스 수집 실행."""
    print(f"[{_now()}] 뉴스 수집 시작...")
    for market in ["us", "kr"]:
        try:
            result = subprocess.run(
                ["python3", "scripts/collect_news.py", "--market", market],
                capture_output=True, text=True, timeout=120,
                cwd=str(_PROJECT_ROOT),
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                print(f"  [{market}] 수집 완료 ({len(lines)} lines output)")
            else:
                print(f"  [{market}] 수집 실패: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print(f"  [{market}] 수집 타임아웃 (120초)")
        except Exception as e:
            print(f"  [{market}] 수집 에러: {e}")


def find_relevant_news(issue_name: str) -> list[dict]:
    """이슈별 키워드로 최근 뉴스를 필터링한다."""
    from sqlalchemy import or_, select

    from src.core.database import NewsItemDB, get_session

    keywords = ISSUE_KEYWORDS.get(issue_name, [])
    if not keywords:
        return []

    with get_session() as session:
        conditions = [NewsItemDB.title.ilike(f"%{kw}%") for kw in keywords]
        stmt = (
            select(NewsItemDB)
            .where(or_(*conditions))
            .order_by(NewsItemDB.created_at.desc())
            .limit(20)
        )
        rows = session.execute(stmt).scalars().all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "content": r.content or "",
                "summary": r.summary or "",
                "source": r.source,
                "published_at": str(r.published_at or r.created_at),
            }
            for r in rows
        ]


def _save_pending_news(issue_name: str, news: list[dict]) -> Path:
    """관련 뉴스를 JSON으로 저장 — Claude Code 세션에서 분석용."""
    pending_dir = _PROJECT_ROOT / "data" / "geoinvest" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    slug = issue_name.replace(" ", "_").replace("/", "_")
    path = pending_dir / f"{ts}_{slug}.json"

    payload = {
        "issue": issue_name,
        "collected_at": _now(),
        "news_count": len(news),
        "articles": [
            {
                "title": n["title"],
                "source": n["source"],
                "published_at": n["published_at"],
                "summary": (n.get("summary") or n.get("content", ""))[:500],
            }
            for n in news
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main() -> None:
    parser = argparse.ArgumentParser(description="GeoInvest 자동 업데이트 (뉴스 수집만)")
    parser.add_argument("--skip-collect", action="store_true", help="뉴스 수집 건너뛰기")
    parser.add_argument("--issue", type=str, default=None, help="특정 이슈만 업데이트")
    parser.add_argument("--verbose", action="store_true", help="뉴스 제목 출력")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"GeoInvest 뉴스 수집 — {_now()}")
    print(f"{'='*50}")

    # 1. 뉴스 수집
    if not args.skip_collect:
        collect_news()

    # 2. DB 초기화
    from src.core.database import init_db
    init_db()

    # 3. 이슈별 관련 뉴스 필터링 + pending 저장
    issues = [args.issue] if args.issue else list(ISSUE_KEYWORDS.keys())
    total_news = 0
    saved_files = 0

    for issue_name in issues:
        news = find_relevant_news(issue_name)
        count = len(news)
        total_news += count

        if not news:
            continue

        # 새 뉴스가 있으면 pending에 저장
        path = _save_pending_news(issue_name, news)
        saved_files += 1
        print(f"  {issue_name}: {count}개 뉴스 → {path.name}")

        if args.verbose:
            for n in news[:5]:
                print(f"    - {n['title'][:80]}")

    print(f"\n[{_now()}] 완료 — {total_news}개 뉴스, {saved_files}개 이슈 저장")
    print("  → 엔티티/관계 추출은 Claude Code 세션에서 수행")


if __name__ == "__main__":
    main()
