#!/usr/bin/env python3
r"""실적 리포트 자동 생성 파이프라인.

cron: 0 8 * * * cd ~/stock && python3 scripts/earn_reporter.py >> ~/.pm_logs/earn_reporter_$(date +\%Y\%m\%d).log 2>&1
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
import yfinance as yf

# GLM 클라이언트 경로 추가
sys.path.insert(0, str(Path.home() / "project-manager/scripts"))
try:
    from glm_client import call_glm
except ImportError:
    print("Warning: glm_client not found. GLM calls will fail.", file=sys.stderr)
    call_glm = None

# =============================================================================
# 설정
# =============================================================================

# S&P500 + Nasdaq100 대형주 (상위 200개 시총)
MAJOR_TICKERS = frozenset({
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "BRK.B",
    "JPM", "V", "UNH", "MA", "JNJ", "WMT", "PG", "HD", "XOM", "BAC",
    "COST", "ABBV", "KO", "MRK", "PEP", "AVGO", "LLY", "TMO", "CSCO",
    "MCD", "ACN", "ADBE", "CRM", "AMD", "INTC", "QCOM", "TXN", "NFLX",
    "AMGN", "HON", "IBM", "CAT", "GE", "BA", "RTX", "SBUX", "BKNG",
    "NOW", "ISRG", "AMAT", "LRCX", "ADI", "REGN", "VRTX", "GILD",
    "MDLZ", "ADP", "PANW", "SNPS", "CDNS", "KLAC", "MRVL", "CME",
    "ORLY", "FTNT", "CSX", "ABNB", "DASH", "COIN", "CRWD", "DDOG",
    "SPOT", "NET", "ZS", "SNOW", "HOOD", "PLTR", "GM", "F", "UPS",
    "FDX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CL", "CVX", "SLB",
    "LIN", "UNP", "GS", "MS", "BLK", "SCHW", "AXP", "SPGI", "MMC",
    "CB", "PGR", "AFL", "MET", "TRV", "CI", "HUM", "ELV", "CVS",
    "MCK", "ABT", "SYK", "DHR", "BSX", "BDX", "ZTS", "EW",
    "DE", "ITW", "EMR", "ROK", "PH", "ETN", "GD", "LMT", "NOC",
    "NEE", "DUK", "SO", "AEP", "XEL", "SRE", "PCG", "WEC",
    "PLD", "AMT", "CCI", "EQIX", "SPG", "O", "PSA",
    "UBER", "LYFT", "SQ", "PYPL", "SHOP", "MELI", "SE",
})

# 요청 헤더
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 경로
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "earnings"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# 로그 설정
LOG_DIR = Path.home() / ".pm_logs"
LOG_DIR.mkdir(exist_ok=True)

# =============================================================================
# CSS 템플릿 (HOOD_2026Q1.html에서 추출)
# =============================================================================

CSS_TEMPLATE = """
  :root {
    --bg: #0a0a0a; --surface: #141414; --surface2: #1c1c1c;
    --border: #2a2a2a; --text: #e8e8e8; --text-dim: #888; --text-muted: #555;
    --accent: {accent_color}; --accent-dim: {accent_color}33;
    --red: #ff4d4d; --red-dim: #ff4d4d22;
    --yellow: #ffc107; --blue: #4da6ff;
    --purple: #b388ff; --purple-dim: #b388ff22;
  }
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--text); font-family:'IBM Plex Sans KR',-apple-system,sans-serif; font-size:15px; line-height:1.7; }}

  .hero {{ background:linear-gradient(135deg,{accent_color}15,#0a0a0a 60%); border-bottom:1px solid var(--border); padding:60px 40px 40px; }}
  .hero-inner {{ max-width:1100px; margin:0 auto; }}
  .hero .ticker {{ font-family:'IBM Plex Mono',monospace; font-size:14px; color:var(--accent); letter-spacing:2px; text-transform:uppercase; margin-bottom:8px; }}
  .hero h1 {{ font-family:'Playfair Display',serif; font-size:42px; font-weight:900; line-height:1.2; margin-bottom:4px; }}
  .hero .company-kr {{ font-size:20px; color:var(--text-dim); font-weight:400; margin-bottom:12px; }}
  .hero .subtitle {{ font-size:17px; color:var(--text-dim); font-weight:300; }}
  .hero .meta-row {{ display:flex; gap:24px; margin-top:20px; font-size:13px; color:var(--text-muted); font-family:'IBM Plex Mono',monospace; flex-wrap:wrap; }}
  .verdict {{ display:inline-flex; align-items:center; gap:8px; padding:6px 16px; border-radius:4px; font-size:13px; font-weight:600; font-family:'IBM Plex Mono',monospace; margin-top:16px; }}
  .verdict.miss {{ background:var(--red-dim); color:var(--red); border:1px solid #ff4d4d44; }}
  .verdict.beat {{ background:var(--accent-dim); color:var(--accent); border:1px solid {accent_color}44; }}
  .verdict.mixed {{ background:var(--yellow); color:#000; border:1px solid #ffc10744; }}

  .container {{ max-width:1100px; margin:0 auto; padding:40px; }}
  .section {{ margin-bottom:56px; }}
  .section-label {{ font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:3px; text-transform:uppercase; color:var(--accent); margin-bottom:8px; }}
  .section h2 {{ font-size:24px; font-weight:700; margin-bottom:24px; padding-bottom:12px; border-bottom:1px solid var(--border); }}
  .section h3 {{ font-size:17px; margin:28px 0 16px; color:var(--text-dim); }}

  .numbers-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; margin-bottom:32px; }}
  .num-card {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:24px; }}
  .num-card .label {{ font-size:12px; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }}
  .num-card .value {{ font-family:'IBM Plex Mono',monospace; font-size:28px; font-weight:700; }}
  .num-card .compare {{ font-size:13px; color:var(--text-dim); margin-top:4px; }}
  .num-card .compare .miss-tag {{ color:var(--red); font-weight:600; }}
  .num-card .compare .beat-tag {{ color:var(--accent); font-weight:600; }}

  table {{ width:100%; border-collapse:collapse; margin-bottom:24px; font-size:14px; }}
  th {{ text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:1px; color:var(--text-muted); padding:10px 16px; border-bottom:1px solid var(--border); background:var(--surface); }}
  td {{ padding:12px 16px; border-bottom:1px solid #1a1a1a; }}
  td.mono {{ font-family:'IBM Plex Mono',monospace; font-size:14px; }}
  tr:hover {{ background:var(--surface); }}
  .positive {{ color:var(--accent); }}
  .negative {{ color:var(--red); }}

  .tier-header {{ display:flex; align-items:center; gap:12px; margin:32px 0 16px; }}
  .tier-badge {{ font-family:'IBM Plex Mono',monospace; font-size:11px; padding:3px 10px; border-radius:4px; font-weight:600; letter-spacing:1px; }}
  .tier-badge.t1 {{ background:{accent_color}22; color:var(--accent); }}
  .tier-badge.t2 {{ background:#4da6ff22; color:var(--blue); }}
  .tier-badge.t3 {{ background:#ffc10722; color:var(--yellow); }}
  .tier-badge.t4 {{ background:#b388ff22; color:var(--purple); }}
  .tier-badge.t5 {{ background:#ff4d4d22; color:var(--red); }}
  .tier-title {{ font-size:16px; font-weight:600; }}
  .tier-desc {{ font-size:12px; color:var(--text-muted); margin-left:auto; font-style:italic; }}

  .quote-block {{ background:var(--surface); border-left:3px solid var(--accent); padding:20px 24px; margin:16px 0; border-radius:0 8px 8px 0; }}
  .quote-block.analyst {{ border-left-color:var(--yellow); }}
  .quote-block .speaker {{ font-size:12px; font-weight:600; color:var(--accent); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }}
  .quote-block.analyst .speaker {{ color:var(--yellow); }}
  .quote-block blockquote {{ font-size:15px; font-style:italic; line-height:1.8; }}
  .quote-block .analysis {{ margin-top:12px; font-size:13px; color:var(--text-dim); line-height:1.6; padding-left:16px; border-left:1px solid var(--border); }}

  .tone-meter {{ display:flex; gap:12px; margin:24px 0; }}
  .tone-item {{ flex:1; background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:16px; text-align:center; }}
  .tone-item .tone-label {{ font-size:11px; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }}
  .tone-bar {{ height:6px; background:var(--surface2); border-radius:3px; overflow:hidden; margin:8px 0; }}
  .tone-bar .fill {{ height:100%; border-radius:3px; }}
  .tone-item .tone-score {{ font-family:'IBM Plex Mono',monospace; font-size:20px; font-weight:700; }}

  .next-q {{ background:linear-gradient(135deg,#4da6ff10,var(--surface)); border:1px solid #4da6ff33; border-radius:8px; padding:24px; }}
  .next-q h3 {{ color:var(--blue); font-size:16px; margin-bottom:16px; }}
  .next-q-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
  .next-q-item .nq-label {{ font-size:12px; color:var(--text-muted); }}
  .next-q-item .nq-value {{ font-family:'IBM Plex Mono',monospace; font-size:22px; font-weight:700; color:var(--blue); }}

  .links-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:12px; }}
  .link-card {{ display:flex; align-items:center; gap:12px; background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:16px; text-decoration:none; color:var(--text); transition:border-color .2s; }}
  .link-card:hover {{ border-color:var(--accent); }}
  .link-card .link-icon {{ font-size:20px; }}
  .link-card .link-text .link-title {{ font-weight:600; font-size:14px; }}
  .link-card .link-text .link-url {{ font-size:11px; color:var(--text-muted); font-family:'IBM Plex Mono',monospace; }}

  .keywords {{ display:flex; flex-wrap:wrap; gap:8px; margin:16px 0; }}
  .kw-tag {{ font-size:11px; padding:4px 10px; border-radius:4px; font-family:'IBM Plex Mono',monospace; letter-spacing:.5px; }}
  .kw-tag.bullish {{ background:var(--accent-dim); color:var(--accent); }}
  .kw-tag.bearish {{ background:var(--red-dim); color:var(--red); }}
  .kw-tag.neutral-tag {{ background:#ffc10722; color:var(--yellow); }}

  .footer {{ border-top:1px solid var(--border); padding:24px 0; text-align:center; font-size:12px; color:var(--text-muted); }}

  .kpi-note {{ font-size:12px; color:var(--text-muted); background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:12px 16px; margin-top:8px; line-height:1.6; }}
  .kpi-note strong {{ color:var(--yellow); }}
"""

# =============================================================================
# 로거 설정
# =============================================================================

def setup_logging() -> logging.Logger:
    """로거 설정."""
    logger = logging.getLogger("earn_reporter")
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러
    today = datetime.now().strftime("%Y%m%d")
    log_file = LOG_DIR / f"earn_reporter_{today}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 포맷터
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# =============================================================================
# 1. 전일 실적 발표 기업 목록 가져오기
# =============================================================================

def get_yesterday_earnings(target_date: str | None = None) -> list[dict[str, Any]]:
    """Yahoo Finance 실적 캘린더에서 전일 발표 기업 목록 가져오기.
    
    Args:
        target_date: YYYY-MM-DD (None이면 어제)
    
    Returns:
        [{"ticker": "AAPL", "company": "Apple Inc.", "eps_estimate": 1.2, ...}, ...]
    """
    if target_date is None:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    logger.info(f"Fetching earnings for {target_date}")
    
    # Nasdaq Earnings Calendar API 사용 (더 안정적)
    url = f"https://api.nasdaq.com/api/calendar/earnings"
    params = {"date": target_date}
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data") is None:
            logger.warning(f"No earnings data for {target_date}")
            return []
        
        rows = data["data"].get("rows", [])
        earnings_list = []
        
        for row in rows:
            ticker = row.get("symbol", "").strip()
            if not ticker:
                continue
            
            earnings_list.append({
                "ticker": ticker,
                "company": row.get("companyName", ""),
                "eps_estimate": _parse_number(row.get("epsEstimate")),
                "eps_actual": _parse_number(row.get("epsActual")),
                "revenue_estimate": _parse_number(row.get("revenueEstimate")),
                "time": row.get("time", ""),
            })
        
        logger.info(f"Found {len(earnings_list)} companies reporting on {target_date}")
        return earnings_list
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch earnings data: {e}")
        return []

def _parse_number(value: str | None) -> float | None:
    """문자열을 숫자로 파싱."""
    if value is None or value == "" or value == "-":
        return None
    try:
        # 콤마 제거
        cleaned = str(value).replace(",", "").replace("$", "")
        return float(cleaned)
    except (ValueError, TypeError):
        return None

# =============================================================================
# 2. 대형주 필터
# =============================================================================

def filter_major(tickers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """대형주만 필터링."""
    filtered = [t for t in tickers if t["ticker"] in MAJOR_TICKERS]
    logger.info(f"Filtered to {len(filtered)} major tickers (from {len(tickers)})")
    return filtered

# =============================================================================
# 3. 실적 데이터 수집
# =============================================================================

def collect_earnings_data(ticker: str) -> dict[str, Any]:
    """yfinance로 실적 숫자 수집.
    
    Returns:
        {
            "ticker": str,
            "company_name": str,
            "company_name_kr": str,
            "report_date": str,
            "fiscal_quarter": str,
            "sector": str,
            "market_cap": str,
            "revenue": float,
            "revenue_estimate": float,
            "revenue_surprise_pct": float,
            "revenue_yoy": float,
            "eps": float,
            "eps_estimate": float,
            "eps_surprise_pct": float,
            "eps_yoy": float,
            "segments": list,
            "guidance": str,
        }
    """
    logger.info(f"Collecting data for {ticker}")
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 기본 정보
        company_name = info.get("longName") or info.get("shortName") or ""
        sector = info.get("sector") or ""
        market_cap = info.get("marketCap")
        
        # 시가총액 포맷팅
        if market_cap:
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.1f}조"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.0f}억"
            elif market_cap >= 1e8:
                market_cap_str = f"${market_cap/1e8:.1f}억"
            else:
                market_cap_str = f"${market_cap/1e6:.0f}백만"
        else:
            market_cap_str = ""
        
        # 실적 데이터 (yfinance에서 직접 가져오기 어려운 경우 많음)
        # earnings_history, quarterly_financials 등 시도
        earnings_history = stock.earnings_history
        quarterly_financials = stock.quarterly_financials
        quarterly_income = stock.quarterly_income_stmt
        
        # 기본 반환값 구조
        data = {
            "ticker": ticker,
            "company_name": company_name,
            "company_name_kr": "",  # GLM이 채움
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "fiscal_quarter": _guess_current_quarter(),
            "sector": sector,
            "market_cap": market_cap_str,
            "revenue": None,
            "revenue_estimate": None,
            "revenue_surprise_pct": None,
            "revenue_yoy": None,
            "eps": None,
            "eps_estimate": None,
            "eps_surprise_pct": None,
            "eps_yoy": None,
            "segments": [],
            "guidance": "",
        }
        
        # earnings_history에서 최신 실적 가져오기 시도
        if earnings_history is not None and not earnings_history.empty:
            latest = earnings_history.iloc[-1]
            data["eps_estimate"] = float(latest.get("EPS Estimate")) if pd.notna(latest.get("EPS Estimate")) else None
            data["eps"] = float(latest.get("Reported EPS")) if pd.notna(latest.get("Reported EPS")) else None
        
        # quarterly_financials에서 매출 가져오기 시도
        if quarterly_financials is not None and not quarterly_financials.empty:
            latest_rev = quarterly_financials.iloc[:, 0]  # 최신 분기
            if "Total Revenue" in latest_rev.index:
                data["revenue"] = float(latest_rev["Total Revenue"]) / 1e9  # 억 달러 단위
        
        # YoY 계산 시도
        if quarterly_financials is not None and len(quarterly_financials.columns) >= 5:
            current_rev = quarterly_financials.iloc[0, 0]
            yoy_rev = quarterly_financials.iloc[0, 4]  # 4분기 전
            if pd.notna(current_rev) and pd.notna(yoy_rev) and yoy_rev != 0:
                data["revenue_yoy"] = round((current_rev / yoy_rev - 1) * 100, 1)
        
        logger.info(f"Collected basic data for {ticker}")
        return data
        
    except Exception as e:
        logger.error(f"Error collecting data for {ticker}: {e}")
        return {
            "ticker": ticker,
            "company_name": "",
            "company_name_kr": "",
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "fiscal_quarter": _guess_current_quarter(),
            "sector": "",
            "market_cap": "",
            "revenue": None,
            "revenue_estimate": None,
            "revenue_surprise_pct": None,
            "revenue_yoy": None,
            "eps": None,
            "eps_estimate": None,
            "eps_surprise_pct": None,
            "eps_yoy": None,
            "segments": [],
            "guidance": "",
        }

def _guess_current_quarter() -> str:
    """현재 분기 추정."""
    month = datetime.now().month
    year = datetime.now().year
    quarter = (month - 1) // 3 + 1
    # 실적은 보통 한 달 정도 늦게 발표되므로 이전 분기일 가능성 높음
    if quarter == 1:
        return f"Q4 {year-1}"
    else:
        return f"Q{quarter-1} {year}"

# pandas import for yfinance
try:
    import pandas as pd
except ImportError:
    pd = None

# =============================================================================
# 4. GLM으로 컨콜 분석 + 데이터 보완
# =============================================================================

def analyze_with_glm(ticker: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """GLM에 실적 데이터를 보내고 컨콜 분석 + 누락 데이터 보완."""
    if call_glm is None:
        logger.warning("GLM client not available, skipping analysis")
        return None
    
    logger.info(f"Analyzing {ticker} with GLM")
    
    prompt = f"""다음 기업의 실적을 분석해줘.

티커: {ticker}
회사명: {data.get('company_name', '')}
섹터: {data.get('sector', '')}
시가총액: {data.get('market_cap', '')}
분기: {data.get('fiscal_quarter', '')}

수집된 실적 데이터:
- 매출: ${data.get('revenue', 'N/A')}억 (추정: ${data.get('revenue_estimate', 'N/A')}억)
- EPS: ${data.get('eps', 'N/A')} (추정: ${data.get('eps_estimate', 'N/A')})
- 매출 YoY: {data.get('revenue_yoy', 'N/A')}%

아래 JSON 형식으로 응답해. JSON 코드블록만 출력해:
```json
{{
    "company_name_kr": "한국어 회사명",
    "verdict": "BEAT" | "MISS" | "MIXED",
    "verdict_detail": "한줄 판정 이유",
    "accent_color": "#hex (기업 브랜드 색상, 다크모드용. 예: #00d632 for green, #ff4d4d for red, #0066cc for blue)",
    
    "revenue_breakdown": [
        {{"name": "세그먼트명", "value": "$XX억", "yoy": "+XX%", "signal": "STRONG|STEADY|HEADWIND"}}
    ],
    
    "kpis": {{
        "tier1": [{{"name": "지표명", "value": "값", "yoy": "+X%", "why": "왜 중요한지"}}],
        "tier2": [],
        "tier3": [],
        "tier4": [],
        "tier5": []
    }},
    
    "guidance": {{
        "items": [{{"label": "Q2 매출 가이던스", "value": "$XX억"}}]
    }},
    
    "tone": {{
        "ceo_confidence": 8.5,
        "cfo_defense": 6.0,
        "analyst_skepticism": 7.0,
        "outlook_clarity": 7.5
    }},
    
    "ceo": {{
        "name": "CEO 이름",
        "style": "한줄 어조 설명",
        "keywords": ["KEY1", "KEY2"],
        "quotes": [
            {{"context": "오프닝", "text": "영어 원문", "analysis": "한글 분석"}}
        ]
    }},
    
    "cfo": {{
        "name": "CFO 이름",
        "quotes": [
            {{"context": "가이던스", "text": "영어 원문", "analysis": "한글 분석"}}
        ]
    }},
    
    "analyst_qa": [
        {{"analyst": "이름, 소속", "question_summary": "질문 요약", "answer_summary": "답변 요약", "analysis": "한글 분석"}}
    ],
    
    "one_liner": {{
        "ceo": "CEO 한줄 요약",
        "cfo": "CFO 한줄 요약",
        "analyst": "애널리스트 한줄 요약",
        "market": "시장 반응 한줄 요약"
    }},
    
    "sources": [
        {{"title": "IR 보도자료", "url": "https://...", "icon": "📄"}},
        {{"title": "컨콜 트랜스크립트", "url": "https://...", "icon": "🎬"}}
    ]
}}
```

참고: 실적 데이터가 웹검색해서 최신 정보를 반영해. 컨콜 트랜스크립트가 있다면 실제 인용구를 포함해."""

    for attempt in range(3):
        try:
            result = call_glm(
                prompt=prompt,
                project="stock",
                feature="earn_reporter",
                timeout=180
            )
            
            # JSON 파싱
            json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = result.strip()
            
            glm_data = json.loads(json_str)
            logger.info(f"GLM analysis completed for {ticker}")
            return glm_data
            
        except json.JSONDecodeError as e:
            logger.warning(f"GLM JSON parse error (attempt {attempt+1}/3): {e}")
            time.sleep(2)
        except Exception as e:
            logger.error(f"GLM call error (attempt {attempt+1}/3): {e}")
            time.sleep(2)
    
    logger.error(f"GLM analysis failed after 3 attempts for {ticker}")
    return None

# =============================================================================
# 5. HTML 생성
# =============================================================================

def generate_html(data: dict[str, Any], glm_result: dict[str, Any] | None) -> str:
    """HOOD 템플릿의 CSS를 재사용하고, 내용만 교체하여 HTML 생성."""
    
    # 기본값 설정
    ticker = data["ticker"]
    company_name = data.get("company_name", ticker)
    company_name_kr = glm_result.get("company_name_kr", "") if glm_result else ""
    fiscal_quarter = data.get("fiscal_quarter", "")
    report_date = data.get("report_date", "")
    sector = data.get("sector", "")
    market_cap = data.get("market_cap", "")
    
    verdict = glm_result.get("verdict", "MIXED") if glm_result else "MIXED"
    verdict_detail = glm_result.get("verdict_detail", "") if glm_result else ""
    accent_color = glm_result.get("accent_color", "#00d632") if glm_result else "#00d632"
    
    # CSS 삽입
    css = CSS_TEMPLATE.format(accent_color=accent_color)
    
    # 실적 숫자
    revenue = data.get("revenue")
    revenue_estimate = data.get("revenue_estimate")
    revenue_str = f"${revenue:.1f}억" if revenue else "N/A"
    
    if revenue and revenue_estimate:
        revenue_surprise = (revenue / revenue_estimate - 1) * 100
        revenue_tag = "BEAT" if revenue_surprise > 0 else "MISS"
        revenue_tag_class = "beat-tag" if revenue_surprise > 0 else "miss-tag"
        revenue_compare = f"컨센서스: ${revenue_estimate:.1f}억 <span class=\"{revenue_tag_class}\">{revenue_tag} {revenue_surprise:+.1f}%</span>"
    else:
        revenue_compare = "컨센서스: N/A"
    
    revenue_yoy = data.get("revenue_yoy")
    revenue_yoy_str = f"전년비: {revenue_yoy:+.0f}%" if revenue_yoy else "전년비: N/A"
    
    eps = data.get("eps")
    eps_estimate = data.get("eps_estimate")
    eps_str = f"${eps:.2f}" if eps else "N/A"
    
    if eps and eps_estimate:
        eps_surprise = (eps / eps_estimate - 1) * 100
        eps_tag = "BEAT" if eps_surprise > 0 else "MISS"
        eps_tag_class = "beat-tag" if eps_surprise > 0 else "miss-tag"
        eps_compare = f"컨센서스: ${eps_estimate:.2f} <span class=\"{eps_tag_class}\">{eps_tag}</span>"
    else:
        eps_compare = "컨센서스: N/A"
    
    # EBITDA (Placeholder)
    ebitda_str = "N/A"
    ebitda_margin = "N/A"
    
    # 매출 구성 (GLM 결과)
    revenue_breakdown = glm_result.get("revenue_breakdown", []) if glm_result else []
    
    # 가이던스 (GLM 결과)
    guidance_items = glm_result.get("guidance", {}).get("items", []) if glm_result else []
    
    # KPI (GLM 결과)
    kpis = glm_result.get("kpis", {}) if glm_result else {}
    
    # Tone (GLM 결과)
    tone = glm_result.get("tone", {}) if glm_result else {}
    
    # CEO/CFO (GLM 결과)
    ceo_data = glm_result.get("ceo", {}) if glm_result else {}
    cfo_data = glm_result.get("cfo", {}) if glm_result else {}
    
    # Analyst Q&A (GLM 결과)
    analyst_qa = glm_result.get("analyst_qa", []) if glm_result else []
    
    # One-liner (GLM 결과)
    one_liner = glm_result.get("one_liner", {}) if glm_result else {}
    
    # Sources (GLM 결과)
    sources = glm_result.get("sources", []) if glm_result else []
    
    # verdict class
    verdict_class = verdict.lower() if verdict in ["BEAT", "MISS"] else "mixed"
    
    # HTML 빌드
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{ticker} | {company_name} {fiscal_quarter} 실적 딥다이브</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
<style>{css}
</style>
</head>
<body>

<!-- ===== HERO ===== -->
<div class="hero">
  <div class="hero-inner">
    <div class="ticker">{ticker}</div>
    <h1>{company_name}</h1>
    <div class="company-kr">{company_name_kr}</div>
    <div class="subtitle">{fiscal_quarter} 실적 딥다이브 &mdash; {report_date} 발표</div>
    <div class="meta-row">
      <span>발표일: {report_date}</span>
      <span>|</span>
      <span>섹터: {sector}</span>
      <span>|</span>
      <span>시가총액: ~{market_cap}</span>
    </div>
    <div class="verdict {verdict_class}">{verdict} &mdash; {verdict_detail}</div>
  </div>
</div>

<div class="container">

<!-- ===== 01: 실적 숫자 ===== -->
<div class="section">
  <div class="section-label">01 &mdash; 실적 숫자</div>
  <h2>컨센서스 vs 실적</h2>

  <div class="numbers-grid">
    <div class="num-card">
      <div class="label">매출</div>
      <div class="value">{revenue_str}</div>
      <div class="compare">{revenue_compare}</div>
      <div class="compare">{revenue_yoy_str}</div>
    </div>
    <div class="num-card">
      <div class="label">희석 EPS</div>
      <div class="value">{eps_str}</div>
      <div class="compare">{eps_compare}</div>
      <div class="compare">전년비: N/A</div>
    </div>
    <div class="num-card">
      <div class="label">조정 EBITDA</div>
      <div class="value">{ebitda_str}</div>
      <div class="compare">마진: {ebitda_margin}</div>
      <div class="compare">전년비: N/A</div>
    </div>
  </div>
"""

    # 매출 구성 테이블
    if revenue_breakdown:
        html += """
  <h3>매출 구성</h3>
  <table>
    <thead><tr><th>수익원</th><th>분기 실적</th><th>전년비</th><th>시그널</th></tr></thead>
    <tbody>
"""
        for segment in revenue_breakdown:
            signal = segment.get("signal", "STEADY")
            signal_class = "bullish" if signal == "STRONG" else "bearish" if signal == "HEADWIND" else "neutral-tag"
            html += f"""      <tr><td>{segment.get('name', '')}</td><td class="mono">{segment.get('value', '')}</td><td class="mono">{segment.get('yoy', '')}</td><td><span class="kw-tag {signal_class}">{signal}</span></td></tr>
"""
        html += "    </tbody>\n  </table>\n"

    # 가이던스
    if guidance_items:
        html += """
  <div class="next-q">
    <h3>다음 분기 가이던스 / 컨센서스</h3>
    <div class="next-q-grid">
"""
        for item in guidance_items[:3]:
            html += f"""      <div class="next-q-item"><div class="nq-label">{item.get('label', '')}</div><div class="nq-value">{item.get('value', '')}</div></div>
"""
        html += "    </div>\n  </div>\n"

    html += "</div>\n"

    # KPI 섹션
    html += """
<!-- ===== 02: 핵심 KPI ===== -->
<div class="section">
  <div class="section-label">02 &mdash; 핵심 KPI 대시보드</div>
  <h2>이 회사를 읽는 숫자들</h2>
"""
    
    tier_names = {
        "tier1": ("TIER 1", "t1", "North Star &mdash; 경영진이 직접 선언한 최우선 지표"),
        "tier2": ("TIER 2", "t2", "사용자 건강 &mdash; 이게 무너지면 끝"),
        "tier3": ("TIER 3", "t3", "자산 규모 &mdash; 밸류에이션의 근거"),
        "tier4": ("TIER 4", "t4", "거래량 &mdash; 수수료 매출의 선행지표"),
        "tier5": ("TIER 5", "t5", "신규 사업 &mdash; 미래 베팅"),
    }
    
    for tier_key, (tier_label, tier_class, tier_desc) in tier_names.items():
        tier_kpis = kpis.get(tier_key, [])
        if tier_kpis:
            html += f"""  <!-- {tier_label} -->
  <div class="tier-header">
    <span class="tier-badge {tier_class}">{tier_label}</span>
    <span class="tier-title">{tier_desc}</span>
  </div>
  <table>
    <thead><tr><th>지표</th><th>분기 실적</th><th>전년비</th><th>왜 중요한가</th></tr></thead>
    <tbody>
"""
            for kpi in tier_kpis:
                html += f"""      <tr><td><strong>{kpi.get('name', '')}</strong></td><td class="mono">{kpi.get('value', '')}</td><td class="mono">{kpi.get('yoy', '')}</td><td>{kpi.get('why', '')}</td></tr>
"""
            html += "    </tbody>\n  </table>\n"
    
    html += "</div>\n"

    # 컨콜 분석 섹션
    html += """
<!-- ===== 03: 컨퍼런스 콜 ===== -->
<div class="section">
  <div class="section-label">03 &mdash; 컨퍼런스 콜 분석</div>
  <h2>경영진은 뭐라고 했나</h2>
"""
    
    # Tone meter
    if tone:
        html += """
  <div class="tone-meter>
"""
        tone_labels = {
            "ceo_confidence": "CEO 자신감",
            "cfo_defense": "CFO 방어도",
            "analyst_skepticism": "애널리스트 회의감",
            "outlook_clarity": "전망 명확성",
        }
        tone_colors = {
            "ceo_confidence": accent_color,
            "cfo_defense": "#ffc107",
            "analyst_skepticism": "#ff4d4d",
            "outlook_clarity": "#4da6ff",
        }
        
        for key, label in tone_labels.items():
            score = tone.get(key, 5.0)
            color = tone_colors.get(key, accent_color)
            html += f"""    <div class="tone-item">
      <div class="tone-label">{label}</div>
      <div class="tone-bar"><div class="fill" style="width:{score*10}%;background:{color};"></div></div>
      <div class="tone-score">{score:.1f}<span style="font-size:12px;color:var(--text-muted)">/10</span></div>
    </div>
"""
        html += "  </div>\n"
    
    # CEO quotes
    if ceo_data:
        html += f"""
  <h3>{ceo_data.get('name', 'CEO')}</h3>
  <p style="color:var(--text-dim);margin-bottom:20px;">
    <strong>어조:</strong> {ceo_data.get('style', '')}
  </p>
"""
        keywords = ceo_data.get("keywords", [])
        if keywords:
            html += '  <div class="keywords">\n'
            for kw in keywords:
                html += f'    <span class="kw-tag bullish">{kw}</span>\n'
            html += "  </div>\n"
        
        for quote in ceo_data.get("quotes", []):
            html += f"""
  <div class="quote-block">
    <div class="speaker">{ceo_data.get('name', 'CEO')} &mdash; {quote.get('context', '')}</div>
    <blockquote>"{quote.get('text', '')}"</blockquote>
    <div class="analysis">{quote.get('analysis', '')}</div>
  </div>
"""
    
    # CFO quotes
    if cfo_data:
        html += f"""
  <h3>{cfo_data.get('name', 'CFO')}</h3>
"""
        for quote in cfo_data.get("quotes", []):
            html += f"""
  <div class="quote-block">
    <div class="speaker">{cfo_data.get('name', 'CFO')} &mdash; {quote.get('context', '')}</div>
    <blockquote>"{quote.get('text', '')}"</blockquote>
    <div class="analysis">{quote.get('analysis', '')}</div>
  </div>
"""
    
    # Analyst Q&A
    if analyst_qa:
        html += """
  <h3>애널리스트 Q&amp;A</h3>
  <p style="color:var(--text-dim);margin-bottom:20px;">
    <strong>전체 분위기:</strong> 존중하되 회의적. "증명해봐" 모드 가동.
  </p>
"""
        for qa in analyst_qa:
            html += f"""
  <div class="quote-block analyst">
    <div class="speaker">{qa.get('analyst', '')}</div>
    <blockquote>"{qa.get('question_summary', '')}"</blockquote>
    <div class="analysis"><strong>답변:</strong> {qa.get('answer_summary', '')}<br><br>{qa.get('analysis', '')}</div>
  </div>
"""
    
    html += "</div>\n"

    # 한줄 요약
    html += """
<!-- ===== 04: 한줄 요약 ===== -->
<div class="section">
  <div class="section-label">04 &mdash; 한줄 읽기</div>
  <h2>요약</h2>
  <table>
    <tbody>
"""
    if one_liner:
        if ceo_data:
            html += f"      <tr><td style='width:140px;font-weight:600;color:var(--accent);'>{ceo_data.get('name', 'CEO')}</td><td>\"{one_liner.get('ceo', '')}\"</td></tr>\n"
        if cfo_data:
            html += f"      <tr><td style='font-weight:600;color:var(--accent);'>{cfo_data.get('name', 'CFO')}</td><td>\"{one_liner.get('cfo', '')}\"</td></tr>\n"
        html += f"      <tr><td style='font-weight:600;color:var(--yellow);'>애널리스트</td><td>\"{one_liner.get('analyst', '')}\"</td></tr>\n"
        html += f"      <tr><td style='font-weight:600;color:var(--red);'>시장 반응</td><td>{one_liner.get('market', '')}</td></tr>\n"
    
    html += "    </tbody>\n  </table>\n</div>\n"

    # 소스 링크
    html += """
<!-- ===== 05: 소스 ===== -->
<div class="section">
  <div class="section-label">05 &mdash; 자료 링크</div>
  <h2>원본 자료</h2>
  <div class="links-grid>
"""
    for source in sources:
        html += f"""    <a class="link-card" href="{source.get('url', '')}" target="_blank">
      <div class="link-icon">{source.get('icon', '📄')}</div>
      <div class="link-text"><div class="link-title">{source.get('title', '')}</div><div class="link-url">{source.get('url', '')}</div></div>
    </a>
"""
    
    html += """
  </div>
</div>

<div class="footer">
  Generated by Earnings Call Analyzer &mdash; """ + datetime.now().strftime("%Y-%m-%d") + """ &mdash; MACROHARD / Be:Analogue
</div>

</div>
</body>
</html>
"""
    
    return html

# =============================================================================
# 6. 저장 + 업로드
# =============================================================================

def save_and_upload(ticker: str, html: str, quarter: str = "Q1") -> Path:
    """HTML 파일 저장 + rclone 업로드."""
    
    # 파일명: TICKER_2026Q1.html
    year = datetime.now().year
    filename = f"{ticker}_{year}{quarter}.html"
    filepath = DOCS_DIR / filename
    
    # 저장
    filepath.write_text(html, encoding="utf-8")
    logger.info(f"Saved HTML to {filepath}")
    
    # rclone 업로드
    try:
        subprocess.run(
            ["rclone", "copy", str(filepath), "gdrive:Earnings Reports/"],
            check=True,
            capture_output=True,
            timeout=60
        )
        logger.info(f"Uploaded {filename} to Google Drive")
    except subprocess.CalledProcessError as e:
        logger.error(f"rclone upload failed: {e}")
    except subprocess.TimeoutExpired:
        logger.error("rclone upload timed out")
    except FileNotFoundError:
        logger.warning("rclone not found, skipping upload")
    
    return filepath

# =============================================================================
# 7. 일일 인덱스 갱신
# =============================================================================

def update_daily_index(reports: list[dict[str, Any]]) -> None:
    """일일 인덱스 파일 갱신."""
    if not reports:
        return
    
    index_path = DOCS_DIR / "daily_index.md"
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 기존 내용 읽기
    existing_content = ""
    if index_path.exists():
        existing_content = index_path.read_text(encoding="utf-8")
    
    # 오늘 날짜 섹션 확인
    today_section = f"## {today}"
    if today_section in existing_content:
        # 이미 있으면 덮어쓰기
        lines = existing_content.split("\n")
        new_lines = []
        skip_until_next_section = False
        
        for line in lines:
            if line.startswith(today_section):
                new_lines.append(line)
                new_lines.append("| 티커 | 회사명 | Verdict | 파일 |")
                new_lines.append("|------|--------|---------|------|")
                for report in reports:
                    new_lines.append(f"| {report['ticker']} | {report['company_name_kr']} | {report['verdict']} | {report['filename']} |")
                skip_until_next_section = True
            elif skip_until_next_section:
                if line.startswith("## "):
                    skip_until_next_section = False
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        index_content = "\n".join(new_lines)
    else:
        # 새로 추가
        new_section = f"\n{today_section}\n| 티커 | 회사명 | Verdict | 파일 |\n|------|--------|---------|------|\n"
        for report in reports:
            new_section += f"| {report['ticker']} | {report['company_name_kr']} | {report['verdict']} | {report['filename']} |\n"
        
        index_content = existing_content + new_section
    
    index_path.write_text(index_content, encoding="utf-8")
    logger.info(f"Updated daily index at {index_path}")

# =============================================================================
# 8. 메인
# =============================================================================

def main() -> None:
    """메인 실행."""
    parser = argparse.ArgumentParser(description="실적 리포트 자동 생성")
    parser.add_argument("--date", type=str, help="대상 날짜 (YYYY-MM-DD), 기본값: 어제")
    parser.add_argument("--ticker", type=str, help="특정 티커만 처리")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Earnings Reporter Started")
    logger.info("=" * 60)
    
    # 1. 전일 실적 발표 기업 목록
    if args.ticker:
        # 특정 티커만 처리
        tickers = [{"ticker": args.ticker, "company": "", "eps_estimate": None}]
    else:
        tickers = get_yesterday_earnings(args.date)
    
    if not tickers:
        logger.info("No earnings to process")
        return
    
    # 2. 대형주 필터
    major_tickers = filter_major(tickers)
    
    if not major_tickers:
        logger.info("No major tickers to process")
        return
    
    # 3~5. 각 기업별 처리
    generated_reports = []
    
    for ticker_data in major_tickers:
        ticker = ticker_data["ticker"]
        logger.info(f"\n{'=' * 40}")
        logger.info(f"Processing {ticker}")
        logger.info(f"{'=' * 40}")
        
        try:
            # 실적 데이터 수집
            data = collect_earnings_data(ticker)
            
            # GLM 분석
            glm_result = analyze_with_glm(ticker, data)
            
            # HTML 생성
            html = generate_html(data, glm_result)
            
            # 분기 추출
            quarter = data.get("fiscal_quarter", "Q1").split()[0]
            
            # 저장 + 업로드
            filepath = save_and_upload(ticker, html, quarter)
            
            # 리포트 기록
            generated_reports.append({
                "ticker": ticker,
                "company_name_kr": glm_result.get("company_name_kr", "") if glm_result else "",
                "verdict": glm_result.get("verdict", "N/A") if glm_result else "N/A",
                "filename": filepath.name,
            })
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to process {ticker}: {e}", exc_info=True)
            continue
    
    # 6. 일일 인덱스 갱신
    if generated_reports:
        update_daily_index(generated_reports)
    
    logger.info("=" * 60)
    logger.info(f"Completed. Generated {len(generated_reports)} reports.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
