"""통합 시그널 리포트 Excel 생성.

시그마 밴드(저점 매수 가격대) + 시장 심리(매수 시점) 결합.
3단계: 시장 → 종목 → 옵션 변동성.

Usage::

    python scripts/generate_signal_report.py                              # US 기본 실행
    python scripts/generate_signal_report.py --market us --universe full  # US 풀 유니버스
    python scripts/generate_signal_report.py --market kr --universe full  # KR 풀 유니버스
    python scripts/generate_signal_report.py --market kr --skip-sigma     # KR 워치리스트
    python scripts/generate_signal_report.py --top-n 20                   # 상위 20개
    python scripts/generate_signal_report.py --tickers AAPL NVDA          # 특정 종목만
    python scripts/generate_signal_report.py --skip-sigma                 # 시그마 건너뛰기
    python scripts/generate_signal_report.py --delay 0.5                  # 요청 간격
"""

from __future__ import annotations

import argparse
import math
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# curl_cffi (used by yfinance) cannot load SSL certificates from non-ASCII
# paths. If the project directory contains non-ASCII characters, copy the
# certifi CA bundle to a temp location with an ASCII-only path.
import certifi as _certifi

_cert_src = Path(_certifi.where())
try:
    str(_cert_src).encode("ascii")
except (UnicodeEncodeError, UnicodeDecodeError):
    _cert_dst = Path(os.environ.get("TEMP", "/tmp")) / "yf_certs" / "cacert.pem"
    if not _cert_dst.exists() or _cert_dst.stat().st_size != _cert_src.stat().st_size:
        _cert_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_cert_src, _cert_dst)
    os.environ.setdefault("CURL_CA_BUNDLE", str(_cert_dst))

import numpy as np
import pandas as pd
import yfinance as yf
from openpyxl import Workbook

from src.analyzers.market_sentiment import (
    compute_fear_greed,
    compute_regime_composite,
    compute_trend_strength,
    market_diagnosis,
)
from src.analyzers.regime import MarketRegimeEngine
from src.analyzers.technical import TechnicalAnalyzer, _bbands
from src.analyzers.trend import classify_stock_pattern
from src.core.config import PROJECT_ROOT
from src.core.logger import get_logger
from src.exporters.signal_builder import build_signal_sheet

# iv_sigma_report functions — reuse for sigma analysis
from scripts.iv_sigma_report import (
    _compute_hv,
    _compute_sigma_bands,
    _get_options_iv,
)

logger = get_logger("generate_signal_report")

# ============================================================
# Constants
# ============================================================

INDEX_TICKERS = [
    ("^GSPC", "S&P 500"),
    ("^NDX", "NASDAQ 100"),
    ("^IXIC", "NASDAQ Composite"),
    ("^DJI", "DOW"),
    ("^RUT", "Russell 2000"),
]

VIX_TICKER = ("^VIX", "VIX")

# Default stock list: Big Tech + Korean-popular US stocks, roughly by market cap
DEFAULT_TICKERS = [
    # Mag 7 + 빅테크
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA",
    # 반도체
    "TSM", "AVGO", "AMD", "MU", "INTC", "SMCI",
    # AI / 소프트웨어
    "PLTR", "ORCL", "SOUN",
    # 금융 / 핀테크
    "JPM", "COIN", "HOOD",
    # 크립토 생태계
    "BMNR", "MSTR",
    # 소비재 / 헬스케어
    "NFLX", "COST", "HIMS",
    # 핀테크 / 기타
    "SOFI",
    # 양자컴퓨터
    "IONQ", "RGTI",
    # 우주 / eVTOL
    "RKLB", "JOBY", "ACHR",
    # 에너지 / 원자로
    "SMR",
]

# Sigma analysis periods
# "주간": 금요일 만기 옵션 IV 사용, 실제 DTE로 시그마 계산.
def _days_to_friday() -> int:
    """이번 주 금요일까지 캘린더 일수.

    월~금: 해당 주 금요일. 토·일: 다음 주 금요일.
    """
    weekday = datetime.now().weekday()
    if weekday <= 4:  # Mon~Fri → this Friday
        return 4 - weekday
    return 4 + (7 - weekday)


_SIGMA_PERIODS = {
    "주간": _days_to_friday(),
    "1개월": 30,
}

_MIN_VALID_IV = 0.02

# KR market constants — use yfinance symbols (pykrx index API is broken)
KR_INDEX_TICKERS = [
    ("^KS11", "KOSPI"),
    ("^KQ11", "KOSDAQ"),
]

# Default KR watchlist (10 popular stocks)
KR_DEFAULT_TICKERS = [
    ("005930", "삼성전자"),
    ("000660", "SK하이닉스"),
    ("373220", "LG에너지솔루션"),
    ("207940", "삼성바이오로직스"),
    ("005380", "현대차"),
    ("000270", "기아"),
    ("068270", "셀트리온"),
    ("035420", "NAVER"),
    ("035720", "카카오"),
    ("051910", "LG화학"),
]

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "dashboards"


# ============================================================
# KR market helpers
# ============================================================


def _get_pykrx_stock() -> Any:
    """Lazy-import pykrx.stock module.

    Returns:
        pykrx.stock module.
    """
    from pykrx import stock as pykrx_stock  # noqa: PLC0415
    return pykrx_stock


def _fetch_kr_stock_ohlcv(ticker: str, days: int = 365) -> pd.DataFrame:
    """Fetch KR stock OHLCV via pykrx.

    Args:
        ticker: Korean stock code (e.g., "005930").
        days: Calendar days of history.

    Returns:
        DataFrame with [Open, High, Low, Close, Volume] columns.
    """
    pykrx_stock = _get_pykrx_stock()
    end = datetime.now()
    start = end - timedelta(days=days)
    start_str = start.strftime("%Y%m%d")
    end_str = end.strftime("%Y%m%d")

    try:
        df = pykrx_stock.get_market_ohlcv(start_str, end_str, ticker)
        if df.empty:
            return pd.DataFrame()
        column_map = {
            "시가": "Open",
            "고가": "High",
            "저가": "Low",
            "종가": "Close",
            "거래량": "Volume",
        }
        df = df.rename(columns=column_map)
        standard_cols = ["Open", "High", "Low", "Close", "Volume"]
        available = [c for c in standard_cols if c in df.columns]
        return df[available]
    except Exception as e:
        logger.warning("kr_stock_fetch_failed", ticker=ticker, error=str(e))
        return pd.DataFrame()


def _compute_hv_from_df(df: pd.DataFrame, window: int = 20) -> float | None:
    """Compute annualized historical volatility from OHLCV DataFrame.

    Args:
        df: OHLCV DataFrame with 'Close' column.
        window: Rolling window in trading days.

    Returns:
        Annualized HV (decimal) or None.
    """
    if df.empty or len(df) < window + 1:
        return None
    log_returns = np.log(df["Close"] / df["Close"].shift(1)).dropna()
    if len(log_returns) < window:
        return None
    hv = float(log_returns.rolling(window).std().iloc[-1]) * math.sqrt(252)
    return round(hv, 4) if not math.isnan(hv) else None


def _analyze_sigma_hv_only(
    ticker: str,
    ohlcv: pd.DataFrame,
    price: float,
) -> dict[str, Any]:
    """HV20-only sigma analysis (for KR stocks without options).

    Args:
        ticker: Stock code.
        ohlcv: OHLCV DataFrame.
        price: Current price.

    Returns:
        Sigma analysis result dict.
    """
    hv = _compute_hv_from_df(ohlcv)
    if hv is None:
        return {"ticker": ticker, "status": "no_data", "error": "HV 산출 불가"}

    periods: dict[str, Any] = {}
    for label, target_days in _SIGMA_PERIODS.items():
        band = _compute_sigma_bands(price, hv, target_days)
        band["vol"] = round(hv, 4)
        band["vol_pct"] = round(hv * 100, 1)
        band["vol_source"] = "HV20"
        band["vol_detail"] = "20일 실현 변동성"

        ref = _get_ref_price(ohlcv, target_days)
        sigma_move = band["sigma_move"]
        if ref is not None and sigma_move > 0:
            delta = price - ref
            band["pos_1s"] = round(delta / sigma_move * 100, 1)
            band["pos_2s"] = round(delta / (sigma_move * 2) * 100, 1)
        else:
            band["pos_1s"] = 0.0
            band["pos_2s"] = 0.0

        periods[label] = band

    return {
        "ticker": ticker,
        "status": "ok",
        "current_price": price,
        "hv20": round(hv * 100, 1),
        "periods": periods,
    }


def _fetch_kr_stock_data(
    ticker: str,
    name: str,
    marcap: int,
    ta: TechnicalAnalyzer,
    days: int = 365,
) -> dict[str, Any] | None:
    """Fetch and analyze a single KR stock.

    Args:
        ticker: Korean stock code.
        name: Company name.
        marcap: Market capitalization (KRW).
        ta: TechnicalAnalyzer instance.
        days: Calendar days of history.

    Returns:
        Stock data dict or None on failure.
    """
    try:
        df = _fetch_kr_stock_ohlcv(ticker, days)
        if df.empty or len(df) < 5:
            return None

        price = float(df["Close"].iloc[-1])

        # Price changes
        change_1d = None
        change_1w = None
        if len(df) >= 2:
            change_1d = round((price / float(df["Close"].iloc[-2]) - 1) * 100, 2)
        if len(df) >= 6:
            change_1w = round((price / float(df["Close"].iloc[-6]) - 1) * 100, 2)

        # Technical analysis
        tech_score = 50.0
        indicators: dict[str, Any] = {}
        try:
            tech_result = ta.analyze(ticker, ohlcv=df)
            tech_score = tech_result["score"]
            indicators = tech_result.get("indicators", {})
        except Exception:
            pass

        # MACD signal direction
        macd_val = indicators.get("macd")
        macd_sig_val = indicators.get("macd_signal")
        if macd_val is not None and macd_sig_val is not None:
            macd_signal = "Bullish" if macd_val > macd_sig_val else "Bearish"
        else:
            macd_signal = "N/A"

        # Trend strength
        trend = compute_trend_strength(ticker, name, df)

        ema_alignment = trend.get("ema_alignment", "N/A")
        ema_200_slope = trend.get("ema_200_slope")
        macd_histogram = indicators.get("macd_histogram")
        adx_change_5d = trend.get("adx_change_5d")

        # Volume ratio
        vol_ratio = None
        if "Volume" in df.columns and len(df) >= 20:
            vol_20_avg = df["Volume"].rolling(20).mean().iloc[-1]
            if vol_20_avg and vol_20_avg > 0:
                vol_ratio = round(float(df["Volume"].iloc[-1]) / float(vol_20_avg), 2)

        # BB width rank
        bb_width_rank = None
        if "Close" in df.columns and len(df) >= 20:
            try:
                bb_df = _bbands(df["Close"], length=20, std_dev=2)
                bb_width = bb_df["upper"] - bb_df["lower"]
                bb_width_valid = bb_width.dropna()
                lookback = min(120, len(bb_width_valid))
                if lookback >= 20:
                    recent = bb_width_valid.iloc[-lookback:]
                    current_width = float(recent.iloc[-1])
                    bb_width_rank = round(
                        float((recent < current_width).sum()) / len(recent) * 100, 1,
                    )
            except Exception:
                pass

        # Pattern classification
        pattern_result = classify_stock_pattern(
            trend_regime=trend.get("trend_regime", "N/A"),
            ema_alignment=ema_alignment,
            supertrend_dir=trend.get("supertrend_direction", "N/A"),
            macd_signal=macd_signal,
            rsi=trend.get("rsi"),
            adx=trend.get("adx"),
            adx_change_5d=adx_change_5d,
            change_1w=change_1w,
            price_vs_ema200=trend.get("price_vs_ema200"),
            ema_200_slope=ema_200_slope,
            vol_ratio=vol_ratio,
            bb_width_rank=bb_width_rank,
            macd_histogram=macd_histogram,
            price=price,
        )

        return {
            "ticker": ticker,
            "name": name,
            "sector": "N/A",
            "price": price,
            "change_1d": change_1d,
            "change_1w": change_1w,
            "market_cap": marcap,
            "rsi": trend.get("rsi"),
            "rsi_state": trend.get("rsi_state", "N/A"),
            "macd_signal": macd_signal,
            "supertrend_dir": trend.get("supertrend_direction", "N/A"),
            "adx": trend.get("adx"),
            "adx_trend": trend.get("adx_trend", "N/A"),
            "tech_score": tech_score,
            "trend_regime": trend.get("trend_regime", "N/A"),
            "trend_regime_kr": trend.get("trend_regime_kr", "N/A"),
            "price_vs_ema200": trend.get("price_vs_ema200"),
            "pattern": pattern_result["pattern"],
            "pattern_kr": pattern_result["pattern_kr"],
            "pattern_score": pattern_result["pattern_score"],
            "_yf_ticker": None,
            "_ohlcv": df,
        }
    except Exception as e:
        logger.warning("kr_stock_fetch_failed", ticker=ticker, error=str(e))
        return None


# ============================================================
# US market helpers
# ============================================================


def _fetch_index_ohlcv(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch OHLCV for a US index via yfinance.

    Args:
        ticker: yfinance ticker symbol.
        period: yfinance period string.

    Returns:
        OHLCV DataFrame.
    """
    try:
        df = yf.Ticker(ticker).history(period=period)
        if df.empty:
            return pd.DataFrame()
        standard_cols = ["Open", "High", "Low", "Close", "Volume"]
        available = [c for c in standard_cols if c in df.columns]
        return df[available]
    except Exception as e:
        logger.warning("index_fetch_failed", ticker=ticker, error=str(e))
        return pd.DataFrame()


def _fetch_stock_data(
    ticker: str,
    ta: TechnicalAnalyzer,
    period: str = "1y",
) -> dict[str, Any] | None:
    """Fetch and analyze a single stock.

    Creates one yf.Ticker object and fetches OHLCV once.
    Computes technical indicators, trend strength, and basic price changes.

    Args:
        ticker: Stock ticker.
        ta: TechnicalAnalyzer instance.
        period: yfinance period string.

    Returns:
        Stock data dict or None on failure.
    """
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        name = info.get("shortName") or info.get("longName") or ticker
        sector = info.get("sector") or "N/A"
        market_cap = info.get("marketCap")

        df = yf_ticker.history(period=period)
        if df.empty or len(df) < 5:
            return None

        standard_cols = ["Open", "High", "Low", "Close", "Volume"]
        available = [c for c in standard_cols if c in df.columns]
        df = df[available]

        price = float(df["Close"].iloc[-1])

        # Price changes
        change_1d = None
        change_1w = None
        if len(df) >= 2:
            change_1d = round((price / float(df["Close"].iloc[-2]) - 1) * 100, 2)
        if len(df) >= 6:
            change_1w = round((price / float(df["Close"].iloc[-6]) - 1) * 100, 2)

        # Technical analysis
        tech_score = 50.0
        indicators: dict[str, Any] = {}
        try:
            tech_result = ta.analyze(ticker, ohlcv=df)
            tech_score = tech_result["score"]
            indicators = tech_result.get("indicators", {})
        except Exception:
            pass

        # MACD signal direction
        macd_val = indicators.get("macd")
        macd_sig_val = indicators.get("macd_signal")
        if macd_val is not None and macd_sig_val is not None:
            macd_signal = "Bullish" if macd_val > macd_sig_val else "Bearish"
        else:
            macd_signal = "N/A"

        # Trend strength (ADX, Supertrend, RSI)
        trend = compute_trend_strength(ticker, name, df)

        # Fields previously computed but not passed through
        ema_alignment = trend.get("ema_alignment", "N/A")
        ema_200_slope = trend.get("ema_200_slope")
        macd_histogram = indicators.get("macd_histogram")
        adx_change_5d = trend.get("adx_change_5d")

        # Volume ratio: current volume / 20-day average
        vol_ratio = None
        if "Volume" in df.columns and len(df) >= 20:
            vol_20_avg = df["Volume"].rolling(20).mean().iloc[-1]
            if vol_20_avg and vol_20_avg > 0:
                vol_ratio = round(float(df["Volume"].iloc[-1]) / float(vol_20_avg), 2)

        # BB width rank: percentile of current BB width over 120 days
        bb_width_rank = None
        if "Close" in df.columns and len(df) >= 20:
            try:
                bb_df = _bbands(df["Close"], length=20, std_dev=2)
                bb_width = bb_df["upper"] - bb_df["lower"]
                bb_width_valid = bb_width.dropna()
                lookback = min(120, len(bb_width_valid))
                if lookback >= 20:
                    recent = bb_width_valid.iloc[-lookback:]
                    current_width = float(recent.iloc[-1])
                    bb_width_rank = round(
                        float((recent < current_width).sum()) / len(recent) * 100, 1,
                    )
            except Exception:
                pass

        # Pattern classification
        pattern_result = classify_stock_pattern(
            trend_regime=trend.get("trend_regime", "N/A"),
            ema_alignment=ema_alignment,
            supertrend_dir=trend.get("supertrend_direction", "N/A"),
            macd_signal=macd_signal,
            rsi=trend.get("rsi"),
            adx=trend.get("adx"),
            adx_change_5d=adx_change_5d,
            change_1w=change_1w,
            price_vs_ema200=trend.get("price_vs_ema200"),
            ema_200_slope=ema_200_slope,
            vol_ratio=vol_ratio,
            bb_width_rank=bb_width_rank,
            macd_histogram=macd_histogram,
            price=price,
        )

        return {
            "ticker": ticker,
            "name": name,
            "sector": sector,
            "price": price,
            "change_1d": change_1d,
            "change_1w": change_1w,
            "market_cap": market_cap,
            "rsi": trend.get("rsi"),
            "rsi_state": trend.get("rsi_state", "N/A"),
            "macd_signal": macd_signal,
            "supertrend_dir": trend.get("supertrend_direction", "N/A"),
            "adx": trend.get("adx"),
            "adx_trend": trend.get("adx_trend", "N/A"),
            "tech_score": tech_score,
            "trend_regime": trend.get("trend_regime", "N/A"),
            "trend_regime_kr": trend.get("trend_regime_kr", "N/A"),
            "price_vs_ema200": trend.get("price_vs_ema200"),
            "pattern": pattern_result["pattern"],
            "pattern_kr": pattern_result["pattern_kr"],
            "pattern_score": pattern_result["pattern_score"],
            # Keep yf_ticker + df for sigma reuse
            "_yf_ticker": yf_ticker,
            "_ohlcv": df,
        }
    except Exception as e:
        logger.warning("stock_fetch_failed", ticker=ticker, error=str(e))
        return None


def _get_ref_price(hist: Any, target_days: int) -> float | None:
    """기간 시작가 조회 (target_days 거래일 전 종가).

    Args:
        hist: OHLCV DataFrame (최근 3개월).
        target_days: 캘린더 일 수.

    Returns:
        기간 시작 종가 또는 None.
    """
    if hist is None or hist.empty:
        return None
    # 캘린더일 → 거래일 근사 (×5/7)
    trading_days = max(1, int(target_days * 5 / 7))
    if len(hist) > trading_days:
        return float(hist["Close"].iloc[-(trading_days + 1)])
    return float(hist["Close"].iloc[0])


def _analyze_sigma(
    ticker: str,
    yf_ticker: Any,
    price: float,
    hv: float | None,
    hist: Any = None,
) -> dict[str, Any]:
    """Run sigma band analysis reusing existing yf.Ticker and HV.

    Args:
        ticker: Stock ticker.
        yf_ticker: Already-constructed yf.Ticker object.
        price: Current price.
        hv: Pre-computed HV20 (decimal) or None.
        hist: OHLCV DataFrame for reference price lookup.

    Returns:
        Sigma analysis result dict.
    """
    periods: dict[str, Any] = {}

    for label, target_days in _SIGMA_PERIODS.items():
        # Try options IV first (주간 → 금요일 만기만 사용)
        opt_iv, exp_used, exp_dte = _get_options_iv(
            yf_ticker, price, target_days, friday_only=(label == "주간"),
        )

        if opt_iv is not None:
            vol = opt_iv
            vol_source = "IV"
            vol_detail = f"만기 {exp_used} (DTE {exp_dte})"
        elif hv is not None:
            vol = hv
            vol_source = "HV20"
            vol_detail = "20일 실현 변동성"
        else:
            periods[label] = {"error": "변동성 데이터 없음"}
            continue

        # 주간: 실제 만기 DTE로 시그마 계산 (target이 아닌 실제 옵션 만기 기준)
        sigma_days = exp_dte if exp_dte else target_days
        band = _compute_sigma_bands(price, vol, sigma_days)
        band["vol"] = round(vol, 4)
        band["vol_pct"] = round(vol * 100, 1)
        band["vol_source"] = vol_source
        band["vol_detail"] = vol_detail
        if exp_used:
            band["expiry_used"] = exp_used
            band["expiry_dte"] = exp_dte

        # 시그마 밴드 내 위치 (기간 시작가 대비 현재가)
        ref = _get_ref_price(hist, sigma_days)
        sigma_move = band["sigma_move"]
        if ref is not None and sigma_move > 0:
            delta = price - ref
            band["pos_1s"] = round(delta / sigma_move * 100, 1)
            band["pos_2s"] = round(delta / (sigma_move * 2) * 100, 1)
        else:
            band["pos_1s"] = 0.0
            band["pos_2s"] = 0.0

        # 주간 라벨에 실제 만기일/DTE 표시
        actual_label = f"{label}({exp_used},{sigma_days}d)" if exp_used and label == "주간" else label
        periods[actual_label] = band

    has_valid = any("sigma_1" in v for v in periods.values())
    if not has_valid:
        return {"ticker": ticker, "status": "no_data", "error": "분석 불가"}

    return {
        "ticker": ticker,
        "status": "ok",
        "current_price": price,
        "hv20": round(hv * 100, 1) if hv else None,
        "periods": periods,
    }


def _try_collect_putcall() -> dict[str, Any] | None:
    """Try to collect put/call ratio data.

    Returns:
        Dict with ratio and sentiment, or None.
    """
    try:
        from src.collectors.sentiment.putcall_collector import PutCallRatioCollector
        collector = PutCallRatioCollector()
        data = collector.collect()
        if data:
            # Prefer equity ratio
            equity = next((d for d in data if d["type"] == "equity"), data[0])
            return {
                "ratio": equity["pc_ratio"],
                "sentiment": equity.get("sentiment", ""),
            }
    except Exception as e:
        logger.info("putcall_collection_skipped", error=str(e))
    return None


def _try_collect_cnn_fg() -> dict[str, Any] | None:
    """Try to collect CNN Fear & Greed data.

    Returns:
        Dict with score and level, or None.
    """
    try:
        from src.collectors.sentiment.cnn_fear_greed_collector import CNNFearGreedCollector
        collector = CNNFearGreedCollector()
        data = collector.collect()
        if data:
            return {
                "score": data[0].get("score"),
                "level": data[0].get("level", ""),
            }
    except Exception as e:
        logger.info("cnn_fg_collection_skipped", error=str(e))
    return None


# ============================================================
# Main pipeline
# ============================================================


def _run_us_pipeline(args: argparse.Namespace) -> None:
    """Run US market signal report pipeline.

    Args:
        args: Parsed CLI arguments.
    """
    from src.collectors.market.constituents import get_combined_universe

    # Determine stock list
    if args.tickers:
        stock_tickers = [t.upper() for t in args.tickers]
    elif args.universe == "full":
        print("[0/6] Fetching US full universe (S&P 500 + NASDAQ 100)...")
        stock_tickers = get_combined_universe()
        if args.top_n:
            stock_tickers = stock_tickers[:args.top_n]
        print(f"  Universe: {len(stock_tickers)} stocks\n")
    elif args.top_n:
        stock_tickers = DEFAULT_TICKERS[:args.top_n]
    else:
        stock_tickers = DEFAULT_TICKERS[:]

    print("=" * 60)
    print("  Integrated Signal Report Generator — US Market")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Stocks: {len(stock_tickers)}  |  Sigma: {'OFF' if args.skip_sigma else 'ON'}")
    print("=" * 60)
    print()

    # ===== Step 1: Collect Index Data =====
    print("[1/6] Collecting index data...")
    index_ohlcv: dict[str, dict[str, Any]] = {}

    for ticker, name in INDEX_TICKERS:
        print(f"  {name}...", end=" ", flush=True)
        df = _fetch_index_ohlcv(ticker)
        if not df.empty:
            current = float(df["Close"].iloc[-1])
            change_1d = None
            change_1w = None
            if len(df) >= 2:
                change_1d = round((current / float(df["Close"].iloc[-2]) - 1) * 100, 2)
            if len(df) >= 6:
                change_1w = round((current / float(df["Close"].iloc[-6]) - 1) * 100, 2)
            index_ohlcv[ticker] = {
                "name": name,
                "ohlcv": df,
                "current": current,
                "change_1d": change_1d,
                "change_1w": change_1w,
            }
            print(f"OK ({len(df)} rows)")
        else:
            print("FAILED")
        time.sleep(0.3)

    # VIX
    print(f"  VIX...", end=" ", flush=True)
    vix_df = _fetch_index_ohlcv(VIX_TICKER[0])
    vix_current = 0.0
    if not vix_df.empty:
        vix_current = float(vix_df["Close"].iloc[-1])
        print(f"OK ({vix_current:.2f})")
    else:
        print("FAILED")
    print(f"  Collected {len(index_ohlcv)} indices + VIX\n")

    # ===== Step 2: Compute Market Sentiment =====
    print("[2/6] Computing market sentiment...")
    non_vix_data = {k: v["ohlcv"] for k, v in index_ohlcv.items()}

    # Try external data collection
    putcall_raw = None
    cnn_fg_raw = None
    try:
        from src.collectors.sentiment.putcall_collector import PutCallRatioCollector
        putcall_raw = PutCallRatioCollector().collect() or None
        if putcall_raw:
            print(f"  Put/Call data: collected ({len(putcall_raw)} series)")
    except Exception:
        pass
    try:
        from src.collectors.sentiment.cnn_fear_greed_collector import CNNFearGreedCollector
        cnn_fg_raw = CNNFearGreedCollector().collect() or None
        if cnn_fg_raw:
            print(f"  CNN Fear & Greed: collected")
    except Exception:
        pass

    fear_greed = compute_fear_greed(
        vix_current, non_vix_data,
        putcall_data=putcall_raw,
        cnn_fear_greed=cnn_fg_raw,
    )
    print(f"  Fear/Greed: {fear_greed['score']:.1f} ({fear_greed['level']})")

    # Trend strength for each index
    index_trend: list[dict[str, Any]] = []
    for ticker, info in index_ohlcv.items():
        ts = compute_trend_strength(ticker, info["name"], info["ohlcv"])
        ts["current"] = info["current"]
        ts["change_1d"] = info.get("change_1d")
        ts["change_1w"] = info.get("change_1w")
        index_trend.append(ts)
        print(f"  {info['name']}: ADX={ts.get('adx', 'N/A')}, "
              f"ST={ts.get('supertrend_direction', 'N/A')}, "
              f"RSI={ts.get('rsi', 'N/A')}, "
              f"Trend={ts.get('trend_regime', 'N/A')}")

    diagnosis = market_diagnosis(fear_greed, index_trend)
    print(f"  Diagnosis: {diagnosis['verdict']}\n")

    # VIX level classification
    if vix_current >= 30:
        vix_level = "High (Fear)"
    elif vix_current >= 20:
        vix_level = "Elevated (Caution)"
    elif vix_current <= 12:
        vix_level = "Low (Complacent)"
    else:
        vix_level = "Normal"

    # Build put/call summary for market_data
    putcall_summary = _try_collect_putcall() if not putcall_raw else None
    if putcall_raw:
        equity = next((d for d in putcall_raw if d["type"] == "equity"), None)
        if equity:
            putcall_summary = {
                "ratio": equity["pc_ratio"],
                "sentiment": equity.get("sentiment", ""),
            }

    cnn_fg_summary = None
    if cnn_fg_raw:
        cnn_fg_summary = {
            "score": cnn_fg_raw[0].get("score"),
            "level": cnn_fg_raw[0].get("level", ""),
        }

    market_data: dict[str, Any] = {
        "index_trend": index_trend,
        "vix": {"current": vix_current, "level": vix_level},
        "fear_greed": fear_greed,
        "diagnosis": diagnosis,
        "putcall": putcall_summary,
        "cnn_fg": cnn_fg_summary,
    }

    # ===== Step 3: Collect Stock Data =====
    print(f"[3/6] Collecting stock data ({len(stock_tickers)} stocks)...")
    ta = TechnicalAnalyzer()
    stock_data_list: list[dict[str, Any]] = []

    for i, ticker in enumerate(stock_tickers, 1):
        print(f"  [{i}/{len(stock_tickers)}] {ticker}...", end=" ", flush=True)
        data = _fetch_stock_data(ticker, ta)
        if data:
            stock_data_list.append(data)
            print(f"OK (Score={data['tech_score']:.1f}, Trend={data.get('trend_regime', 'N/A')}, Pattern={data.get('pattern', '—')})")
        else:
            print("SKIP")
        if i < len(stock_tickers):
            time.sleep(args.delay)

    # Sort: top N by tech_score at front, rest by market cap
    stock_data_list.sort(key=lambda x: x.get("tech_score") or 0, reverse=True)
    top_n_action = min(50, len(stock_data_list))
    top_slice = stock_data_list[:top_n_action]
    rest_slice = sorted(
        stock_data_list[top_n_action:],
        key=lambda x: x.get("market_cap") or 0,
        reverse=True,
    )
    stock_data_list = top_slice + rest_slice
    print(f"  Collected {len(stock_data_list)} stocks "
          f"(top {top_n_action} by signal strength)\n")

    # ===== Step 3.5: Regime Composite =====
    print("[3.5] Computing regime composite...")

    # Breadth: % of collected stocks above their 200 DMA
    if stock_data_list:
        above_200 = sum(
            1 for s in stock_data_list if (s.get("price_vs_ema200") or 0) > 0
        )
        breadth_pct = above_200 / len(stock_data_list) * 100
    else:
        breadth_pct = 50.0

    # SPY trend regime (^GSPC is the S&P 500 proxy)
    spy_trend_regime = "Sideways"
    for t in index_trend:
        if t["ticker"] == "^GSPC":
            spy_trend_regime = t.get("trend_regime", "Sideways")
            break

    exposure = compute_regime_composite(
        spy_trend_regime=spy_trend_regime,
        vix_current=vix_current,
        breadth_pct=breadth_pct,
        fg_score=fear_greed["score"],
    )
    market_data["exposure"] = exposure

    print(f"  Composite Score: {exposure['composite_score']:+.1f}")
    print(f"  Regime: {exposure['regime_label']} ({exposure['regime_label_en']})")
    print(f"  Net Exposure: {exposure['net_exposure']:.0f}%  |  "
          f"Gross: {exposure['gross_exposure']:.0f}%")
    print(f"  Long: {exposure['long_allocation']:.1f}%  |  "
          f"Short: {exposure['short_allocation']:.1f}%")
    print(f"  Breadth: {exposure['breadth_pct']:.1f}% above 200 DMA\n")

    # Investment Stance (MarketRegimeEngine — FRED/FX/기술적/뉴스 기반)
    investment_stance: dict[str, Any] | None = None
    try:
        print("[3.6] Computing investment stance (FRED/FX/기술적/뉴스)...")
        regime_result = MarketRegimeEngine().compute()
        if regime_result:
            investment_stance = {
                "regime": regime_result.regime,
                "confidence": regime_result.confidence,
                "drivers": regime_result.drivers,
                "sizing": regime_result.sizing,
            }
            print(f"  Investment Stance: {regime_result.regime} "
                  f"(신뢰도 {int(regime_result.confidence * 100)}%)\n")
        else:
            print("  Investment Stance: 계산 실패 — 생략\n")
    except Exception as _e:
        print(f"  Investment Stance: 오류({_e}) — 생략\n")

    # ===== Step 4: Sigma Analysis (parallel) =====
    sigma_results: list[dict[str, Any]] = []
    if not args.skip_sigma:
        workers = min(args.sigma_workers, len(stock_data_list))
        print(f"[4/6] Running sigma analysis ({len(stock_data_list)} stocks, {workers} threads)...")

        def _sigma_worker(s: dict[str, Any]) -> dict[str, Any]:
            """Single-stock sigma analysis worker (thread-safe)."""
            yf_ticker = s.get("_yf_ticker")
            price = s["price"]
            hv = _compute_hv_from_df(s.get("_ohlcv"))
            return _analyze_sigma(s["ticker"], yf_ticker, price, hv, hist=s.get("_ohlcv"))

        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_to_idx = {
                pool.submit(_sigma_worker, s): i
                for i, s in enumerate(stock_data_list)
            }
            sigma_results = [None] * len(stock_data_list)  # type: ignore[list-item]
            done_count = 0
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                result = future.result()
                sigma_results[idx] = result
                done_count += 1
                ticker = stock_data_list[idx]["ticker"]
                if result["status"] == "ok":
                    first_period = next(iter(result.get("periods", {}).values()), {})
                    src = first_period.get("vol_source", "?")
                    vol = first_period.get("vol_pct", 0)
                    print(f"  [{done_count}/{len(stock_data_list)}] {ticker}... {src} {vol:.1f}%")
                else:
                    print(f"  [{done_count}/{len(stock_data_list)}] {ticker}... {result.get('error', 'failed')}")
        print(f"  Sigma analysis done: {sum(1 for r in sigma_results if r['status'] == 'ok')} OK\n")
    else:
        print("[4/6] Sigma analysis skipped (--skip-sigma)\n")

    # ===== Step 5: Build Excel =====
    _build_and_save(args, "us", market_data, stock_data_list, sigma_results,
                    investment_stance=investment_stance)


def _run_kr_pipeline(args: argparse.Namespace) -> None:
    """Run KR market signal report pipeline.

    Args:
        args: Parsed CLI arguments.
    """
    from src.collectors.market.constituents import fetch_kr_top_tickers

    # Determine stock list
    if args.tickers:
        # Manual tickers: [(code, name, 0)]
        kr_tickers = [(t, t, 0) for t in args.tickers]
    elif args.universe == "full":
        print("[0/6] Fetching KR full universe (Top 200 by market cap)...")
        kr_tickers = fetch_kr_top_tickers(200)
        if args.top_n:
            kr_tickers = kr_tickers[:args.top_n]
        print(f"  Universe: {len(kr_tickers)} stocks\n")
    else:
        # Watchlist with marcap=0 placeholder
        kr_tickers = [(code, name, 0) for code, name in KR_DEFAULT_TICKERS]
        if args.top_n:
            kr_tickers = kr_tickers[:args.top_n]

    print("=" * 60)
    print("  Integrated Signal Report Generator — KR Market")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Stocks: {len(kr_tickers)}  |  Sigma: {'OFF' if args.skip_sigma else 'ON'}")
    print("=" * 60)
    print()

    # ===== Step 1: Collect KR Index Data (via yfinance) =====
    print("[1/6] Collecting KR index data...")
    index_ohlcv: dict[str, dict[str, Any]] = {}

    for code, name in KR_INDEX_TICKERS:
        print(f"  {name}...", end=" ", flush=True)
        df = _fetch_index_ohlcv(code)  # yfinance works for ^KS11, ^KQ11
        if not df.empty:
            current = float(df["Close"].iloc[-1])
            change_1d = None
            change_1w = None
            if len(df) >= 2:
                change_1d = round((current / float(df["Close"].iloc[-2]) - 1) * 100, 2)
            if len(df) >= 6:
                change_1w = round((current / float(df["Close"].iloc[-6]) - 1) * 100, 2)
            index_ohlcv[code] = {
                "name": name,
                "ohlcv": df,
                "current": current,
                "change_1d": change_1d,
                "change_1w": change_1w,
            }
            print(f"OK ({len(df)} rows, {current:,.2f})")
        else:
            print("FAILED")
        time.sleep(0.3)

    print(f"  Collected {len(index_ohlcv)} indices\n")

    # ===== Step 1.5: VKOSPI proxy (KODEX200 ETF HV20) =====
    import FinanceDataReader as fdr  # noqa: PLC0415

    vkospi_val = 0.0
    vkospi_level = "N/A"
    try:
        kodex_df = fdr.DataReader("069500")
        if kodex_df is not None and not kodex_df.empty:
            hv = _compute_hv_from_df(kodex_df)
            if hv is not None:
                vkospi_val = round(hv * 100, 2)
                if vkospi_val >= 30:
                    vkospi_level = "High (Fear)"
                elif vkospi_val >= 20:
                    vkospi_level = "Elevated"
                elif vkospi_val <= 12:
                    vkospi_level = "Low"
                else:
                    vkospi_level = "Normal"
    except Exception as e:
        logger.warning("vkospi_proxy_failed", error=str(e))
    print(f"  VKOSPI proxy (KODEX200 HV20): {vkospi_val:.1f}% ({vkospi_level})")

    # ===== Step 2: Compute KR Market Sentiment (simplified) =====
    print("[2/6] Computing KR market sentiment...")

    # Trend strength for each index
    index_trend: list[dict[str, Any]] = []
    for code, info in index_ohlcv.items():
        ts = compute_trend_strength(code, info["name"], info["ohlcv"])
        ts["current"] = info["current"]
        ts["change_1d"] = info.get("change_1d")
        ts["change_1w"] = info.get("change_1w")
        index_trend.append(ts)
        print(f"  {info['name']}: ADX={ts.get('adx', 'N/A')}, "
              f"ST={ts.get('supertrend_direction', 'N/A')}, "
              f"RSI={ts.get('rsi', 'N/A')}, "
              f"Trend={ts.get('trend_regime', 'N/A')}")

    # KR: use VKOSPI proxy for VIX equivalent
    non_vix_data = {k: v["ohlcv"] for k, v in index_ohlcv.items()}
    vix_current = vkospi_val  # feed into regime composite

    fear_greed = compute_fear_greed(vix_current, non_vix_data)
    print(f"  Fear/Greed (simplified): {fear_greed['score']:.1f} ({fear_greed['level']})")

    diagnosis = market_diagnosis(fear_greed, index_trend)
    print(f"  Diagnosis: {diagnosis['verdict']}\n")

    market_data: dict[str, Any] = {
        "index_trend": index_trend,
        "vix": {"current": vkospi_val, "level": vkospi_level, "label": "VKOSPI (proxy)"},
        "fear_greed": fear_greed,
        "diagnosis": diagnosis,
        "putcall": None,
        "cnn_fg": None,
    }

    # ===== Step 3: Collect KR Stock Data =====
    print(f"[3/6] Collecting KR stock data ({len(kr_tickers)} stocks)...")
    ta = TechnicalAnalyzer()
    stock_data_list: list[dict[str, Any]] = []

    for i, (code, name, marcap) in enumerate(kr_tickers, 1):
        print(f"  [{i}/{len(kr_tickers)}] {code} {name}...", end=" ", flush=True)
        data = _fetch_kr_stock_data(code, name, marcap, ta)
        if data:
            stock_data_list.append(data)
            print(f"OK (Score={data['tech_score']:.1f}, Trend={data.get('trend_regime', 'N/A')}, Pattern={data.get('pattern', '—')})")
        else:
            print("SKIP")
        if i < len(kr_tickers):
            time.sleep(args.delay)

    # Sort by market cap (descending)
    stock_data_list.sort(
        key=lambda x: x.get("market_cap") or 0,
        reverse=True,
    )
    print(f"  Collected {len(stock_data_list)} stocks\n")

    # ===== Step 3.5: Regime Composite =====
    print("[3.5] Computing regime composite...")

    if stock_data_list:
        above_200 = sum(
            1 for s in stock_data_list if (s.get("price_vs_ema200") or 0) > 0
        )
        breadth_pct = above_200 / len(stock_data_list) * 100
    else:
        breadth_pct = 50.0

    # KOSPI trend regime (^KS11)
    kospi_trend_regime = "Sideways"
    for t in index_trend:
        if t["ticker"] == "^KS11":
            kospi_trend_regime = t.get("trend_regime", "Sideways")
            break

    exposure = compute_regime_composite(
        spy_trend_regime=kospi_trend_regime,
        vix_current=vix_current,
        breadth_pct=breadth_pct,
        fg_score=fear_greed["score"],
    )
    market_data["exposure"] = exposure

    print(f"  Composite Score: {exposure['composite_score']:+.1f}")
    print(f"  Regime: {exposure['regime_label']} ({exposure['regime_label_en']})")
    print(f"  Net Exposure: {exposure['net_exposure']:.0f}%  |  "
          f"Gross: {exposure['gross_exposure']:.0f}%")
    print(f"  Breadth: {exposure['breadth_pct']:.1f}% above 200 DMA\n")

    # ===== Step 4: KR Sigma Analysis (HV20 only) =====
    sigma_results: list[dict[str, Any]] = []
    if not args.skip_sigma:
        print(f"[4/6] Running HV20 sigma analysis ({len(stock_data_list)} stocks)...")
        for i, s in enumerate(stock_data_list, 1):
            ticker = s["ticker"]
            print(f"  [{i}/{len(stock_data_list)}] {ticker}...", end=" ", flush=True)
            ohlcv = s.get("_ohlcv")
            price = s["price"]

            result = _analyze_sigma_hv_only(ticker, ohlcv, price)
            sigma_results.append(result)

            if result["status"] == "ok":
                print(f"HV20 {result.get('hv20', 0):.1f}%")
            else:
                print(f"{result.get('error', 'failed')}")

            if i < len(stock_data_list):
                time.sleep(0.1)
        print(f"  Sigma analysis done: {sum(1 for r in sigma_results if r['status'] == 'ok')} OK\n")
    else:
        print("[4/6] Sigma analysis skipped (--skip-sigma)\n")

    # ===== Step 5: Build Excel =====
    _build_and_save(args, "kr", market_data, stock_data_list, sigma_results,
                    investment_stance=None)


def _build_and_save(
    args: argparse.Namespace,
    market: str,
    market_data: dict[str, Any],
    stock_data_list: list[dict[str, Any]],
    sigma_results: list[dict[str, Any]],
    investment_stance: dict[str, Any] | None = None,
) -> None:
    """Build Excel workbook and save to disk.

    Args:
        args: Parsed CLI arguments.
        market: "us" or "kr".
        market_data: Market-level data dict.
        stock_data_list: List of stock data dicts (may contain internal fields).
        sigma_results: List of sigma analysis dicts.
        investment_stance: MarketRegimeEngine 결과 (RISK_ON/NEUTRAL/RISK_OFF). None이면 생략.
    """
    print("[5/6] Building Excel workbook...")

    # Clean internal fields before passing to builder
    clean_stock_data = []
    for s in stock_data_list:
        clean = {k: v for k, v in s.items() if not k.startswith("_")}
        clean_stock_data.append(clean)

    wb = Workbook()
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]

    build_signal_sheet(wb, market_data, clean_stock_data, sigma_results, market=market,
                       investment_stance=investment_stance)
    print("  [OK] Integrated_Signal sheet built")

    # ===== Step 6: Save =====
    print("\n[6/6] Saving...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    market_label = market.upper()
    output_path = OUTPUT_DIR / f"Signal_Report_{market_label}_{date_str}.xlsx"
    try:
        wb.save(str(output_path))
    except PermissionError:
        for seq in range(2, 100):
            alt = OUTPUT_DIR / f"Signal_Report_{market_label}_{date_str}_v{seq}.xlsx"
            if not alt.exists():
                output_path = alt
                break
        wb.save(str(output_path))
        print(f"  (original file locked, saved as {output_path.name})")

    file_size = output_path.stat().st_size / 1024

    fear_greed = market_data.get("fear_greed", {})
    diagnosis = market_data.get("diagnosis", {})

    print(f"\n{'=' * 60}")
    print(f"  Signal Report saved: {output_path}")
    print(f"  File size: {file_size:.0f} KB")
    print(f"  Market: {market_label}  |  Stocks: {len(clean_stock_data)} | Sigma: {len(sigma_results)}")
    print(f"  Fear/Greed: {fear_greed.get('score', 0):.1f} ({fear_greed.get('level', 'N/A')})")
    print(f"  Diagnosis: {diagnosis.get('verdict', 'N/A')}")
    print(f"{'=' * 60}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="통합 시그널 리포트 Excel 생성 (US/KR)",
    )
    parser.add_argument(
        "--market", choices=["us", "kr"], default="us",
        help="시장 선택 (기본: us)",
    )
    parser.add_argument(
        "--universe", choices=["full", "watchlist"], default="watchlist",
        help="유니버스 (full: 전체, watchlist: 기본 종목)",
    )
    parser.add_argument(
        "--tickers", nargs="*", default=None,
        help="분석할 종목 (예: AAPL NVDA TSLA / 005930 000660)",
    )
    parser.add_argument(
        "--top-n", type=int, default=None,
        help="유니버스에서 상위 N개만 사용",
    )
    parser.add_argument(
        "--skip-sigma", action="store_true",
        help="시그마 밴드 분석 건너뛰기 (빠르게)",
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="종목 간 요청 딜레이(초) (기본: 0.5)",
    )
    parser.add_argument(
        "--sigma-workers", type=int, default=15,
        help="시그마 병렬 분석 스레드 수 (기본: 15)",
    )
    args = parser.parse_args()

    if args.market == "kr":
        _run_kr_pipeline(args)
    else:
        _run_us_pipeline(args)


if __name__ == "__main__":
    main()
