"""Market Regime Engine — FRED + FX + 기술적 지표 + 뉴스 센티먼트 종합.

레짐 판단 결과를 Investment Standup 형식으로 모닝 브리핑에 주입한다.
자동 체결 없음 — 판단 보조만.

사용 예시::

    engine = MarketRegimeEngine()
    result = engine.compute()
    if result:
        print(result.regime)       # "RISK_ON"
        print(result.confidence)   # 0.72
        print(result.drivers)      # ["ADX 34 (강한 추세)", ...]
        print(result.sizing)       # {"TSLA": 0.25, "BTC": 0.15, ...}
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

import yaml
from sqlalchemy import func, select

from src.core.database import NewsItemDB, get_session
from src.core.logger import get_logger

# ---------------------------------------------------------------------------
# Crypto ticker 매핑 (yfinance 심볼)
# ---------------------------------------------------------------------------

_CRYPTO_TICKER_MAP: dict[str, str] = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
}

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "regime_sizing.yaml"
_LOOKBACK_HOURS = 24  # 뉴스 센티먼트 집계 윈도우
_OHLCV_PERIOD = "1mo"  # yfinance OHLCV 조회 기간


def _resolve_ticker(ticker: str) -> str:
    """config 심볼을 yfinance 심볼로 변환."""
    return _CRYPTO_TICKER_MAP.get(ticker, ticker)


# ---------------------------------------------------------------------------
# 결과 데이터클래스
# ---------------------------------------------------------------------------


@dataclass
class RegimeResult:
    """MarketRegimeEngine.compute() 반환값.

    Attributes:
        regime: RISK_ON / NEUTRAL / RISK_OFF
        confidence: 0.0~1.0 (abs(합산 점수) / 최대 가능 점수)
        drivers: 레짐 근거 문장 리스트 (최대 3개, 사람이 읽는 한 줄씩)
        sizing: 레짐별 종목 목표 비율 {"TSLA": 0.25, ...} (가이드, 최종 결정은 사용자)
        raw_score: 가중 합산 전 원시 점수 (디버그용)
    """

    regime: Literal["RISK_ON", "NEUTRAL", "RISK_OFF"]
    confidence: float
    drivers: list[str]
    sizing: dict[str, float]
    raw_score: float = 0.0


# ---------------------------------------------------------------------------
# 인자 정규화 함수 (각 factor → [-1, +1])
# ---------------------------------------------------------------------------


def _normalize_rsi(rsi: float) -> float:
    """RSI → [-1, +1].

    < 35 (과매도) → +1, > 70 (과매수) → -1, 45~55 → 0 근방.
    """
    if rsi <= 35:
        return 1.0
    if rsi >= 70:
        return -1.0
    # 35~70 선형 보간: 35→+1, 52.5→0, 70→-1
    return 1.0 - 2.0 * (rsi - 35.0) / (70.0 - 35.0)


def _normalize_macd_histogram(histogram: float) -> float:
    """MACD 히스토그램 → [-1, +1]. 양수면 +1, 음수면 -1, 0은 0."""
    if histogram > 0:
        return min(1.0, histogram / 0.5)  # 0.5 이상이면 만점
    if histogram < 0:
        return max(-1.0, histogram / 0.5)
    return 0.0


def _normalize_adx(adx: float, direction_bullish: bool) -> float:
    """ADX + 방향 → [-1, +1].

    ADX > 30이고 상승 방향 → +1
    ADX > 30이고 하락 방향 → -1
    ADX < 20 → 0 (추세 없음)
    """
    if adx < 20:
        return 0.0
    if adx >= 30:
        return 1.0 if direction_bullish else -1.0
    # 20~30: 약한 추세, 비례
    strength = (adx - 20.0) / 10.0
    return strength if direction_bullish else -strength


def _normalize_supertrend(bullish: bool) -> float:
    """Supertrend → +1 (상승) / -1 (하락)."""
    return 1.0 if bullish else -1.0


def _normalize_fred_liquidity(wow_change: float | None) -> float:
    """FRED net_liquidity WoW 변화 → [-1, +1].

    > 0 (증가) → +1, < 0 (감소) → -1, 0 또는 None → 0.
    """
    if wow_change is None:
        return 0.0
    if wow_change > 0:
        return 1.0
    if wow_change < 0:
        return -1.0
    return 0.0


def _normalize_dxy(pct_1w: float | None) -> float:
    """DXY 5일 모멘텀 → [-1, +1].

    < -0.5% (달러 약세) → +1 (위험자산 순풍)
    > +0.5% (달러 강세) → -1 (위험자산 역풍)
    ±0.5% 내 → 0
    """
    if pct_1w is None:
        return 0.0
    if pct_1w <= -0.5:
        return min(1.0, -pct_1w / 1.0)
    if pct_1w >= 0.5:
        return max(-1.0, -pct_1w / 1.0)
    return 0.0


def _normalize_news_sentiment(avg_score: float | None) -> float:
    """뉴스 센티먼트 평균 → [-1, +1].

    > +0.2 → +1 방향, < -0.2 → -1 방향, -0.2 ~ +0.2 → 0.
    """
    if avg_score is None:
        return 0.0
    if avg_score > 0.2:
        return min(1.0, avg_score / 0.5)
    if avg_score < -0.2:
        return max(-1.0, avg_score / 0.5)
    return 0.0


# ---------------------------------------------------------------------------
# 엔진
# ---------------------------------------------------------------------------


class MarketRegimeEngine:
    """FRED + FX + 기술적 지표 + 뉴스 센티먼트를 종합해 레짐을 판단한다.

    각 factor 실패 시 0.0(중립)으로 fallback — 브리핑 파이프라인이 죽지 않는다.
    compute()가 None을 반환하면 브리핑에서 스탠드업 섹션을 생략한다.
    """

    def __init__(self) -> None:
        self._logger = get_logger("MarketRegimeEngine")
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """regime_sizing.yaml 로드."""
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def compute(self) -> RegimeResult | None:
        """레짐 판단 실행.

        Returns:
            RegimeResult 또는 None (전체 실패 시).
        """
        t0 = time.time()
        self._logger.info("regime_compute_start")

        try:
            # ----------------------------------------------------------------
            # 인풋 1: 기술적 점수 (watchlist TSLA/BTC/ETH 평균)
            # ----------------------------------------------------------------
            tech_score, tech_drivers = self._compute_technical_score()

            # ----------------------------------------------------------------
            # 인풋 2: FRED net_liquidity WoW 방향
            # ----------------------------------------------------------------
            fred_score, fred_driver = self._compute_fred_score()

            # ----------------------------------------------------------------
            # 인풋 3: DXY 5일 모멘텀
            # ----------------------------------------------------------------
            fx_score, fx_driver = self._compute_fx_score()

            # ----------------------------------------------------------------
            # 인풋 4: 뉴스 센티먼트 (DB 24h 평균)
            # ----------------------------------------------------------------
            sentiment_score, sentiment_driver = self._compute_sentiment_score()

            # ----------------------------------------------------------------
            # 가중 합산
            # ----------------------------------------------------------------
            weights = self._config["weights"]
            raw_score = (
                tech_score * weights["technical"]
                + fred_score * weights["fred_liquidity"]
                + fx_score * weights["fx"]
                + sentiment_score * weights["news_sentiment"]
            )

            # ----------------------------------------------------------------
            # 레짐 판단
            # ----------------------------------------------------------------
            thresholds = self._config["thresholds"]
            if raw_score > thresholds["risk_on"]:
                regime: Literal["RISK_ON", "NEUTRAL", "RISK_OFF"] = "RISK_ON"
            elif raw_score < thresholds["risk_off"]:
                regime = "RISK_OFF"
            else:
                regime = "NEUTRAL"

            # 신뢰도: |점수| / 최대 가능 점수(모든 factor +1일 때)
            max_possible = sum(weights.values())  # = 1.0
            confidence = round(min(1.0, abs(raw_score) / max_possible), 2)

            # 드라이버 (의미 있는 것 최대 3개)
            drivers: list[str] = []
            for d in tech_drivers + [fred_driver, fx_driver, sentiment_driver]:
                if d and len(drivers) < 3:
                    drivers.append(d)

            # 포지션 사이징 가이드
            sizing: dict[str, float] = self._config["positions"].get(regime, {})

            result = RegimeResult(
                regime=regime,
                confidence=confidence,
                drivers=drivers,
                sizing=dict(sizing),
                raw_score=round(raw_score, 3),
            )

            elapsed = round(time.time() - t0, 1)
            self._logger.info(
                "regime_compute_done",
                regime=regime,
                confidence=confidence,
                score=raw_score,
                elapsed_s=elapsed,
            )
            return result

        except Exception as exc:
            self._logger.error("regime_compute_failed", error=str(exc))
            return None

    # -----------------------------------------------------------------------
    # 기술적 점수 — TSLA/BTC/ETH 평균
    # -----------------------------------------------------------------------

    def _compute_technical_score(self) -> tuple[float, list[str]]:
        """watchlist 종목(regime_sizing.yaml positions 키)의 평균 기술적 점수.

        Returns:
            ([-1, +1] 정규화 점수, 드라이버 문장 리스트)
        """
        try:
            import pandas as pd
            import yfinance as yf

            from src.analyzers.trend import _adx, _supertrend
        except ImportError as exc:
            self._logger.warning("technical_import_failed", error=str(exc))
            return 0.0, []

        tickers = list(self._config["positions"]["RISK_ON"].keys())
        yf_tickers = [_resolve_ticker(t) for t in tickers]

        try:
            # 한 번에 묶어서 fetch (latency 절감)
            import pandas as pd
            raw = yf.download(
                yf_tickers,
                period=_OHLCV_PERIOD,
                auto_adjust=True,
                progress=False,
                timeout=10,
            )
            if raw.empty:
                return 0.0, []
        except Exception as exc:
            self._logger.warning("yfinance_fetch_failed", error=str(exc))
            return 0.0, []

        from src.analyzers.technical import TechnicalAnalyzer, _rsi, _macd
        from src.analyzers.trend import _adx, _supertrend

        scores: list[float] = []
        drivers: list[str] = []

        for orig_ticker, yf_ticker in zip(tickers, yf_tickers):
            try:
                # multi-ticker download: columns에 ticker 레벨 존재
                if len(yf_tickers) > 1:
                    import pandas as pd
                    try:
                        df = raw.xs(yf_ticker, axis=1, level=1).dropna()
                    except KeyError:
                        df = raw.xs(yf_ticker, axis=1, level=0).dropna()
                else:
                    df = raw.dropna()

                if len(df) < 30:
                    continue

                close = df["Close"]

                # RSI
                from src.analyzers.technical import _rsi
                rsi_series = _rsi(close, 14)
                rsi_val = float(rsi_series.dropna().iloc[-1]) if not rsi_series.dropna().empty else 50.0

                # MACD histogram
                from src.analyzers.technical import _macd
                macd_df = _macd(close)
                hist_val = float(macd_df["histogram"].dropna().iloc[-1]) if not macd_df["histogram"].dropna().empty else 0.0

                # ADX + direction
                from src.analyzers.trend import _adx, _supertrend
                if all(c in df.columns for c in ("High", "Low", "Close")):
                    adx_df = _adx(df)
                    adx_val = float(adx_df["ADX"].dropna().iloc[-1]) if not adx_df["ADX"].dropna().empty else 0.0
                    plus_di = float(adx_df["plus_di"].dropna().iloc[-1]) if not adx_df["plus_di"].dropna().empty else 0.0
                    minus_di = float(adx_df["minus_di"].dropna().iloc[-1]) if not adx_df["minus_di"].dropna().empty else 0.0
                    direction_bullish = plus_di > minus_di

                    # Supertrend
                    st_df = _supertrend(df)
                    st_dir = int(st_df["direction"].dropna().iloc[-1]) if not st_df["direction"].dropna().empty else 1
                    supertrend_bullish = st_dir == 1
                else:
                    adx_val = 0.0
                    direction_bullish = True
                    supertrend_bullish = True

                # 4개 지표 평균
                ticker_score = (
                    _normalize_rsi(rsi_val)
                    + _normalize_macd_histogram(hist_val)
                    + _normalize_adx(adx_val, direction_bullish)
                    + _normalize_supertrend(supertrend_bullish)
                ) / 4.0

                scores.append(ticker_score)

                # 드라이버: 가장 의미 있는 것 하나
                if adx_val >= 30:
                    state = "상승 추세" if direction_bullish else "하락 추세"
                    drivers.append(
                        f"{orig_ticker} — ADX {adx_val:.0f} ({state}), RSI {rsi_val:.0f}"
                    )
                elif abs(hist_val) > 0.05:
                    direction = "상향" if hist_val > 0 else "하향"
                    drivers.append(
                        f"{orig_ticker} — MACD 히스토그램 {direction} ({hist_val:+.3f})"
                    )

            except Exception as exc:
                self._logger.warning(
                    "technical_ticker_failed", ticker=yf_ticker, error=str(exc)
                )

        if not scores:
            return 0.0, []

        avg_score = sum(scores) / len(scores)
        return round(avg_score, 3), drivers

    # -----------------------------------------------------------------------
    # FRED 유동성 점수
    # -----------------------------------------------------------------------

    def _compute_fred_score(self) -> tuple[float, str]:
        """FRED net_liquidity WoW 방향 → [-1, +1].

        Returns:
            (점수, 드라이버 문장)
        """
        try:
            from src.collectors.macro.fred_collector import FredCollector

            data = FredCollector().collect()
            wow = data.get("net_liquidity_wow")
            score = _normalize_fred_liquidity(wow)

            if wow is None:
                driver = ""
            elif wow > 0:
                driver = f"FRED net_liquidity 증가 방향 (+{wow:.1f}B WoW)"
            else:
                driver = f"FRED net_liquidity 감소 방향 ({wow:.1f}B WoW)"

            return score, driver

        except Exception as exc:
            self._logger.warning("fred_collect_failed", error=str(exc))
            return 0.0, ""

    # -----------------------------------------------------------------------
    # FX (DXY) 점수
    # -----------------------------------------------------------------------

    def _compute_fx_score(self) -> tuple[float, str]:
        """DXY 1주 모멘텀 → [-1, +1].

        Returns:
            (점수, 드라이버 문장)
        """
        try:
            from src.collectors.macro.fx_collector import FxCollector

            data = FxCollector().collect()
            pct_1w = data.get("currencies", {}).get("DXY", {}).get("pct_1w")
            score = _normalize_dxy(pct_1w)

            if pct_1w is None:
                driver = ""
            elif pct_1w >= 0.5:
                driver = f"DXY {pct_1w:+.1f}% (달러 강세, 위험자산 역풍)"
            elif pct_1w <= -0.5:
                driver = f"DXY {pct_1w:+.1f}% (달러 약세, 위험자산 순풍)"
            else:
                driver = f"DXY {pct_1w:+.1f}% (중립 구간)"

            return score, driver

        except Exception as exc:
            self._logger.warning("fx_collect_failed", error=str(exc))
            return 0.0, ""

    # -----------------------------------------------------------------------
    # 뉴스 센티먼트 점수
    # -----------------------------------------------------------------------

    def _compute_sentiment_score(self) -> tuple[float, str]:
        """DB news_items.sentiment_score 최근 24h 평균 → [-1, +1].

        Returns:
            (점수, 드라이버 문장)
        """
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=_LOOKBACK_HOURS)

            with get_session() as session:
                stmt = (
                    select(func.avg(NewsItemDB.sentiment_score))
                    .where(NewsItemDB.created_at >= cutoff)
                )
                avg_sentiment: float | None = session.execute(stmt).scalar()

            score = _normalize_news_sentiment(avg_sentiment)

            if avg_sentiment is None:
                driver = ""
            else:
                driver = f"뉴스 센티먼트 {avg_sentiment:+.2f} (DB 24h 평균)"

            return score, driver

        except Exception as exc:
            self._logger.warning("sentiment_query_failed", error=str(exc))
            return 0.0, ""
