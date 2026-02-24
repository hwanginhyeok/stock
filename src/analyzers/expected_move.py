"""Expected move analysis using options-implied volatility."""

from __future__ import annotations

import math
from typing import Any

from src.analyzers.base import BaseAnalyzer


def _iv_to_expected_move(
    price: float,
    iv: float,
    days: int,
) -> float:
    """Convert annualized IV to expected move for a given period.

    Args:
        price: Current stock price.
        iv: Annualized implied volatility (decimal, e.g., 0.25 = 25%).
        days: Number of calendar days.

    Returns:
        Expected move in price units (1σ).
    """
    return price * iv * math.sqrt(days / 365)


def _classify_expected_move(move_pct: float) -> str:
    """Classify the expected move magnitude.

    Args:
        move_pct: Expected move as % of current price.

    Returns:
        Classification label.
    """
    if move_pct >= 10:
        return "Extreme"
    if move_pct >= 5:
        return "Very High"
    if move_pct >= 3:
        return "High"
    if move_pct >= 1.5:
        return "Moderate"
    return "Low"


class ExpectedMoveAnalyzer(BaseAnalyzer):
    """Analyze options-implied expected moves and sigma price ranges.

    Takes raw options IV data from OptionsIVCollector and produces
    actionable analysis: support/resistance levels from sigma bands,
    IV regime classification, and cross-ticker comparison.
    """

    def analyze(self, ticker: str, **kwargs: Any) -> dict[str, Any]:
        """Analyze expected move for a single ticker.

        Args:
            ticker: Stock ticker symbol.
            **kwargs: Must include ``options_data`` (dict from OptionsIVCollector).

        Returns:
            Dict with expected move analysis, sigma levels, and signals.
        """
        options_data: dict[str, Any] = kwargs.get("options_data", {})

        if not options_data or "error" in options_data:
            return {
                "ticker": ticker,
                "status": "no_data",
                "error": options_data.get("error", "No options data provided"),
            }

        current_price = options_data["current_price"]
        expected_moves = options_data.get("expected_moves", [])

        if not expected_moves:
            return {
                "ticker": ticker,
                "status": "no_chains",
                "current_price": current_price,
            }

        # Primary analysis uses nearest expiration
        primary = expected_moves[0]
        analysis = self._analyze_single_expiry(ticker, current_price, primary)

        # Multi-expiry term structure analysis
        if len(expected_moves) >= 2:
            term_structure = self._analyze_term_structure(expected_moves)
            analysis["term_structure"] = term_structure

        # Add IV context from collector
        analysis["iv_rank"] = options_data.get("iv_rank")
        analysis["iv_level"] = options_data.get("iv_level")
        analysis["skew_sentiment"] = options_data.get("skew_sentiment")

        # Generate trading signals
        analysis["signals"] = self._generate_signals(analysis)

        return analysis

    def _analyze_single_expiry(
        self,
        ticker: str,
        current_price: float,
        expiry_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze expected move for a single expiration.

        Args:
            ticker: Stock ticker.
            current_price: Current stock price.
            expiry_data: Single expiration data from OptionsIVCollector.

        Returns:
            Analysis dict with sigma bands and classification.
        """
        atm_iv = expiry_data["atm_iv"]
        dte = expiry_data["dte"]
        sigma_1 = expiry_data["sigma_1"]
        sigma_2 = expiry_data["sigma_2"]
        move_pct = expiry_data["expected_move_pct"]

        # Additional sigma levels (0.5σ and 1.5σ for finer granularity)
        half_sigma = round(expiry_data["expected_move"] / 2, 2)
        sigma_1_5 = round(expiry_data["expected_move"] * 1.5, 2)

        return {
            "ticker": ticker,
            "status": "ok",
            "current_price": current_price,
            "expiration": expiry_data["expiration"],
            "dte": dte,
            "atm_iv": atm_iv,
            "atm_iv_pct": expiry_data["atm_iv_pct"],
            "expected_move": expiry_data["expected_move"],
            "expected_move_pct": move_pct,
            "move_magnitude": _classify_expected_move(move_pct),
            "price_ranges": {
                "sigma_0_5": {
                    "upper": round(current_price + half_sigma, 2),
                    "lower": round(current_price - half_sigma, 2),
                    "probability": 38.3,
                    "label": "Likely range",
                },
                "sigma_1": {
                    **sigma_1,
                    "label": "Expected range",
                },
                "sigma_1_5": {
                    "upper": round(current_price + sigma_1_5, 2),
                    "lower": round(current_price - sigma_1_5, 2),
                    "probability": 86.6,
                    "label": "Extended range",
                },
                "sigma_2": {
                    **sigma_2,
                    "label": "Extreme range",
                },
            },
            "iv_skew": expiry_data.get("iv_skew", {}),
            "oi_pc_ratio": expiry_data.get("oi_pc_ratio"),
            "volume_pc_ratio": expiry_data.get("volume_pc_ratio"),
        }

    def _analyze_term_structure(
        self,
        expected_moves: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Analyze IV term structure across expirations.

        Normal: longer expiry has higher IV (contango).
        Inverted: near-term IV > far-term IV (backwardation) = stress signal.

        Args:
            expected_moves: List of expiry data sorted by DTE ascending.

        Returns:
            Term structure analysis dict.
        """
        ivs = [
            (em["dte"], em["atm_iv"])
            for em in expected_moves
            if em.get("atm_iv") is not None
        ]

        if len(ivs) < 2:
            return {"shape": "insufficient_data", "entries": []}

        # Check if term structure is normal (contango) or inverted
        near_iv = ivs[0][1]
        far_iv = ivs[-1][1]

        if far_iv > 0:
            ratio = near_iv / far_iv
        else:
            ratio = 1.0

        if ratio > 1.10:
            shape = "Inverted (Backwardation)"
            interpretation = "단기 IV가 장기보다 높음 — 근기 이벤트/스트레스 신호"
        elif ratio < 0.90:
            shape = "Steep Contango"
            interpretation = "장기 불확실성이 높음 — 시장이 먼 미래 리스크를 가격에 반영"
        else:
            shape = "Normal (Flat)"
            interpretation = "IV 기간 구조가 정상적 — 특별한 이벤트 감지 없음"

        entries = [
            {
                "dte": dte,
                "iv": round(iv, 4),
                "iv_pct": round(iv * 100, 2),
            }
            for dte, iv in ivs
        ]

        return {
            "shape": shape,
            "interpretation": interpretation,
            "near_far_ratio": round(ratio, 3),
            "entries": entries,
        }

    def _generate_signals(
        self,
        analysis: dict[str, Any],
    ) -> list[dict[str, str]]:
        """Generate actionable signals from expected move analysis.

        Args:
            analysis: Full analysis dict.

        Returns:
            List of signal dicts with type, message, and severity.
        """
        signals: list[dict[str, str]] = []

        # IV rank signal
        iv_rank = analysis.get("iv_rank")
        if iv_rank is not None:
            if iv_rank >= 80:
                signals.append({
                    "type": "iv_high",
                    "message": f"IV Rank {iv_rank}% — 옵션 프리미엄이 역사적 고점 근처. 변동성 매도(short vol) 전략 고려",
                    "severity": "warning",
                })
            elif iv_rank <= 20:
                signals.append({
                    "type": "iv_low",
                    "message": f"IV Rank {iv_rank}% — 옵션이 저렴. 변동성 매수(long vol) 전략 고려",
                    "severity": "info",
                })

        # Skew signal
        skew_sentiment = analysis.get("skew_sentiment", "Neutral")
        if "Fear" in skew_sentiment:
            signals.append({
                "type": "skew_fear",
                "message": f"풋 스큐 확대 — {skew_sentiment}. 하방 헤지 수요 증가",
                "severity": "warning",
            })

        # Term structure signal
        term = analysis.get("term_structure", {})
        if term.get("shape", "").startswith("Inverted"):
            signals.append({
                "type": "term_inverted",
                "message": "IV 기간 구조 역전 — 단기 불확실성이 장기보다 높음 (이벤트 리스크)",
                "severity": "alert",
            })

        # Move magnitude
        move_magnitude = analysis.get("move_magnitude")
        if move_magnitude in ("Extreme", "Very High"):
            signals.append({
                "type": "high_expected_move",
                "message": f"예상 변동 {analysis.get('expected_move_pct', 0):.1f}% — {move_magnitude} 변동성 구간",
                "severity": "warning",
            })

        # P/C ratio from options chain
        oi_pc = analysis.get("oi_pc_ratio")
        if oi_pc is not None:
            if oi_pc >= 1.5:
                signals.append({
                    "type": "put_heavy",
                    "message": f"옵션 OI P/C = {oi_pc:.2f} — 풋 옵션 비중 과다 (공포/헤지)",
                    "severity": "info",
                })
            elif oi_pc <= 0.5:
                signals.append({
                    "type": "call_heavy",
                    "message": f"옵션 OI P/C = {oi_pc:.2f} — 콜 옵션 비중 과다 (낙관/투기)",
                    "severity": "info",
                })

        return signals

    def analyze_batch(
        self,
        options_data_list: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Analyze expected moves for multiple tickers and rank by IV.

        Args:
            options_data_list: List of OptionsIVCollector results.

        Returns:
            Dict with per-ticker analysis and cross-ticker summary.
        """
        analyses: list[dict[str, Any]] = []

        for data in options_data_list:
            ticker = data.get("ticker", "UNKNOWN")
            result = self.analyze(ticker, options_data=data)
            analyses.append(result)

        # Sort by IV (highest first) for quick overview
        valid = [a for a in analyses if a.get("status") == "ok"]
        valid.sort(key=lambda x: x.get("atm_iv", 0) or 0, reverse=True)

        # Summary statistics
        ivs = [a["atm_iv"] for a in valid if a.get("atm_iv")]
        avg_iv = sum(ivs) / len(ivs) if ivs else 0
        high_vol_count = sum(1 for a in valid if a.get("move_magnitude") in ("Extreme", "Very High", "High"))

        summary = {
            "total_tickers": len(analyses),
            "analyzed": len(valid),
            "avg_iv_pct": round(avg_iv * 100, 2),
            "high_volatility_count": high_vol_count,
            "highest_iv_ticker": valid[0]["ticker"] if valid else None,
            "lowest_iv_ticker": valid[-1]["ticker"] if valid else None,
        }

        self._logger.info(
            "batch_expected_move_complete",
            count=len(valid),
            avg_iv=summary["avg_iv_pct"],
            high_vol=high_vol_count,
        )

        return {
            "summary": summary,
            "analyses": analyses,
        }
