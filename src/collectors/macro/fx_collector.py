"""FX and destination asset collector using yfinance.

Covers:
- Flow signals: DXY, USD/JPY, USD/KRW, EUR/USD, USD/CNY
- Destination assets: S&P 500, KOSPI, EM ETF, Gold, Oil, Copper, Bitcoin, TLT

Usage::

    collector = FXCollector()
    data = collector.collect()
    print(data["currencies"]["DXY"]["last"])
    print(data["destinations"]["Gold"]["pct_1w"])
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import certifi
import pandas as pd
import yfinance as yf

from src.core.logger import get_logger

logger = get_logger(__name__)

# Fix non-ASCII path for curl_cffi used internally by yfinance
_cert_src = Path(certifi.where())
try:
    str(_cert_src).encode("ascii")
except (UnicodeEncodeError, UnicodeDecodeError):
    _cert_dst = Path(os.environ.get("TEMP", "/tmp")) / "yf_certs" / "cacert.pem"
    if not _cert_dst.exists() or _cert_dst.stat().st_size != _cert_src.stat().st_size:
        _cert_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_cert_src, _cert_dst)
    os.environ.setdefault("CURL_CA_BUNDLE", str(_cert_dst))


# ── Ticker definitions ──────────────────────────────────────────────────────

CURRENCY_TICKERS: dict[str, str] = {
    "DXY":     "DX-Y.NYB",
    "USD/JPY": "JPY=X",
    "USD/KRW": "KRW=X",
    "EUR/USD": "EURUSD=X",
    "USD/CNY": "CNY=X",
}

DESTINATION_TICKERS: dict[str, str] = {
    "S&P 500":   "^GSPC",
    "KOSPI":     "^KS11",
    "EM ETF":    "EEM",
    "금(Gold)":  "GC=F",
    "WTI 원유":  "CL=F",
    "구리":      "HG=F",
    "비트코인":  "BTC-USD",
    "미채권TLT": "TLT",
}

# 11 GICS sectors — SPDR ETFs (ticker as internal key, displayed with Korean name)
SECTOR_TICKERS: dict[str, str] = {
    "XLK":  "XLK",   # Technology
    "XLC":  "XLC",   # Communication Services
    "XLF":  "XLF",   # Financials
    "XLY":  "XLY",   # Consumer Discretionary
    "XLV":  "XLV",   # Health Care
    "XLP":  "XLP",   # Consumer Staples
    "XLE":  "XLE",   # Energy
    "XLI":  "XLI",   # Industrials
    "XLB":  "XLB",   # Materials
    "XLU":  "XLU",   # Utilities
    "XLRE": "XLRE",  # Real Estate
}

SECTOR_NAMES: dict[str, str] = {
    "XLK":  "기술",
    "XLC":  "커뮤니케이션",
    "XLF":  "금융",
    "XLY":  "임의소비재",
    "XLV":  "헬스케어",
    "XLP":  "필수소비재",
    "XLE":  "에너지",
    "XLI":  "산업재",
    "XLB":  "소재",
    "XLU":  "유틸리티",
    "XLRE": "리츠",
}

SECTOR_EMOJIS: dict[str, str] = {
    "XLK":  "💻",  # 기술
    "XLC":  "📡",  # 커뮤니케이션
    "XLF":  "💰",  # 금융
    "XLY":  "🛍️",  # 임의소비재
    "XLV":  "💊",  # 헬스케어
    "XLP":  "🛒",  # 필수소비재
    "XLE":  "⚡",  # 에너지
    "XLI":  "🏭",  # 산업재
    "XLB":  "⛏️",  # 소재
    "XLU":  "💡",  # 유틸리티
    "XLRE": "🏢",  # 리츠
}

_PERIOD = "1mo"  # fetch 1 month to compute 1d / 1w / 1m changes


def _pct(new: float, old: float) -> float | None:
    """Percentage change from old to new."""
    if old == 0:
        return None
    return round((new / old - 1) * 100, 2)


def _build_sector_entry(ticker_sym: str, label: str) -> dict[str, Any]:
    """Fetch 1-year OHLCV and compute multi-period returns for sector ETFs.

    Fetches a full year to compute 1d / 1w / 1m / 3m / 1y returns,
    enabling the multi-period sector rotation table.

    Args:
        ticker_sym: yfinance ticker string.
        label: Human-readable label for logging.

    Returns:
        Dict with last, pct_1d, pct_1w, pct_1m, pct_3m, pct_1y, date, or error key.
    """
    try:
        df = yf.Ticker(ticker_sym).history(period="1y")
        if df.empty or "Close" not in df.columns:
            return {"error": "no_data"}
        closes = df["Close"].dropna()
        n = len(closes)
        if n < 2:
            return {"error": "insufficient_data"}

        last = float(closes.iloc[-1])
        date = str(closes.index[-1].date())

        return {
            "last":   round(last, 4),
            "pct_1d": _pct(last, float(closes.iloc[-2]))  if n >= 2  else None,
            "pct_1w": _pct(last, float(closes.iloc[-6]))  if n >= 6  else None,
            "pct_1m": _pct(last, float(closes.iloc[-22])) if n >= 22 else None,
            "pct_3m": _pct(last, float(closes.iloc[-65])) if n >= 65 else None,
            "pct_1y": _pct(last, float(closes.iloc[0])),
            "date":   date,
        }
    except Exception as e:
        logger.warning("sector_fetch_failed", ticker=ticker_sym, label=label, error=str(e))
        return {"error": str(e)}


def _build_entry(ticker_sym: str, label: str) -> dict[str, Any]:
    """Fetch OHLCV and compute price change metrics for one ticker.

    Args:
        ticker_sym: yfinance ticker string.
        label: Human-readable label for logging.

    Returns:
        Dict with last, pct_1d, pct_1w, pct_1m, date, or error key.
    """
    try:
        df = yf.Ticker(ticker_sym).history(period=_PERIOD)
        if df.empty or "Close" not in df.columns:
            return {"error": "no_data"}
        closes = df["Close"].dropna()
        if closes.empty:
            return {"error": "empty_closes"}

        last = float(closes.iloc[-1])
        date = str(closes.index[-1].date())

        pct_1d = _pct(last, float(closes.iloc[-2])) if len(closes) >= 2 else None
        pct_1w = _pct(last, float(closes.iloc[-6])) if len(closes) >= 6 else None
        pct_1m = _pct(last, float(closes.iloc[0]))  if len(closes) >= 2 else None

        return {
            "last":   round(last, 4),
            "pct_1d": pct_1d,
            "pct_1w": pct_1w,
            "pct_1m": pct_1m,
            "date":   date,
        }
    except Exception as e:
        logger.warning("fx_fetch_failed", ticker=ticker_sym, label=label, error=str(e))
        return {"error": str(e)}


class FXCollector:
    """Collects FX flow signals and destination asset prices via yfinance."""

    def collect_series(self, period: str = "1y") -> dict[str, pd.Series]:
        """Return Close price series for currencies, destinations, and sectors.

        Args:
            period: yfinance period string (e.g. '1y', '2y', '6mo').

        Returns:
            Dict mapping label → pandas Series of Close prices indexed by date.
            Sector keys use the ticker symbol (e.g. "XLK") for chart lookups.
        """
        result: dict[str, pd.Series] = {}
        all_tickers = {**CURRENCY_TICKERS, **DESTINATION_TICKERS, **SECTOR_TICKERS}
        for label, sym in all_tickers.items():
            try:
                df = yf.Ticker(sym).history(period=period)
                if not df.empty and "Close" in df.columns:
                    s = df["Close"].dropna()
                    s.index = s.index.tz_localize(None)  # strip timezone for plotting
                    result[label] = s
            except Exception as e:
                logger.warning("fx_series_failed", ticker=sym, label=label, error=str(e))
        return result

    def collect(self) -> dict[str, Any]:
        """Fetch all currencies, destination assets, and sector ETFs.

        Returns:
            Dict with keys:
                - ``currencies``:   {label: {last, pct_1d, pct_1w, pct_1m, date}}
                - ``destinations``: same structure
                - ``sectors``:      {"XLK (기술)": {last, pct_1d, pct_1w, pct_1m, date}, ...}
                - ``fetched_at``:   ISO timestamp
        """
        logger.info("fx_collect_start")

        currencies: dict[str, Any] = {}
        for label, sym in CURRENCY_TICKERS.items():
            currencies[label] = _build_entry(sym, label)

        destinations: dict[str, Any] = {}
        for label, sym in DESTINATION_TICKERS.items():
            destinations[label] = _build_entry(sym, label)

        sectors: dict[str, Any] = {}
        for ticker, sym in SECTOR_TICKERS.items():
            emoji = SECTOR_EMOJIS.get(ticker, "")
            display = f"{emoji} {ticker} {SECTOR_NAMES[ticker]}"
            sectors[display] = _build_sector_entry(sym, display)

        result = {
            "currencies":    currencies,
            "destinations":  destinations,
            "sectors":       sectors,
            "fetched_at":    datetime.now().isoformat(),
        }

        ok_cur  = sum(1 for v in currencies.values()   if "error" not in v)
        ok_dest = sum(1 for v in destinations.values() if "error" not in v)
        ok_sect = sum(1 for v in sectors.values()      if "error" not in v)
        logger.info("fx_collect_done",
                    currencies_ok=ok_cur, destinations_ok=ok_dest, sectors_ok=ok_sect)
        return result
