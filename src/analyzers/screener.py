"""Stock screener combining technical and fundamental analysis."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from src.analyzers.base import BaseAnalyzer
from src.analyzers.fundamental import FundamentalAnalyzer
from src.analyzers.technical import TechnicalAnalyzer
from src.core.config import ScreeningConfig
from src.core.models import Market, StockAnalysis
from src.storage import StockAnalysisRepository


class StockScreener(BaseAnalyzer):
    """Screen stocks using a composite technical + fundamental score.

    Composite score = tech_score * weight_tech + fund_score * weight_fund.

    Recommendation thresholds:
        >= 80: strong_positive
        >= 60: positive
        >= 40: neutral
        < 40: negative
    """

    def __init__(self) -> None:
        super().__init__()
        self._screening: ScreeningConfig = self._config.market.screening
        self._technical = TechnicalAnalyzer()
        self._fundamental = FundamentalAnalyzer()
        self._repo = StockAnalysisRepository()

    def analyze(self, ticker: str, **kwargs: Any) -> dict[str, Any]:
        """Analyze a single ticker with combined scoring.

        Args:
            ticker: Stock ticker symbol.
            **kwargs: Must include ``ohlcv`` (DataFrame) and
                optionally ``market`` (Market enum).

        Returns:
            Dict with score, tech_score, fund_score, signals, recommendation.
        """
        ohlcv: pd.DataFrame | None = kwargs.get("ohlcv")
        market: Market = kwargs.get("market", Market.US)

        tech_result = self._safe_technical(ticker, ohlcv)
        fund_result = self._safe_fundamental(ticker, market)

        tech_score = tech_result.get("score", 50.0)
        fund_score = fund_result.get("score", 50.0)

        weights = self._screening.weights
        composite = (
            tech_score * weights.get("technical", 0.5)
            + fund_score * weights.get("fundamental", 0.5)
        )
        composite = round(max(0.0, min(100.0, composite)), 1)

        recommendation = self._classify_recommendation(composite)
        signals = tech_result.get("signals", [])

        return {
            "score": composite,
            "technical_score": tech_score,
            "fundamental_score": fund_score,
            "signals": signals,
            "recommendation": recommendation,
            "technical_indicators": tech_result.get("indicators", {}),
            "fundamental_data": fund_result.get("data", {}),
        }

    def screen_watchlist(
        self,
        ohlcv_data: dict[str, pd.DataFrame],
        market: Market,
    ) -> list[StockAnalysis]:
        """Screen all watchlist stocks and return StockAnalysis models.

        Args:
            ohlcv_data: Dict mapping ticker -> OHLCV DataFrame.
            market: Market enum for the watchlist.

        Returns:
            List of StockAnalysis sorted by composite_score descending.
        """
        watchlist = (
            self._config.market.korea.watchlist
            if market == Market.KOREA
            else self._config.market.us.watchlist
        )

        analyses: list[StockAnalysis] = []
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for item in watchlist:
            ohlcv = ohlcv_data.get(item.ticker)
            if ohlcv is None or ohlcv.empty:
                self._logger.debug("skipping_no_ohlcv", ticker=item.ticker)
                continue

            result = self.analyze(item.ticker, ohlcv=ohlcv, market=market)

            analysis = StockAnalysis(
                ticker=item.ticker,
                name=item.name,
                market=market,
                date=today,
                technical_score=result["technical_score"],
                fundamental_score=result["fundamental_score"],
                composite_score=result["score"],
                signals=result["signals"],
                technical_indicators=result["technical_indicators"],
                fundamental_data=result["fundamental_data"],
                recommendation=result["recommendation"],
            )
            analyses.append(analysis)

        # Sort by composite score descending, limit to top_n
        analyses.sort(key=lambda a: a.composite_score, reverse=True)
        analyses = analyses[: self._screening.top_n]

        self._logger.info(
            "watchlist_screened",
            market=market.value,
            count=len(analyses),
        )
        return analyses

    def screen_and_store(
        self,
        ohlcv_data: dict[str, pd.DataFrame],
        market: Market,
    ) -> list[StockAnalysis]:
        """Screen watchlist and persist results to DB.

        Args:
            ohlcv_data: Dict mapping ticker -> OHLCV DataFrame.
            market: Market enum.

        Returns:
            List of persisted StockAnalysis.
        """
        analyses = self.screen_watchlist(ohlcv_data, market)
        if not analyses:
            self._logger.info("no_analyses_to_store")
            return []
        stored = self._repo.create_many(analyses)
        self._logger.info("analyses_stored", count=len(stored))
        return stored

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _safe_technical(
        self,
        ticker: str,
        ohlcv: pd.DataFrame | None,
    ) -> dict[str, Any]:
        """Run technical analysis with error handling."""
        if ohlcv is None or ohlcv.empty:
            return {"score": 50.0, "signals": [], "indicators": {}}
        try:
            return self._technical.analyze(ticker, ohlcv=ohlcv)
        except Exception as e:
            self._logger.warning(
                "technical_analysis_error",
                ticker=ticker,
                error=str(e),
            )
            return {"score": 50.0, "signals": [], "indicators": {}}

    def _safe_fundamental(
        self,
        ticker: str,
        market: Market,
    ) -> dict[str, Any]:
        """Run fundamental analysis with error handling."""
        try:
            return self._fundamental.analyze(ticker, market=market)
        except Exception as e:
            self._logger.warning(
                "fundamental_analysis_error",
                ticker=ticker,
                error=str(e),
            )
            return {"score": 50.0, "data": {}}

    @staticmethod
    def _classify_recommendation(score: float) -> str:
        """Convert composite score to a recommendation string.

        Args:
            score: Composite score (0-100).

        Returns:
            Recommendation string.
        """
        if score >= 80:
            return "strong_positive"
        if score >= 60:
            return "positive"
        if score >= 40:
            return "neutral"
        return "negative"
