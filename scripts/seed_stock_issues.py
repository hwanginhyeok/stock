#!/usr/bin/env python3
"""주식 이슈 시딩 — US/KR 시장별 재무적/기술적/시황적 이슈 생성."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.database import init_db
from src.core.models import GeoIssue, GeoIssueStatus, Severity
from src.storage import GeoIssueRepository

# ── US Market 이슈 ───────────────────────────────────────────────────────────

US_ISSUES = [
    # 시황적 분석
    {
        "title": "Fed 금리 정책",
        "description": "연준 금리 결정, FOMC 회의, 파월 발언, 금리 전망이 시장에 미치는 영향",
        "severity": "critical",
        "category": "stock_us",
        "analysis_type": "market",
    },
    {
        "title": "미국 고용·인플레이션",
        "description": "CPI, PPI, 고용지표(NFP), 소비자심리 등 거시경제 데이터",
        "severity": "major",
        "category": "stock_us",
        "analysis_type": "market",
    },
    {
        "title": "달러·채권 동향",
        "description": "DXY 달러인덱스, 미국채 10년물 금리, 달러 강세/약세 흐름",
        "severity": "major",
        "category": "stock_us",
        "analysis_type": "market",
    },
    # 재무적 분석
    {
        "title": "빅테크 실적",
        "description": "AAPL, MSFT, GOOGL, AMZN, META 실적 발표 및 가이던스",
        "severity": "critical",
        "category": "stock_us",
        "analysis_type": "fundamental",
    },
    {
        "title": "테슬라·일론머스크",
        "description": "TSLA 실적, 생산량, FSD, 로보택시, xAI, SpaceX 연관 이슈",
        "severity": "critical",
        "category": "stock_us",
        "analysis_type": "fundamental",
    },
    {
        "title": "AI·반도체 실적",
        "description": "NVDA, AMD, AVGO, TSM 실적 및 AI 수요 전망",
        "severity": "critical",
        "category": "stock_us",
        "analysis_type": "fundamental",
    },
    # 기술적 분석
    {
        "title": "S&P500·나스닥 추세",
        "description": "주요 지수 기술적 분석, 지지/저항, 이동평균, RSI, 추세 전환",
        "severity": "major",
        "category": "stock_us",
        "analysis_type": "technical",
    },
    {
        "title": "VIX·변동성",
        "description": "공포지수 VIX, 풋콜비율, 옵션 시장 변동성 신호",
        "severity": "major",
        "category": "stock_us",
        "analysis_type": "technical",
    },
]

# ── KR Market 이슈 ───────────────────────────────────────────────────────────

KR_ISSUES = [
    # 시황적 분석
    {
        "title": "한국은행 금리",
        "description": "한은 기준금리, 금통위, 총재 발언, 국내 금리 전망",
        "severity": "critical",
        "category": "stock_kr",
        "analysis_type": "market",
    },
    {
        "title": "원달러 환율",
        "description": "원/달러 환율 동향, 외환시장 개입, 수출입 영향",
        "severity": "major",
        "category": "stock_kr",
        "analysis_type": "market",
    },
    {
        "title": "수출입·경기지표",
        "description": "수출입 동향, GDP, 소비자물가, 경기선행지수",
        "severity": "major",
        "category": "stock_kr",
        "analysis_type": "market",
    },
    # 재무적 분석
    {
        "title": "삼성전자·반도체",
        "description": "삼성전자 실적, HBM, 파운드리, 메모리 시장 동향",
        "severity": "critical",
        "category": "stock_kr",
        "analysis_type": "fundamental",
    },
    {
        "title": "SK하이닉스·AI메모리",
        "description": "SK하이닉스 실적, HBM3E, AI 서버용 메모리 수요",
        "severity": "critical",
        "category": "stock_kr",
        "analysis_type": "fundamental",
    },
    {
        "title": "현대차·전기차",
        "description": "현대차/기아 실적, 전기차 판매, 미국 공장, 로보틱스",
        "severity": "major",
        "category": "stock_kr",
        "analysis_type": "fundamental",
    },
    {
        "title": "2차전지·배터리",
        "description": "LG에너지, 삼성SDI, SK이노 실적, 배터리 수주, IRA 보조금",
        "severity": "major",
        "category": "stock_kr",
        "analysis_type": "fundamental",
    },
    # 기술적 분석
    {
        "title": "코스피·코스닥 추세",
        "description": "코스피/코스닥 기술적 분석, 외국인·기관 수급, 프로그램 매매",
        "severity": "major",
        "category": "stock_kr",
        "analysis_type": "technical",
    },
]


# ── 이슈별 뉴스 매칭 키워드 ──────────────────────────────────────────────────

STOCK_KEYWORDS: dict[str, list[str]] = {
    # US - 시황
    "Fed 금리 정책": [
        "fed", "fomc", "powell", "파월", "federal reserve", "연준",
        "interest rate", "기준금리", "rate cut", "금리 인하", "rate hike",
    ],
    "미국 고용·인플레이션": [
        "CPI", "PPI", "inflation", "인플레이션", "nonfarm", "고용",
        "unemployment", "실업률", "consumer sentiment", "소비자심리",
        "jobs report", "PCE",
    ],
    "달러·채권 동향": [
        "DXY", "dollar index", "달러인덱스", "treasury", "국채",
        "10-year yield", "bond", "채권", "dollar strength", "달러 강세",
    ],
    # US - 재무
    "빅테크 실적": [
        "apple earnings", "microsoft earnings", "google earnings",
        "amazon earnings", "meta earnings", "AAPL", "MSFT", "GOOGL",
        "AMZN", "META", "빅테크 실적", "mag seven", "매그니피센트",
    ],
    "테슬라·일론머스크": [
        "tesla", "테슬라", "TSLA", "elon musk", "일론", "머스크",
        "FSD", "robotaxi", "로보택시", "cybertruck", "사이버트럭",
        "xAI", "spacex", "starlink",
    ],
    "AI·반도체 실적": [
        "nvidia earnings", "NVDA", "엔비디아 실적", "AMD earnings",
        "broadcom", "AVGO", "TSM earnings", "AI demand", "AI 수요",
        "data center", "데이터센터", "GPU",
    ],
    # US - 기술
    "S&P500·나스닥 추세": [
        "S&P 500", "S&P500", "nasdaq", "나스닥", "SPX", "QQQ",
        "bull market", "bear market", "강세장", "약세장",
        "all-time high", "correction", "조정",
    ],
    "VIX·변동성": [
        "VIX", "volatility", "변동성", "fear index", "공포지수",
        "put call ratio", "옵션", "options",
    ],
    # KR - 시황
    "한국은행 금리": [
        "한국은행", "금통위", "기준금리", "한은", "BOK",
        "이창용", "금리 동결", "금리 인하",
    ],
    "원달러 환율": [
        "원달러", "환율", "USD/KRW", "원화", "외환시장",
        "환율 방어", "달러 매도",
    ],
    "수출입·경기지표": [
        "수출", "수입", "무역수지", "경상수지", "GDP",
        "소비자물가", "경기선행", "산업생산",
    ],
    # KR - 재무
    "삼성전자·반도체": [
        "삼성전자", "samsung electronics", "HBM", "파운드리",
        "foundry", "메모리", "DRAM", "NAND", "삼성 실적",
    ],
    "SK하이닉스·AI메모리": [
        "SK하이닉스", "sk hynix", "HBM3E", "AI메모리",
        "하이닉스 실적", "HBM 수주",
    ],
    "현대차·전기차": [
        "현대차", "기아", "hyundai", "kia", "전기차", "EV",
        "현대 실적", "기아 실적", "로보틱스", "보스턴다이나믹스",
    ],
    "2차전지·배터리": [
        "LG에너지", "삼성SDI", "SK이노", "배터리", "battery",
        "2차전지", "IRA", "전고체", "리튬",
    ],
    # KR - 기술
    "코스피·코스닥 추세": [
        "코스피", "코스닥", "KOSPI", "KOSDAQ", "외국인 매수",
        "기관 매도", "프로그램 매매", "외국인 수급",
    ],
}


def main() -> None:
    init_db()
    repo = GeoIssueRepository()

    # 기존 이슈 제목 조회 (중복 방지)
    existing = {issue.title for issue in repo.get_many(limit=500)}
    created = 0

    for issue_data in US_ISSUES + KR_ISSUES:
        if issue_data["title"] in existing:
            print(f"  ✓ 이미 존재: {issue_data['title']}")
            continue

        issue = GeoIssue(
            title=issue_data["title"],
            description=issue_data["description"],
            severity=Severity(issue_data["severity"]),
            status=GeoIssueStatus.ACTIVE,
            category=issue_data["category"],
            analysis_type=issue_data["analysis_type"],
        )
        repo.create(issue)
        created += 1
        print(f"  + 생성: [{issue_data['category']}] {issue_data['title']} ({issue_data['analysis_type']})")

    print(f"\n완료 — {created}개 이슈 생성")


if __name__ == "__main__":
    main()
