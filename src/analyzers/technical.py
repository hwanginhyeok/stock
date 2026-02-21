"""Technical analysis using pure pandas indicator calculations."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.analyzers.base import BaseAnalyzer
from src.core.config import TechnicalConfig
from src.core.exceptions import AnalysisError


# ============================================================
# Pure-pandas indicator functions (no pandas-ta dependency)
# ============================================================


def _sma(series: pd.Series, length: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=length, min_periods=length).mean()


def _ema(series: pd.Series, length: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=length, adjust=False).mean()


def _rsi(series: pd.Series, length: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """MACD (line, histogram, signal)."""
    ema_fast = _ema(series, fast)
    ema_slow = _ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = _ema(macd_line, signal)
    histogram = macd_line - signal_line
    return pd.DataFrame({
        "macd": macd_line,
        "histogram": histogram,
        "signal": signal_line,
    })


def _bbands(
    series: pd.Series,
    length: int = 20,
    std_dev: int = 2,
) -> pd.DataFrame:
    """Bollinger Bands (lower, mid, upper)."""
    mid = _sma(series, length)
    rolling_std = series.rolling(window=length, min_periods=length).std()
    upper = mid + std_dev * rolling_std
    lower = mid - std_dev * rolling_std
    return pd.DataFrame({"lower": lower, "mid": mid, "upper": upper})


class TechnicalAnalyzer(BaseAnalyzer):
    """Compute technical indicators and generate a composite score.

    Indicators:
        SMA (5, 20, 60, 120), EMA (12, 26), RSI (14),
        MACD (12, 26, 9), Bollinger Bands (20, 2).

    Score breakdown (0-100):
        RSI (25) + MACD (25) + Moving average trend (25) + Bollinger position (25).
    """

    def __init__(self) -> None:
        super().__init__()
        self._tech_config: TechnicalConfig = self._config.market.technical

    def analyze(self, ticker: str, **kwargs: Any) -> dict[str, Any]:
        """Run technical analysis on OHLCV data.

        Args:
            ticker: Stock ticker symbol.
            **kwargs: Must include ``ohlcv`` key with a pandas DataFrame
                containing at least [Close, Volume] columns.

        Returns:
            Dict with keys: score, signals, indicators, raw.

        Raises:
            AnalysisError: If OHLCV data is missing or insufficient.
        """
        ohlcv: pd.DataFrame | None = kwargs.get("ohlcv")
        if ohlcv is None or ohlcv.empty:
            raise AnalysisError(
                f"No OHLCV data for {ticker}",
                {"ticker": ticker},
            )

        if len(ohlcv) < 30:
            self._logger.warning(
                "insufficient_data",
                ticker=ticker,
                rows=len(ohlcv),
            )
            return {
                "score": 50.0,
                "signals": ["insufficient_data"],
                "indicators": {},
                "raw": {},
            }

        indicators = self._compute_indicators(ohlcv)
        signals = self._detect_signals(ohlcv, indicators)
        score = self._compute_score(ohlcv, indicators)

        self._logger.debug(
            "technical_analysis_complete",
            ticker=ticker,
            score=score,
            signal_count=len(signals),
        )

        return {
            "score": score,
            "signals": signals,
            "indicators": indicators,
            "raw": {
                "close": float(ohlcv["Close"].iloc[-1]),
                "volume": int(ohlcv["Volume"].iloc[-1]) if "Volume" in ohlcv.columns else 0,
                "data_points": len(ohlcv),
            },
        }

    # ------------------------------------------------------------------
    # Indicator computation
    # ------------------------------------------------------------------

    def _compute_indicators(self, df: pd.DataFrame) -> dict[str, Any]:
        """Compute all technical indicators.

        Args:
            df: OHLCV DataFrame.

        Returns:
            Dict of indicator name -> latest value.
        """
        close = df["Close"]
        result: dict[str, Any] = {}

        # SMA
        for period in self._tech_config.sma_periods:
            sma = _sma(close, period)
            result[f"sma_{period}"] = self._last_value(sma)

        # EMA
        for period in self._tech_config.ema_periods:
            ema = _ema(close, period)
            result[f"ema_{period}"] = self._last_value(ema)

        # RSI
        rsi = _rsi(close, self._tech_config.rsi_period)
        result["rsi"] = self._last_value(rsi)

        # MACD
        macd_cfg = self._tech_config.macd
        macd_df = _macd(close, fast=macd_cfg.fast, slow=macd_cfg.slow, signal=macd_cfg.signal)
        result["macd"] = self._last_value(macd_df["macd"])
        result["macd_histogram"] = self._last_value(macd_df["histogram"])
        result["macd_signal"] = self._last_value(macd_df["signal"])

        # Bollinger Bands
        bb_cfg = self._tech_config.bollinger
        bb_df = _bbands(close, length=bb_cfg.period, std_dev=bb_cfg.std_dev)
        result["bb_lower"] = self._last_value(bb_df["lower"])
        result["bb_mid"] = self._last_value(bb_df["mid"])
        result["bb_upper"] = self._last_value(bb_df["upper"])

        return result

    # ------------------------------------------------------------------
    # Signal detection
    # ------------------------------------------------------------------

    def _detect_signals(
        self,
        df: pd.DataFrame,
        indicators: dict[str, Any],
    ) -> list[str]:
        """Detect trading signals from indicators.

        Args:
            df: OHLCV DataFrame.
            indicators: Computed indicator values.

        Returns:
            List of signal description strings.
        """
        signals: list[str] = []
        close = float(df["Close"].iloc[-1])

        # RSI overbought / oversold
        rsi = indicators.get("rsi")
        if rsi is not None:
            if rsi >= self._tech_config.rsi_overbought:
                signals.append(f"RSI overbought ({rsi:.1f})")
            elif rsi <= self._tech_config.rsi_oversold:
                signals.append(f"RSI oversold ({rsi:.1f})")

        # MACD cross
        macd = indicators.get("macd")
        macd_signal = indicators.get("macd_signal")
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                signals.append("MACD bullish cross")
            elif macd < macd_signal:
                signals.append("MACD bearish cross")

        # Golden / Death cross
        for short_p, long_p in self._tech_config.golden_cross_pairs:
            sma_short = indicators.get(f"sma_{short_p}")
            sma_long = indicators.get(f"sma_{long_p}")
            if sma_short is not None and sma_long is not None:
                prev_short = self._prev_sma_value(df, short_p)
                prev_long = self._prev_sma_value(df, long_p)
                if prev_short is not None and prev_long is not None:
                    if prev_short <= prev_long and sma_short > sma_long:
                        signals.append(f"Golden cross (SMA{short_p}/SMA{long_p})")
                    elif prev_short >= prev_long and sma_short < sma_long:
                        signals.append(f"Death cross (SMA{short_p}/SMA{long_p})")

        # Bollinger Band breakout
        bb_upper = indicators.get("bb_upper")
        bb_lower = indicators.get("bb_lower")
        if bb_upper is not None and close > bb_upper:
            signals.append("Bollinger upper breakout")
        if bb_lower is not None and close < bb_lower:
            signals.append("Bollinger lower breakout")

        return signals

    # ------------------------------------------------------------------
    # Score computation
    # ------------------------------------------------------------------

    def _compute_score(
        self,
        df: pd.DataFrame,
        indicators: dict[str, Any],
    ) -> float:
        """Compute a 0-100 composite technical score.

        Breakdown:
            RSI component (25): centered on 50, penalizes extremes.
            MACD component (25): histogram direction.
            MA trend (25): price vs. SMA alignment.
            Bollinger position (25): relative band position.

        Args:
            df: OHLCV DataFrame.
            indicators: Computed indicator values.

        Returns:
            Float score between 0 and 100.
        """
        close = float(df["Close"].iloc[-1])

        # --- RSI component (25 points) ---
        rsi = indicators.get("rsi", 50.0)
        if rsi <= 30:
            rsi_score = 25.0  # Oversold = bullish opportunity
        elif rsi >= 70:
            rsi_score = 5.0  # Overbought = risky
        else:
            rsi_score = 25.0 - (rsi - 30) * (20 / 40)

        # --- MACD component (25 points) ---
        macd_hist = indicators.get("macd_histogram", 0.0)
        if macd_hist is None:
            macd_hist = 0.0
        if macd_hist > 0:
            macd_score = min(25.0, 12.5 + macd_hist * 50)
        else:
            macd_score = max(0.0, 12.5 + macd_hist * 50)

        # --- Moving average trend (25 points) ---
        ma_score = 12.5
        for period in self._tech_config.sma_periods:
            sma_val = indicators.get(f"sma_{period}")
            if sma_val is not None and sma_val > 0:
                if close / sma_val > 1.0:
                    ma_score += 3.0
                else:
                    ma_score -= 3.0
        ma_score = max(0.0, min(25.0, ma_score))

        # --- Bollinger position (25 points) ---
        bb_upper = indicators.get("bb_upper")
        bb_lower = indicators.get("bb_lower")
        if bb_upper and bb_lower and bb_upper > bb_lower:
            bb_range = bb_upper - bb_lower
            position = (close - bb_lower) / bb_range
            bb_score = (1.0 - position) * 20.0 + 2.5
            bb_score = max(0.0, min(25.0, bb_score))
        else:
            bb_score = 12.5

        total = rsi_score + macd_score + ma_score + bb_score
        return round(max(0.0, min(100.0, total)), 1)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _last_value(series: pd.Series) -> float | None:
        """Get the last non-NaN value from a Series."""
        valid = series.dropna()
        if valid.empty:
            return None
        return round(float(valid.iloc[-1]), 4)

    @staticmethod
    def _prev_sma_value(df: pd.DataFrame, period: int) -> float | None:
        """Get the second-to-last SMA value for crossover detection."""
        sma = _sma(df["Close"], period)
        valid = sma.dropna()
        if len(valid) < 2:
            return None
        return float(valid.iloc[-2])
