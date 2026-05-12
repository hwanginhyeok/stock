"""Options chain Implied Volatility collector using yfinance."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

from src.collectors.sentiment.base import BaseSentimentCollector


def _find_atm_iv(
    chain: pd.DataFrame,
    current_price: float,
) -> dict[str, float | None]:
    """Find ATM (at-the-money) implied volatility from an options chain.

    Selects the strike closest to the current price and extracts IV.

    Args:
        chain: Options chain DataFrame (calls or puts) from yfinance.
        current_price: Current stock/index price.

    Returns:
        Dict with strike, impliedVolatility, volume, openInterest.
    """
    if chain.empty or "strike" not in chain.columns:
        return {"strike": None, "iv": None, "volume": None, "open_interest": None}

    # Find the strike closest to current price
    chain = chain.copy()
    chain["distance"] = (chain["strike"] - current_price).abs()
    atm_row = chain.loc[chain["distance"].idxmin()]

    iv = atm_row.get("impliedVolatility")
    if iv is not None and not math.isnan(iv):
        iv = float(iv)
    else:
        iv = None

    return {
        "strike": float(atm_row["strike"]),
        "iv": iv,
        "volume": int(atm_row.get("volume", 0) or 0),
        "open_interest": int(atm_row.get("openInterest", 0) or 0),
    }


def _compute_iv_skew(
    chain: pd.DataFrame,
    current_price: float,
) -> dict[str, float | None]:
    """Compute IV skew metrics from an options chain.

    IV skew = difference between OTM put IV and OTM call IV.
    High put skew indicates hedging demand (fear).

    Args:
        chain: Puts chain DataFrame from yfinance.
        current_price: Current stock/index price.

    Returns:
        Dict with otm_put_iv (5% OTM), otm_call_iv (5% OTM), skew value.
    """
    if chain.empty or "strike" not in chain.columns:
        return {"otm_put_iv": None, "otm_call_iv": None, "skew": None}

    # 5% OTM put = strike at ~95% of current price
    target_put_strike = current_price * 0.95
    # 5% OTM call = strike at ~105% of current price
    target_call_strike = current_price * 1.05

    chain = chain.copy()

    # Find closest to 5% OTM put
    chain["put_dist"] = (chain["strike"] - target_put_strike).abs()
    put_row = chain.loc[chain["put_dist"].idxmin()]
    otm_put_iv = put_row.get("impliedVolatility")
    if otm_put_iv is not None and not math.isnan(otm_put_iv):
        otm_put_iv = float(otm_put_iv)
    else:
        otm_put_iv = None

    # Find closest to 5% OTM call
    chain["call_dist"] = (chain["strike"] - target_call_strike).abs()
    call_row = chain.loc[chain["call_dist"].idxmin()]
    otm_call_iv = call_row.get("impliedVolatility")
    if otm_call_iv is not None and not math.isnan(otm_call_iv):
        otm_call_iv = float(otm_call_iv)
    else:
        otm_call_iv = None

    skew = None
    if otm_put_iv is not None and otm_call_iv is not None and otm_call_iv > 0:
        skew = round(otm_put_iv - otm_call_iv, 4)

    return {
        "otm_put_iv": round(otm_put_iv, 4) if otm_put_iv else None,
        "otm_call_iv": round(otm_call_iv, 4) if otm_call_iv else None,
        "skew": skew,
    }


def _classify_iv_level(
    iv: float,
    iv_percentile: float | None,
) -> str:
    """Classify IV level relative to historical context.

    Args:
        iv: Current annualized IV.
        iv_percentile: IV rank percentile (0-100) if available.

    Returns:
        Classification string.
    """
    if iv_percentile is not None:
        if iv_percentile >= 80:
            return "Very High"
        if iv_percentile >= 60:
            return "High"
        if iv_percentile >= 40:
            return "Normal"
        if iv_percentile >= 20:
            return "Low"
        return "Very Low"

    # Fallback: absolute IV thresholds (rough, stock-dependent)
    if iv >= 0.60:
        return "Very High"
    if iv >= 0.40:
        return "High"
    if iv >= 0.20:
        return "Normal"
    if iv >= 0.10:
        return "Low"
    return "Very Low"


class OptionsIVCollector(BaseSentimentCollector):
    """Collect options-implied volatility data using yfinance.

    For each ticker, fetches the nearest-expiry options chain and
    extracts ATM implied volatility, IV skew, and expected move
    (1-sigma, 2-sigma price ranges).
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch_options_data(
        self,
        ticker: str,
    ) -> dict[str, Any]:
        """Fetch options chain data for a single ticker.

        Args:
            ticker: US stock ticker (e.g., "AAPL").

        Returns:
            Dict with current_price, expiration dates, and nearest chain data.

        Raises:
            ValueError: If no options data is available.
        """
        yf_ticker = yf.Ticker(ticker)

        # Get current price
        hist = yf_ticker.history(period="5d")
        if hist.empty:
            raise ValueError(f"No price data for {ticker}")
        current_price = float(hist["Close"].iloc[-1])

        # Get available expiration dates
        expirations = yf_ticker.options
        if not expirations:
            raise ValueError(f"No options data for {ticker}")

        # Fetch chains for the nearest 3 expirations (short/mid/long view)
        chains: list[dict[str, Any]] = []
        now = datetime.now(tz=timezone.utc)

        for exp_str in expirations[:3]:
            exp_date = datetime.strptime(exp_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc,
            )
            dte = (exp_date - now).days
            if dte < 1:
                continue

            try:
                opt_chain = yf_ticker.option_chain(exp_str)
            except Exception:
                continue

            calls = opt_chain.calls
            puts = opt_chain.puts

            if calls.empty and puts.empty:
                continue

            # ATM IV from calls and puts
            call_atm = _find_atm_iv(calls, current_price)
            put_atm = _find_atm_iv(puts, current_price)

            # Average of call and put ATM IV for more stable estimate
            atm_iv = None
            if call_atm["iv"] is not None and put_atm["iv"] is not None:
                atm_iv = (call_atm["iv"] + put_atm["iv"]) / 2
            elif call_atm["iv"] is not None:
                atm_iv = call_atm["iv"]
            elif put_atm["iv"] is not None:
                atm_iv = put_atm["iv"]

            # IV skew from puts chain
            skew_data = _compute_iv_skew(puts, current_price)

            # Total open interest and volume for sentiment gauge
            total_call_oi = int(calls["openInterest"].sum()) if "openInterest" in calls.columns else 0
            total_put_oi = int(puts["openInterest"].sum()) if "openInterest" in puts.columns else 0
            total_call_vol = int(calls["volume"].fillna(0).sum()) if "volume" in calls.columns else 0
            total_put_vol = int(puts["volume"].fillna(0).sum()) if "volume" in puts.columns else 0

            chains.append({
                "expiration": exp_str,
                "dte": dte,
                "atm_iv": round(atm_iv, 4) if atm_iv else None,
                "call_atm": call_atm,
                "put_atm": put_atm,
                "iv_skew": skew_data,
                "total_call_oi": total_call_oi,
                "total_put_oi": total_put_oi,
                "total_call_volume": total_call_vol,
                "total_put_volume": total_put_vol,
                "oi_pc_ratio": round(total_put_oi / total_call_oi, 4) if total_call_oi > 0 else None,
                "volume_pc_ratio": round(total_put_vol / total_call_vol, 4) if total_call_vol > 0 else None,
            })

        if not chains:
            raise ValueError(f"No valid options chains for {ticker}")

        return {
            "current_price": current_price,
            "expirations_available": len(expirations),
            "chains": chains,
        }

    def _compute_historical_iv_rank(
        self,
        ticker: str,
        current_iv: float,
        lookback_days: int = 252,
    ) -> float | None:
        """Compute IV rank (percentile) vs historical realized volatility.

        IV Rank = what % of the past year had lower IV than current.

        Args:
            ticker: Stock ticker.
            current_iv: Current annualized ATM IV.
            lookback_days: Trading days for historical comparison.

        Returns:
            IV percentile (0-100) or None if insufficient data.
        """
        try:
            yf_ticker = yf.Ticker(ticker)
            hist = yf_ticker.history(period="1y")
            if len(hist) < 30:
                return None

            # Compute 20-day rolling realized volatility (annualized)
            returns = hist["Close"].pct_change().dropna()
            rolling_vol = returns.rolling(window=20).std() * math.sqrt(252)
            rolling_vol = rolling_vol.dropna()

            if rolling_vol.empty:
                return None

            # IV rank: % of historical realized vol values below current IV
            rank = float((rolling_vol < current_iv).sum() / len(rolling_vol) * 100)
            return round(rank, 1)

        except Exception:
            return None

    def collect_stock(self, ticker: str) -> dict[str, Any]:
        """Collect options IV data and compute expected moves for a single stock.

        Args:
            ticker: US stock ticker (e.g., "AAPL").

        Returns:
            Dict with ticker, current price, IV data, expected moves,
            and sigma price ranges.
        """
        try:
            data = self._fetch_options_data(ticker)
        except Exception as e:
            self._logger.warning(
                "options_iv_fetch_failed",
                ticker=ticker,
                error=str(e),
            )
            return {
                "ticker": ticker,
                "error": str(e),
                "expected_moves": [],
            }

        current_price = data["current_price"]
        chains = data["chains"]

        # Compute expected moves for each expiration
        expected_moves: list[dict[str, Any]] = []

        for chain in chains:
            atm_iv = chain["atm_iv"]
            dte = chain["dte"]

            if atm_iv is None or dte < 1:
                continue

            # Expected move = price × IV × √(DTE / 365)
            expected_move = current_price * atm_iv * math.sqrt(dte / 365)

            # σ price ranges
            sigma_1 = round(expected_move, 2)
            sigma_2 = round(expected_move * 2, 2)

            expected_moves.append({
                "expiration": chain["expiration"],
                "dte": dte,
                "atm_iv": round(atm_iv, 4),
                "atm_iv_pct": round(atm_iv * 100, 2),
                "expected_move": sigma_1,
                "expected_move_pct": round(sigma_1 / current_price * 100, 2),
                "sigma_1": {
                    "upper": round(current_price + sigma_1, 2),
                    "lower": round(current_price - sigma_1, 2),
                    "probability": 68.2,
                },
                "sigma_2": {
                    "upper": round(current_price + sigma_2, 2),
                    "lower": round(current_price - sigma_2, 2),
                    "probability": 95.4,
                },
                "iv_skew": chain["iv_skew"],
                "oi_pc_ratio": chain["oi_pc_ratio"],
                "volume_pc_ratio": chain["volume_pc_ratio"],
            })

        # Use nearest expiration as primary
        primary = expected_moves[0] if expected_moves else None

        # IV rank (historical percentile)
        iv_rank = None
        if primary and primary["atm_iv"] is not None:
            iv_rank = self._compute_historical_iv_rank(
                ticker, primary["atm_iv"],
            )

        # Classify IV level
        iv_level = None
        if primary and primary["atm_iv"] is not None:
            iv_level = _classify_iv_level(primary["atm_iv"], iv_rank)

        # Skew sentiment: high put skew = fear/hedging demand
        skew_sentiment = "Neutral"
        if primary and primary["iv_skew"].get("skew") is not None:
            skew = primary["iv_skew"]["skew"]
            if skew > 0.10:
                skew_sentiment = "High Fear (put premium)"
            elif skew > 0.05:
                skew_sentiment = "Moderate Fear"
            elif skew < -0.05:
                skew_sentiment = "Complacent (call premium)"
            else:
                skew_sentiment = "Neutral"

        result = {
            "ticker": ticker,
            "current_price": current_price,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "iv_rank": iv_rank,
            "iv_level": iv_level,
            "skew_sentiment": skew_sentiment,
            "expected_moves": expected_moves,
            "expirations_available": data["expirations_available"],
        }

        self._logger.info(
            "options_iv_collected",
            ticker=ticker,
            price=current_price,
            atm_iv=primary["atm_iv_pct"] if primary else None,
            iv_rank=iv_rank,
            iv_level=iv_level,
            expected_move=primary["expected_move"] if primary else None,
        )

        return result

    def collect(self) -> list[dict[str, Any]]:
        """Collect options IV data for configured US watchlist stocks.

        Returns:
            List of per-ticker options IV and expected move dicts.
        """
        us_watchlist = self._config.market.us.watchlist
        results: list[dict[str, Any]] = []

        for item in us_watchlist:
            if item.ticker.startswith("^"):
                continue
            data = self.collect_stock(item.ticker)
            results.append(data)

        return results
