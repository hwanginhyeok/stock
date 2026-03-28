"""First-principles analysis of ontology events.

Ontology 4th block: Event → Analysis
Takes clustered events and generates structured analysis using Claude.
Pattern: conventional wisdom → fundamental truths → gap → opportunity.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import yaml

from src.core.claude_client import ClaudeClient
from src.core.models import (
    FirstPrincipleAnalysis,
    Market,
    OntologyEvent,
)
from src.storage import (
    NewsFactRepository,
    OntologyEventRepository,
)

logger = logging.getLogger(__name__)

_CONFIG_PATH = "config/ontology_config.yaml"


def _load_config() -> dict[str, Any]:
    """Load ontology config."""
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_prompt(event: OntologyEvent, facts_text: str) -> str:
    """Build Claude prompt for first-principles analysis."""
    return f"""당신은 투자 분석가입니다. 아래 뉴스 이벤트에 대해 제1원칙 분석을 수행하세요.

## 이벤트
제목: {event.title}
요약: {event.summary}
심각도: {event.severity.value if hasattr(event.severity, 'value') else event.severity}
기사 수: {event.article_count}

## 관련 팩트
{facts_text}

## 분석 지시

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만.

{{
    "conventional_wisdom": "시장이 이 이벤트에 대해 당연시하는 가정 (1~2문장)",
    "fundamental_truths": [
        "가정을 제거하고 남는 순수한 팩트 1 (숫자 포함)",
        "가정을 제거하고 남는 순수한 팩트 2",
        "가정을 제거하고 남는 순수한 팩트 3"
    ],
    "gap": "통념이 말하는 것과 팩트가 말하는 것 사이의 괴리 (1~2문장)",
    "opportunity": "Gap에서 도출되는 투자 관점 (1~2문장, 매수/매도 추천 아님)"
}}"""


def analyze_event(
    event: OntologyEvent,
    fact_repo: NewsFactRepository,
    claude_client: ClaudeClient | None = None,
) -> FirstPrincipleAnalysis | None:
    """Run first-principles analysis on a single event.

    Args:
        event: Ontology event to analyze.
        fact_repo: Fact repository for retrieving related facts.
        claude_client: Optional Claude client (created if not provided).

    Returns:
        FirstPrincipleAnalysis or None if analysis fails.
    """
    config = _load_config()
    fpa_config = config.get("first_principle_analysis", {})

    # 최소 기사 수 체크
    min_articles = fpa_config.get("min_article_count", 3)
    if event.article_count < min_articles:
        logger.info(
            "이벤트 '%s' 기사 수 %d < 최소 %d, 스킵",
            event.title, event.article_count, min_articles,
        )
        return None

    # 관련 팩트 수집
    facts = fact_repo.get_by_event_id(event.id) if hasattr(fact_repo, 'get_by_event_id') else []
    if not facts:
        # fallback: 최근 팩트에서 이벤트 키워드로 검색
        all_facts = fact_repo.get_recent(hours=48)
        keywords = event.title.lower().split()
        facts = [
            f for f in all_facts
            if any(kw in f.claim.lower() for kw in keywords if len(kw) > 2)
        ]

    if not facts:
        logger.info("이벤트 '%s'에 관련 팩트 없음, 스킵", event.title)
        return None

    # 팩트 텍스트 구성
    facts_text = "\n".join(
        f"- [{f.fact_type}] {f.claim} (출처: {f.source_quote[:80]}...)"
        for f in facts[:10]  # 최대 10개
    )

    # Claude API 호출
    if claude_client is None:
        claude_client = ClaudeClient()

    prompt = _build_prompt(event, facts_text)

    try:
        response = claude_client.generate(
            prompt=prompt,
            model=fpa_config.get("model", "claude-sonnet-4-6"),
            max_tokens=fpa_config.get("max_tokens", 1500),
            temperature=fpa_config.get("temperature", 0.3),
        )

        # JSON 파싱
        result = json.loads(response)

        analysis = FirstPrincipleAnalysis(
            event_id=event.id,
            event_title=event.title,
            conventional_wisdom=result.get("conventional_wisdom", ""),
            fundamental_truths=result.get("fundamental_truths", []),
            gap=result.get("gap", ""),
            opportunity=result.get("opportunity", ""),
            related_fact_ids=[f.id for f in facts[:10]],
            market=event.market,
            status="draft",
        )

        logger.info("분석 완료: '%s'", event.title)
        return analysis

    except json.JSONDecodeError as e:
        logger.error("JSON 파싱 실패 (이벤트: %s): %s", event.title, e)
        return None
    except Exception as e:
        logger.error("분석 실패 (이벤트: %s): %s", event.title, e)
        return None


def analyze_top_events(
    hours: int = 24,
    market: str | None = None,
    max_events: int = 5,
) -> list[FirstPrincipleAnalysis]:
    """Analyze top events by article count.

    Args:
        hours: Lookback window.
        market: Optional market filter.
        max_events: Maximum events to analyze.

    Returns:
        List of FirstPrincipleAnalysis results.
    """
    config = _load_config()
    fpa_config = config.get("first_principle_analysis", {})
    min_articles = fpa_config.get("min_article_count", 3)

    event_repo = OntologyEventRepository()
    fact_repo = NewsFactRepository()

    # 기사 수 기준 상위 이벤트
    events = event_repo.get_active(market=market)
    events = [e for e in events if e.article_count >= min_articles]
    events.sort(key=lambda e: e.article_count, reverse=True)
    events = events[:max_events]

    if not events:
        logger.info("분석 대상 이벤트 없음 (최소 기사 수: %d)", min_articles)
        return []

    claude_client = ClaudeClient()
    results: list[FirstPrincipleAnalysis] = []

    for event in events:
        analysis = analyze_event(event, fact_repo, claude_client)
        if analysis:
            results.append(analysis)

    return results


def format_analysis_report(analyses: list[FirstPrincipleAnalysis]) -> str:
    """Format analyses into readable report.

    Args:
        analyses: List of completed analyses.

    Returns:
        Formatted markdown report.
    """
    if not analyses:
        return "분석 대상 이벤트 없음."

    lines = ["# 제1원칙 분석 리포트", ""]

    for i, a in enumerate(analyses, 1):
        lines.append(f"## {i}. {a.event_title}")
        lines.append("")
        lines.append(f"**통념**: {a.conventional_wisdom}")
        lines.append("")
        lines.append("**근본 진실**:")
        for truth in a.fundamental_truths:
            lines.append(f"  - {truth}")
        lines.append("")
        lines.append(f"**Gap**: {a.gap}")
        lines.append("")
        lines.append(f"**기회**: {a.opportunity}")
        lines.append("")
        lines.append(f"_상태: {a.status} | 시장: {a.market.value if hasattr(a.market, 'value') else a.market}_")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def extract_thesis_candidates(
    analyses: list[FirstPrincipleAnalysis],
    min_gap_length: int = 20,
) -> list[dict[str, str]]:
    """Extract article thesis candidates from analyses.

    Connects ontology → content pipeline.
    Gap이 충분히 구체적인 분석에서 아티클 테제 후보를 추출.

    Args:
        analyses: Completed analyses.
        min_gap_length: Minimum gap text length to qualify.

    Returns:
        List of thesis candidates with title, thesis, source_event.
    """
    candidates = []
    for a in analyses:
        if len(a.gap) < min_gap_length:
            continue

        candidates.append({
            "title": f"[테제 후보] {a.event_title}",
            "thesis": a.gap,
            "opportunity": a.opportunity,
            "source_event": a.event_title,
            "market": a.market.value if hasattr(a.market, 'value') else str(a.market),
            "fact_count": len(a.related_fact_ids),
        })

    return candidates
