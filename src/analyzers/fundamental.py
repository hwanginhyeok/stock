"""Fundamental analysis using yfinance company data."""

from __future__ import annotations

from typing import Any

import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

from src.analyzers.base import BaseAnalyzer
from src.core.config import FundamentalConfig
from src.core.exceptions import AnalysisError
from src.core.models import Market


class FundamentalAnalyzer(BaseAnalyzer):
    """Compute fundamental metrics and generate a composite score.

    Metrics:
        PER, PBR, ROE, operating margin, revenue growth, earnings growth.

    Score breakdown (0-100):
        Valuation (33) + Profitability (33) + Growth (34).
    """

    def __init__(self) -> None:
        super().__init__()
        self._fund_config: FundamentalConfig = self._config.market.fundamental

    def analyze(self, ticker: str, **kwargs: Any) -> dict[str, Any]:
        """Run fundamental analysis on a stock.

        Args:
            ticker: Stock ticker symbol.
            **kwargs: Optional ``market`` (Market enum) for Korean ticker
                suffix mapping.

        Returns:
            Dict with keys: score, data, metrics.

        Raises:
            AnalysisError: If yfinance data cannot be fetched.
        """
        market: Market = kwargs.get("market", Market.US)
        yf_ticker = self._resolve_yf_ticker(ticker, market)

        info = self._fetch_info(yf_ticker)
        if not info:
            self._logger.warning("no_fundamental_data", ticker=ticker)
            return {
                "score": 50.0,
                "data": {},
                "metrics": {"error": "no_data"},
            }

        metrics = self._extract_metrics(info)
        score = self._compute_score(metrics)

        self._logger.debug(
            "fundamental_analysis_complete",
            ticker=ticker,
            score=score,
        )

        return {
            "score": score,
            "data": metrics,
            "metrics": {
                "per": metrics.get("per"),
                "pbr": metrics.get("pbr"),
                "roe": metrics.get("roe"),
                "operating_margin": metrics.get("operating_margin"),
                "revenue_growth": metrics.get("revenue_growth"),
                "earnings_growth": metrics.get("earnings_growth"),
            },
        }

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=15),
        reraise=True,
    )
    def _fetch_info(self, yf_ticker: str) -> dict[str, Any]:
        """Fetch company info from yfinance with retry.

        Args:
            yf_ticker: yfinance-compatible ticker string.

        Returns:
            yfinance info dict.
        """
        try:
            ticker_obj = yf.Ticker(yf_ticker)
            info = ticker_obj.info
            return info if info else {}
        except Exception as e:
            self._logger.warning(
                "yfinance_fetch_failed",
                ticker=yf_ticker,
                error=str(e),
            )
            return {}

    @staticmethod
    def _resolve_yf_ticker(ticker: str, market: Market) -> str:
        """Add .KS/.KQ suffix for Korean tickers.

        Args:
            ticker: Raw ticker symbol.
            market: Market enum.

        Returns:
            yfinance-compatible ticker string.
        """
        if market == Market.US:
            return ticker

        # Korean tickers: try .KS (KOSPI) first as default
        # Pure numeric tickers are assumed Korean
        if ticker.isdigit():
            return f"{ticker}.KS"
        return ticker

    # ------------------------------------------------------------------
    # Metric extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_metrics(info: dict[str, Any]) -> dict[str, float | None]:
        """Extract fundamental metrics from yfinance info.

        Args:
            info: yfinance Ticker.info dict.

        Returns:
            Dict of metric name -> value (None if unavailable).
        """

        def _safe_float(key: str) -> float | None:
            val = info.get(key)
            if val is None:
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        return {
            "per": _safe_float("trailingPE") or _safe_float("forwardPE"),
            "pbr": _safe_float("priceToBook"),
            "psr": _safe_float("priceToSalesTrailing12Months"),
            "roe": _safe_float("returnOnEquity"),
            "roa": _safe_float("returnOnAssets"),
            "operating_margin": _safe_float("operatingMargins"),
            "revenue_growth": _safe_float("revenueGrowth"),
            "earnings_growth": _safe_float("earningsGrowth"),
            "market_cap": _safe_float("marketCap"),
            "dividend_yield": _safe_float("dividendYield"),
        }

    # ------------------------------------------------------------------
    # Score computation
    # ------------------------------------------------------------------

    def _compute_score(self, metrics: dict[str, float | None]) -> float:
        """Compute a 0-100 composite fundamental score.

        Breakdown:
            Valuation (33): PER + PBR.
            Profitability (33): ROE + Operating margin.
            Growth (34): Revenue growth + Earnings growth.

        Args:
            metrics: Extracted fundamental metrics.

        Returns:
            Float score between 0 and 100.
        """
        val_score = self._valuation_score(metrics)
        prof_score = self._profitability_score(metrics)
        growth_score = self._growth_score(metrics)

        total = val_score + prof_score + growth_score
        return round(max(0.0, min(100.0, total)), 1)

    def _valuation_score(self, metrics: dict[str, float | None]) -> float:
        """Score valuation metrics (max 33 points).

        Lower PER/PBR relative to thresholds = higher score.
        """
        score = 16.5  # Neutral
        thresholds = self._fund_config.valuation

        per = metrics.get("per")
        if per is not None and per > 0:
            if per <= thresholds.per_max * 0.5:
                score += 8.25  # Very cheap
            elif per <= thresholds.per_max:
                ratio = per / thresholds.per_max
                score += 8.25 * (1 - ratio)
            else:
                score -= 8.25  # Expensive

        pbr = metrics.get("pbr")
        if pbr is not None and pbr > 0:
            if pbr <= thresholds.pbr_max * 0.5:
                score += 8.25
            elif pbr <= thresholds.pbr_max:
                ratio = pbr / thresholds.pbr_max
                score += 8.25 * (1 - ratio)
            else:
                score -= 8.25

        return max(0.0, min(33.0, score))

    def _profitability_score(self, metrics: dict[str, float | None]) -> float:
        """Score profitability metrics (max 33 points).

        Higher ROE and operating margin = higher score.
        """
        score = 16.5
        thresholds = self._fund_config.profitability

        roe = metrics.get("roe")
        if roe is not None:
            # yfinance returns as ratio (0.15 = 15%)
            roe_pct = roe * 100 if abs(roe) < 1 else roe
            if roe_pct >= thresholds.roe_min:
                score += min(8.25, (roe_pct - thresholds.roe_min) * 0.5)
            else:
                score -= min(8.25, (thresholds.roe_min - roe_pct) * 0.5)

        margin = metrics.get("operating_margin")
        if margin is not None:
            margin_pct = margin * 100 if abs(margin) < 1 else margin
            if margin_pct >= thresholds.operating_margin_min:
                score += min(8.25, (margin_pct - thresholds.operating_margin_min) * 0.3)
            else:
                score -= min(8.25, (thresholds.operating_margin_min - margin_pct) * 0.3)

        return max(0.0, min(33.0, score))

    def _growth_score(self, metrics: dict[str, float | None]) -> float:
        """Score growth metrics (max 34 points).

        Higher revenue/earnings growth = higher score.
        """
        score = 17.0
        thresholds = self._fund_config.growth

        rev_growth = metrics.get("revenue_growth")
        if rev_growth is not None:
            rev_pct = rev_growth * 100 if abs(rev_growth) < 1 else rev_growth
            if rev_pct >= thresholds.revenue_growth_min:
                score += min(8.5, (rev_pct - thresholds.revenue_growth_min) * 0.4)
            else:
                score -= min(8.5, (thresholds.revenue_growth_min - rev_pct) * 0.4)

        earn_growth = metrics.get("earnings_growth")
        if earn_growth is not None:
            earn_pct = earn_growth * 100 if abs(earn_growth) < 1 else earn_growth
            if earn_pct >= thresholds.earnings_growth_min:
                score += min(8.5, (earn_pct - thresholds.earnings_growth_min) * 0.3)
            else:
                score -= min(8.5, (thresholds.earnings_growth_min - earn_pct) * 0.3)

        return max(0.0, min(34.0, score))
