#!/usr/bin/env python3
"""NASDAQ 100 + S&P 500 VWMA100 터치 스크리너.

매일 장 마감 후 실행 → 저가가 VWMA100에 닿은 종목을 텔레그램으로 전송.

Usage:
    python3 scripts/screener_vwma100.py               # NASDAQ 100 + S&P 500
    python3 scripts/screener_vwma100.py --universe ndx # NASDAQ 100만
    python3 scripts/screener_vwma100.py --universe sp5 # S&P 500만
    python3 scripts/screener_vwma100.py --dry-run      # 텔레그램 전송 없이 출력만
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

TOUCH_PCT  = 0.015   # 저가가 VWMA100 ±1.5% 이내면 터치
SLOPE_N    = 20      # 우상향 판단 봉 수
HISTORY_N  = 20      # 돌파 이력 탐색 봉 수
PERIOD     = "1y"    # 데이터 기간 (VWMA100 충분히 계산)


# ── NASDAQ 100 종목 리스트 (2025 기준)
NASDAQ_100 = [
    "AAPL","MSFT","NVDA","AMZN","META","GOOGL","GOOG","TSLA","AVGO","COST",
    "NFLX","ASML","AMD","AZN","CSCO","ADBE","TMUS","TXN","AMGN","QCOM",
    "INTU","ISRG","BKNG","AMAT","ARM","MU","LRCX","PANW","ADI","MELI",
    "KLAC","REGN","SNPS","CDNS","CRWD","MRNA","MAR","ORLY","ABNB","FTNT",
    "CTAS","ROP","MCHP","NXPI","KDP","CEG","DDOG","MNST","TEAM","WDAY",
    "PAYX","AEP","FAST","ODFL","ROST","PCAR","BIIB","IDXX","FANG","CHTR",
    "ON","EXC","VRSK","ZS","CPRT","MRVL","TTWO","XEL","GEHC","ANSS",
    "DXCM","KHC","EA","CTSH","GFS","BKR","DLTR","WBD","SGEN","ILMN",
    "PDD","SBUX","PYPL","HON","MDLZ","GILD","CSX","NDAQ","ADP","ADSK",
    "CMCSA","LULU","LCID","COIN","RBLX","TTD","ZM","DOCU","MTCH","OKTA",
]


def get_sp500_tickers() -> list[str]:
    """Wikipedia에서 S&P 500 종목 리스트 가져오기."""
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        tickers = tables[0]["Symbol"].tolist()
        # BRK.B → BRK-B 등 Yahoo Finance 포맷으로 변환
        return [t.replace(".", "-") for t in tickers]
    except Exception as e:
        print(f"[WARN] S&P 500 리스트 로드 실패: {e}")
        return []


def vwma(close: pd.Series, volume: pd.Series, period: int) -> pd.Series:
    pv   = (close * volume).rolling(period, min_periods=period).sum()
    vsum = volume.rolling(period, min_periods=period).sum()
    return pv / vsum.replace(0, np.nan)


def scan_ticker(ticker: str, hist: pd.DataFrame) -> dict | None:
    """단일 종목 VWMA100 터치 여부 판단."""
    try:
        df = hist[["Open","High","Low","Close","Volume"]].copy()
        df.columns = ["open","high","low","close","volume"]
        df["vwma100"] = vwma(df["close"], df["volume"], 100)
        df = df.dropna(subset=["vwma100"])

        if len(df) < HISTORY_N + SLOPE_N + 1:
            return None

        last  = df.iloc[-1]
        vw    = last["vwma100"]
        close = last["close"]
        low   = last["low"]

        # 터치 조건: 저가가 VWMA100 ±TOUCH_PCT 이내
        touch = low <= vw * (1 + TOUCH_PCT)
        # 종가는 VWMA100 위 (아직 이탈 아님)
        above = close >= vw

        if not (touch and above):
            return None

        # 돌파 이력: 직전 HISTORY_N봉 중 한번이라도 VWMA100 위에 있었음
        past = df.iloc[-(HISTORY_N+1):-1]
        had_breakout = (past["close"] > past["vwma100"]).any()
        if not had_breakout:
            return None

        # VWMA100 기울기
        vw_past   = df["vwma100"].iloc[-(SLOPE_N+1)]
        slope_up  = bool(vw > vw_past) if pd.notna(vw_past) else False

        # 저가 기준 VWMA100 괴리율
        low_vs_vwma = (low / vw - 1) * 100

        return {
            "ticker":      ticker,
            "close":       round(close, 2),
            "low":         round(low, 2),
            "vwma100":     round(vw, 2),
            "low_vs_vwma": round(low_vs_vwma, 2),
            "close_vs_vwma": round((close / vw - 1) * 100, 2),
            "slope_up":    slope_up,
        }
    except Exception:
        return None


def send_telegram(text: str) -> bool:
    token   = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print("[WARN] 텔레그램 환경변수 없음")
        return False
    url  = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": "HTML",
    }, timeout=10)
    return resp.status_code == 200


def format_message(hits: list[dict], label: str) -> str:
    today = date.today().strftime("%Y-%m-%d")

    if not hits:
        return f"🔍 <b>VWMA100 터치</b> — {label}\n{today}\n\n해당 종목 없음"

    up   = [h for h in hits if h["slope_up"]]
    down = [h for h in hits if not h["slope_up"]]

    lines = [f"🔍 <b>VWMA100 터치</b> — {label}  ({today})", ""]

    if up:
        lines.append("📈 <b>우상향 구간</b>")
        for h in sorted(up, key=lambda x: x["low_vs_vwma"]):
            lines.append(
                f"  • <b>{h['ticker']}</b>  ${h['close']}  "
                f"VWMA↑${h['vwma100']}  "
                f"저가 {h['low_vs_vwma']:+.1f}%"
            )
        lines.append("")

    if down:
        lines.append("⚠️ <b>우하향 구간</b> (판단 필요)")
        for h in sorted(down, key=lambda x: x["low_vs_vwma"]):
            lines.append(
                f"  • <b>{h['ticker']}</b>  ${h['close']}  "
                f"VWMA↓${h['vwma100']}  "
                f"저가 {h['low_vs_vwma']:+.1f}%"
            )

    return "\n".join(lines)


def scan_universe(tickers: list[str], label: str) -> list[dict]:
    """유니버스 전체 스캔 후 히트 리스트 반환."""
    print(f"{label} {len(tickers)}종목 다운로드 중...")
    raw = yf.download(
        tickers,
        period=PERIOD,
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    hits: list[dict] = []
    for ticker in tickers:
        try:
            if ticker in raw.columns.get_level_values(0):
                df = raw[ticker].dropna(how="all")
            else:
                continue
            result = scan_ticker(ticker, df)
            if result:
                result["universe"] = label
                hits.append(result)
        except Exception:
            continue
    return hits


def print_hits(hits: list[dict], label: str) -> None:
    print(f"\n[{label}] 신호: {len(hits)}개")
    up   = [h for h in hits if h["slope_up"]]
    down = [h for h in hits if not h["slope_up"]]
    if up:
        print("  📈 우상향")
        for h in sorted(up, key=lambda x: x["low_vs_vwma"]):
            print(f"    {h['ticker']:<6} ${h['close']:<9} VWMA↑${h['vwma100']:<9} 저가 {h['low_vs_vwma']:+.1f}%")
    if down:
        print("  ⚠️  우하향")
        for h in sorted(down, key=lambda x: x["low_vs_vwma"]):
            print(f"    {h['ticker']:<6} ${h['close']:<9} VWMA↓${h['vwma100']:<9} 저가 {h['low_vs_vwma']:+.1f}%")


def run(dry_run: bool = False, universe: str = "all") -> None:
    universes: list[tuple[list[str], str]] = []

    if universe in ("all", "ndx"):
        universes.append((NASDAQ_100, "NASDAQ 100"))
    if universe in ("all", "sp5"):
        sp500 = get_sp500_tickers()
        if sp500:
            # NDX 중복 제거
            ndx_set = set(NASDAQ_100)
            sp500_only = [t for t in sp500 if t not in ndx_set]
            universes.append((sp500_only, "S&P 500"))

    for tickers, label in universes:
        hits = scan_universe(tickers, label)
        print_hits(hits, label)
        msg  = format_message(hits, label)

        if dry_run:
            print(f"\n--- {label} 텔레그램 미리보기 ---")
            print(msg.replace("<b>","**").replace("</b>","**"))
        else:
            ok = send_telegram(msg)
            print(f"  텔레그램: {'✅' if ok else '❌'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--universe", choices=["all","ndx","sp5"], default="all")
    args = parser.parse_args()
    run(dry_run=args.dry_run, universe=args.universe)
