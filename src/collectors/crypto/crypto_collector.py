"""BTC/ETH price and DeFi ecosystem metrics collector.

Collects:
- BTC and ETH prices via yfinance (1d/1w/1m/3m/1y returns)
- ETH DeFi TVL, L2 TVL, total DeFi TVL via DeFiLlama API (free, no auth)
- BTC market dominance via CoinGecko /global (free, no auth)
- Crypto Fear & Greed Index via alternative.me /fng/ (free, no auth)
- ETH/BTC ratio calculated from existing price data

Usage::

    collector = CryptoCollector()
    data = collector.collect()
    print(data["btc"]["price"])           # current BTC price
    print(data["eth_tvl_b"])              # ETH DeFi TVL in $B
    print(data["btc_dominance"])          # BTC dominance % (e.g. 54.3)
    print(data["eth_btc_ratio"])          # ETH/BTC ratio (e.g. 0.03241)
    print(data["fear_greed"]["value"])    # Fear & Greed 0–100

    series = collector.collect_series(period="1y")
    print(series["BTC-USD"])              # pd.Series of BTC close prices
    print(series["ETH-TVL"])              # pd.Series of ETH DeFi TVL ($B)
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import certifi
import pandas as pd
import requests
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


# ── Ticker & API definitions ─────────────────────────────────────────────────

CRYPTO_TICKERS: dict[str, str] = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
}

# 크립토 생태계 기업 (1-23)
ECOSYSTEM_TICKERS: dict[str, str] = {
    "COIN": "COIN",     # Coinbase — 미국 최대 거래소
    "HOOD": "HOOD",     # Robinhood — 리테일 크립토 진입점
    "MSTR": "MSTR",     # MicroStrategy — BTC 트레저리 프록시
    "SQ":   "SQ",       # Block (Square) — BTC 결제 + Cash App
    "BLK":  "BLK",      # BlackRock — IBIT ETF 운용
    "BMNR": "BMNR",     # Bit Brother — 블록체인 인프라
}

# DeFiLlama chain names as they appear in the API response
_L2_CHAINS = ["Base", "Arbitrum", "Optimism", "zkSync Era"]

_DEFI_LLAMA_CHAINS_URL = "https://api.llama.fi/v2/chains"
_DEFI_LLAMA_HISTORICAL_URL = "https://api.llama.fi/v2/historicalChainTvl/{chain}"
_COINGECKO_GLOBAL_URL = "https://api.coingecko.com/api/v3/global"
_FEAR_GREED_URL = "https://api.alternative.me/fng/"
_REQUEST_TIMEOUT = 10


# ── Helpers ──────────────────────────────────────────────────────────────────

def _pct(new: float, old: float) -> float | None:
    """Percentage change from old to new, rounded to 2 dp."""
    if old == 0:
        return None
    return round((new / old - 1) * 100, 2)


def _build_price_entry(symbol: str, ticker_sym: str) -> dict[str, Any]:
    """Fetch 1-year OHLCV from yfinance and compute multi-period returns.

    Args:
        symbol: Short label for logging (e.g. "BTC").
        ticker_sym: yfinance ticker string (e.g. "BTC-USD").

    Returns:
        Dict with price, pct_1d/1w/1m/3m/1y, date, or error key.
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
            "price":   round(last, 2),
            "pct_1d":  _pct(last, float(closes.iloc[-2]))  if n >= 2  else None,
            "pct_1w":  _pct(last, float(closes.iloc[-6]))  if n >= 6  else None,
            "pct_1m":  _pct(last, float(closes.iloc[-22])) if n >= 22 else None,
            "pct_3m":  _pct(last, float(closes.iloc[-65])) if n >= 65 else None,
            "pct_1y":  _pct(last, float(closes.iloc[0])),
            "date":    date,
        }
    except Exception as e:
        logger.warning("crypto_price_fetch_failed", symbol=symbol, error=str(e))
        return {"error": str(e)}


def _fetch_defi_tvl_snapshot() -> dict[str, float | None]:
    """Fetch current TVL from DeFiLlama /v2/chains endpoint.

    DeFiLlama returns tvl in raw USD — divides by 1e9 for $B.

    Returns:
        Dict with eth_tvl_b, l2_tvl_b, total_tvl_b (all in $B), or None on failure.
    """
    try:
        resp = requests.get(_DEFI_LLAMA_CHAINS_URL, timeout=_REQUEST_TIMEOUT)
        resp.raise_for_status()
        chains = resp.json()  # list of {name, tvl, ...}

        chain_map: dict[str, float] = {}
        total = 0.0
        for c in chains:
            name = c.get("name", "")
            tvl = float(c.get("tvl") or 0)
            chain_map[name] = tvl
            total += tvl

        eth_tvl_b  = round(chain_map.get("Ethereum", 0) / 1e9, 1)
        l2_tvl_b   = round(sum(chain_map.get(n, 0) for n in _L2_CHAINS) / 1e9, 1)
        total_tvl_b = round(total / 1e9, 1)

        return {
            "eth_tvl_b":   eth_tvl_b,
            "l2_tvl_b":    l2_tvl_b,
            "total_tvl_b": total_tvl_b,
        }
    except Exception as e:
        logger.warning("defi_tvl_snapshot_failed", error=str(e))
        return {"eth_tvl_b": None, "l2_tvl_b": None, "total_tvl_b": None}


def _fetch_eth_tvl_series(cutoff_days: int = 365) -> pd.Series | None:
    """Fetch historical ETH chain TVL time series from DeFiLlama.

    Args:
        cutoff_days: How many days back to include (default 365 = 1 year).

    Returns:
        pd.Series indexed by date (tz-naive), values in $B. None on failure.
    """
    try:
        url = _DEFI_LLAMA_HISTORICAL_URL.format(chain="Ethereum")
        resp = requests.get(url, timeout=_REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()  # [{date: unix_ts, tvl: float}, ...]
        if not data:
            return None

        dates  = pd.to_datetime([d["date"] for d in data], unit="s")
        values = [d["tvl"] / 1e9 for d in data]
        s = pd.Series(values, index=dates, name="ETH-TVL")
        s.index = s.index.tz_localize(None)

        cutoff = pd.Timestamp.now() - pd.DateOffset(days=cutoff_days)
        return s[s.index >= cutoff]
    except Exception as e:
        logger.warning("eth_tvl_series_failed", error=str(e))
        return None


def _fetch_btc_dominance() -> float | None:
    """Fetch BTC market cap dominance from CoinGecko /global endpoint.

    CoinGecko returns ``market_cap_percentage`` as a dict keyed by symbol.
    No API key required for this endpoint.

    Returns:
        BTC dominance as a percentage rounded to 1 dp (e.g. 54.3), or None on failure.
    """
    try:
        resp = requests.get(_COINGECKO_GLOBAL_URL, timeout=_REQUEST_TIMEOUT)
        resp.raise_for_status()
        dominance = resp.json().get("data", {}).get("market_cap_percentage", {}).get("btc")
        if dominance is None:
            return None
        return round(float(dominance), 1)
    except Exception as e:
        logger.warning("btc_dominance_fetch_failed", error=str(e))
        return None


def _fetch_fear_greed() -> dict[str, Any] | None:
    """Fetch Crypto Fear & Greed Index from alternative.me /fng/.

    Returns the latest entry with value (0–100) and text classification.
    No API key required.

    Returns:
        Dict with ``value`` (int 0–100), ``label`` (str), ``timestamp`` (str),
        or None on failure.
    """
    try:
        resp = requests.get(_FEAR_GREED_URL, timeout=_REQUEST_TIMEOUT, params={"limit": 1})
        resp.raise_for_status()
        entry = resp.json().get("data", [{}])[0]
        value = entry.get("value")
        if value is None:
            return None
        return {
            "value": int(value),
            "label": entry.get("value_classification", ""),
            "timestamp": entry.get("timestamp", ""),
        }
    except Exception as e:
        logger.warning("fear_greed_fetch_failed", error=str(e))
        return None


# ── Collector class ──────────────────────────────────────────────────────────

class CryptoCollector:
    """Collects BTC/ETH price data and DeFi ecosystem metrics.

    Data sources:
    - Prices: yfinance (BTC-USD, ETH-USD)
    - DeFi TVL: DeFiLlama API (free, no authentication)
    """

    def collect(self) -> dict[str, Any]:
        """Fetch snapshot of crypto prices, DeFi TVL, and market sentiment.

        Returns:
            Dict with keys:
                - ``btc``:           {price, pct_1d/1w/1m/3m/1y, date}
                - ``eth``:           {price, pct_1d/1w/1m/3m/1y, date}
                - ``eth_tvl_b``:     ETH chain DeFi TVL in $B
                - ``l2_tvl_b``:      Combined L2 TVL in $B (Base + Arb + OP + zkSync)
                - ``total_tvl_b``:   Total cross-chain DeFi TVL in $B
                - ``eth_btc_ratio``: ETH price / BTC price (e.g. 0.03241)
                - ``btc_dominance``: BTC market cap % of total crypto (e.g. 54.3)
                - ``fear_greed``:    {value: 0–100, label: str, timestamp: str}
                - ``fetched_at``:    ISO timestamp
        """
        logger.info("crypto_collect_start")

        btc = _build_price_entry("BTC", "BTC-USD")
        eth = _build_price_entry("ETH", "ETH-USD")
        tvl = _fetch_defi_tvl_snapshot()
        btc_dominance = _fetch_btc_dominance()
        fear_greed = _fetch_fear_greed()

        # ETH/BTC ratio — derived from existing price data, no extra API call
        eth_btc_ratio: float | None = None
        btc_price = btc.get("price") if "error" not in btc else None
        eth_price = eth.get("price") if "error" not in eth else None
        if btc_price and eth_price:
            eth_btc_ratio = round(eth_price / btc_price, 5)

        result: dict[str, Any] = {
            "btc": btc,
            "eth": eth,
            **tvl,
            "eth_btc_ratio": eth_btc_ratio,
            "btc_dominance": btc_dominance,
            "fear_greed": fear_greed,
            "fetched_at": datetime.now().isoformat(),
        }

        logger.info(
            "crypto_collect_done",
            btc_ok="error" not in btc,
            eth_ok="error" not in eth,
            eth_tvl_b=tvl.get("eth_tvl_b"),
            btc_dominance=btc_dominance,
            fear_greed_value=fear_greed.get("value") if fear_greed else None,
        )
        return result

    def collect_ecosystem(self) -> dict[str, dict[str, Any]]:
        """Fetch price data for crypto ecosystem companies.

        Collects 1d/1w/1m/3m/1y returns for COIN, HOOD, MSTR, SQ, BLK, BMNR.
        Circle (CRCL) is excluded — private company, no public price data.

        Returns:
            Dict mapping ticker → {price, pct_1d/1w/1m/3m/1y, date} or {error: str}.
        """
        logger.info("ecosystem_collect_start", tickers=list(ECOSYSTEM_TICKERS.keys()))
        result: dict[str, dict[str, Any]] = {}
        ok_count = 0

        for symbol, ticker_sym in ECOSYSTEM_TICKERS.items():
            entry = _build_price_entry(symbol, ticker_sym)
            result[symbol] = entry
            if "error" not in entry:
                ok_count += 1

        logger.info("ecosystem_collect_done", ok=ok_count, total=len(ECOSYSTEM_TICKERS))
        return result

    def collect_series(self, period: str = "1y") -> dict[str, pd.Series]:
        """Fetch price time series for BTC/ETH and ETH DeFi TVL.

        Args:
            period: yfinance period string ('1y', '2y', '6mo', etc.).
                    ETH-TVL is always fetched for ~1 year (DeFiLlama limitation).

        Returns:
            Dict mapping key → pd.Series (tz-naive DatetimeIndex).
            Keys: 'BTC-USD', 'ETH-USD', optionally 'ETH-TVL'.
        """
        result: dict[str, pd.Series] = {}

        for symbol, ticker_sym in CRYPTO_TICKERS.items():
            try:
                df = yf.Ticker(ticker_sym).history(period=period)
                if not df.empty and "Close" in df.columns:
                    s = df["Close"].dropna()
                    s.index = s.index.tz_localize(None)
                    result[ticker_sym] = s
            except Exception as e:
                logger.warning("crypto_series_failed",
                               ticker=ticker_sym, symbol=symbol, error=str(e))

        # ETH DeFi TVL (DeFiLlama always provides full history; we slice to 1y)
        eth_tvl = _fetch_eth_tvl_series(cutoff_days=365)
        if eth_tvl is not None and not eth_tvl.empty:
            result["ETH-TVL"] = eth_tvl

        return result
