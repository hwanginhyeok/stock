"""Technical + Sentiment combo strategy.

Combines RSI oversold/overbought signals with sentiment indicators
for higher-confidence entries and exits.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.backtesting.strategy.base import BaseStrategy, Signal, SignalType


class TechnicalComboStrategy(BaseStrategy):
    """Buy on RSI oversold + fear sentiment, sell on RSI overbought + greed.

    Requires both technical AND sentiment confirmation for a signal.

    Args:
        rsi_period: RSI calculation period (default 14).
        rsi_oversold: RSI level for oversold (default 30).
        rsi_overbought: RSI level for overbought (default 70).
        fear_threshold: F&G score for fear confirmation (default 35).
        greed_threshold: F&G score for greed confirmation (default 65).
        allocation: Portfolio fraction per trade (default 0.15).
    """

    def __init__(
        self,
        *,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        fear_threshold: float = 35,
        greed_threshold: float = 65,
        allocation: float = 0.15,
    ) -> None:
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.fear_threshold = fear_threshold
        self.greed_threshold = greed_threshold
        self.allocation = allocation

    @property
    def name(self) -> str:
        return "technical_combo"

    @property
    def description(self) -> str:
        return (
            f"Buy when RSI<{self.rsi_oversold} AND F&G<{self.fear_threshold}, "
            f"Sell when RSI>{self.rsi_overbought} AND F&G>{self.greed_threshold}"
        )

    def _compute_rsi(self, closes: pd.Series) -> float | None:
        """Compute RSI from a close price series."""
        if len(closes) < self.rsi_period + 1:
            return None

        delta = closes.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)

        avg_gain = gain.rolling(window=self.rsi_period, min_periods=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period, min_periods=self.rsi_period).mean()

        last_gain = avg_gain.iloc[-1]
        last_loss = avg_loss.iloc[-1]

        if last_loss == 0:
            return 100.0
        rs = last_gain / last_loss
        return 100 - (100 / (1 + rs))

    def generate_signals(
        self,
        date: str,
        prices: dict[str, pd.DataFrame],
        context: dict[str, Any] | None = None,
    ) -> list[Signal]:
        """Generate signals requiring both RSI and sentiment confirmation.

        Expected context keys:
            - fear_greed_score: float (0-100)
        """
        if not context:
            return []

        fg_score = context.get("fear_greed_score")
        if fg_score is None:
            return []

        signals: list[Signal] = []

        for ticker, df in prices.items():
            if df.empty:
                continue

            # Filter data up to current date
            date_ts = pd.Timestamp(date)
            df_until = df[df.index <= date_ts]
            if len(df_until) < self.rsi_period + 1:
                continue

            rsi = self._compute_rsi(df_until["close"])
            if rsi is None:
                continue

            # Both conditions must be met
            if rsi <= self.rsi_oversold and fg_score <= self.fear_threshold:
                strength = (
                    (self.rsi_oversold - rsi) / self.rsi_oversold * 0.5
                    + (self.fear_threshold - fg_score) / self.fear_threshold * 0.5
                )
                signals.append(
                    Signal(
                        date=date,
                        ticker=ticker,
                        signal_type=SignalType.BUY,
                        strength=round(min(1.0, strength), 2),
                        reason=f"RSI={rsi:.1f} + F&G={fg_score:.0f}",
                        allocation=self.allocation,
                    )
                )
            elif rsi >= self.rsi_overbought and fg_score >= self.greed_threshold:
                strength = (
                    (rsi - self.rsi_overbought) / (100 - self.rsi_overbought) * 0.5
                    + (fg_score - self.greed_threshold)
                    / (100 - self.greed_threshold)
                    * 0.5
                )
                signals.append(
                    Signal(
                        date=date,
                        ticker=ticker,
                        signal_type=SignalType.SELL,
                        strength=round(min(1.0, strength), 2),
                        reason=f"RSI={rsi:.1f} + F&G={fg_score:.0f}",
                        allocation=self.allocation,
                    )
                )

        return signals
