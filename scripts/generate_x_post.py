#!/usr/bin/env python3
"""DB 뉴스 기반 X 시황 포스트 자동 생성 + 텔레그램 전송.

사용법:
    python3 scripts/generate_x_post.py                  # 전체 시황
    python3 scripts/generate_x_post.py --category stock_us  # US만
    python3 scripts/generate_x_post.py --category stock_kr  # KR만
    python3 scripts/generate_x_post.py --category geo       # 지정학만
    python3 scripts/generate_x_post.py --dry-run            # 텔레그램 전송 안 함
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests as http_requests
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# 텔레그램 설정
load_dotenv(_PROJECT_ROOT.parent / "x-bot" / ".env")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Ollama 설정
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"


# ── DB에서 뉴스 수집 ─────────────────────────────────────────────────────────

def get_top_news_by_category(category: str, limit: int = 15) -> list[dict]:
    """카테고리별 상위 이슈의 최신 뉴스를 수집한다."""
    from sqlalchemy import or_, select

    from src.core.database import NewsItemDB, get_session, init_db
    from src.storage import GeoIssueRepository

    init_db()
    repo = GeoIssueRepository()
    all_issues = repo.get_active()
    issues = [i for i in all_issues if getattr(i, "category", "geo") == category]

    # 키워드 소스
    if category == "geo":
        from src.collectors.news.classifier import ISSUE_RULES
        kw_source = {
            title: [kw for kw, _ in rules[:8]]
            for title, rules in ISSUE_RULES.items()
        }
    else:
        from scripts.seed_stock_issues import STOCK_KEYWORDS
        kw_source = STOCK_KEYWORDS

    # 이슈별 뉴스 수집
    t24 = datetime.now(timezone.utc) - timedelta(hours=24)
    results = []

    with get_session() as session:
        for issue in issues[:8]:  # 상위 8개 이슈
            keywords = kw_source.get(issue.title, [])
            if not keywords:
                continue

            conditions = [NewsItemDB.title.ilike(f"%{kw}%") for kw in keywords[:8]]
            stmt = (
                select(NewsItemDB)
                .where(or_(*conditions), NewsItemDB.created_at >= t24)
                .order_by(NewsItemDB.created_at.desc())
                .limit(5)
            )
            rows = session.execute(stmt).scalars().all()

            if rows:
                results.append({
                    "issue": issue.title,
                    "analysis_type": getattr(issue, "analysis_type", ""),
                    "severity": issue.severity,
                    "news": [
                        {"title": r.title, "source": r.source}
                        for r in rows
                    ],
                })

    return results


# ── Ollama 글 생성 ───────────────────────────────────────────────────────────

CATEGORY_NAMES = {
    "geo": "지정학",
    "stock_us": "미국 증시",
    "stock_kr": "한국 증시",
}

PROMPT_TEMPLATE = """당신은 한국인 투자자를 위한 시황 분석가입니다.
아래 뉴스를 바탕으로 X(트위터)에 올릴 시황 포스트를 작성하세요.

카테고리: {category_name}

뉴스 데이터:
{news_data}

작성 규칙:
1. 한국어로 작성
2. 핵심만 간결하게 (X 포스트 1개 분량, 200-500자)
3. 이슈별로 한 줄 요약 (글머리 기호 사용)
4. 시황 흐름/맥락을 읽어주는 한 줄 코멘트 추가
5. 투자 권유/추천 표현 절대 금지
6. 마지막에 해시태그 3-5개
7. 면책조항: "본 게시물은 정보 공유 목적이며 투자 권유가 아닙니다"

포스트만 출력하세요 (설명 불필요):"""


def generate_post(category: str, news_data: list[dict]) -> str:
    """Ollama로 X 포스트를 생성한다."""
    # 뉴스 데이터를 텍스트로 변환
    news_text = ""
    for item in news_data:
        atype = item.get("analysis_type", "")
        atype_label = {"fundamental": "재무", "technical": "기술", "market": "시황"}.get(atype, "")
        news_text += f"\n[{item['issue']}] ({atype_label})\n"
        for n in item["news"][:3]:
            news_text += f"  - {n['title']} ({n['source']})\n"

    prompt = PROMPT_TEMPLATE.format(
        category_name=CATEGORY_NAMES.get(category, category),
        news_data=news_text,
    )

    try:
        resp = http_requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        return f"[Ollama 에러: {e}]"


# ── 텔레그램 전송 ────────────────────────────────────────────────────────────

def send_telegram(text: str, category: str) -> bool:
    """텔레그램으로 포스트를 전송한다."""
    if not TG_TOKEN or not TG_CHAT_ID:
        print("  ⚠ 텔레그램 토큰/챗ID 없음")
        return False

    header = f"📝 X 포스트 초안 [{CATEGORY_NAMES.get(category, category)}]\n{'─' * 30}\n\n"
    footer = f"\n\n{'─' * 30}\n✅ 복사해서 X에 붙여넣기하세요"

    message = header + text + footer

    # 4096자 제한
    if len(message) > 4000:
        message = message[:3990] + "\n...(잘림)"

    try:
        resp = http_requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={
                "chat_id": TG_CHAT_ID,
                "text": message,
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"  ⚠ 텔레그램 전송 실패: {e}")
        return False


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="X 시황 포스트 생성")
    parser.add_argument("--category", type=str, default=None,
                        help="geo, stock_us, stock_kr (없으면 전체)")
    parser.add_argument("--dry-run", action="store_true",
                        help="텔레그램 전송 안 함")
    args = parser.parse_args()

    categories = [args.category] if args.category else ["stock_us", "stock_kr", "geo"]

    now = datetime.now()
    print(f"\n{'='*50}")
    print(f"X 포스트 생성 — {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")

    for category in categories:
        print(f"\n  [{CATEGORY_NAMES.get(category, category)}] 뉴스 수집 중...")
        news_data = get_top_news_by_category(category)

        if not news_data:
            print(f"    뉴스 없음 — 스킵")
            continue

        total_news = sum(len(item["news"]) for item in news_data)
        print(f"    {len(news_data)}개 이슈, {total_news}개 뉴스 → Ollama 생성 중...")

        post = generate_post(category, news_data)
        print(f"\n{'─'*40}")
        print(post)
        print(f"{'─'*40}")

        if args.dry_run:
            print("    [DRY-RUN] 텔레그램 전송 안 함")
        else:
            ok = send_telegram(post, category)
            print(f"    텔레그램: {'✅ 전송 완료' if ok else '❌ 실패'}")

    print(f"\n완료")


if __name__ == "__main__":
    main()
