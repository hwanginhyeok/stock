"""Sentiment contrarian strategy — buy fear, sell greed.

Uses Fear & Greed index and/or Put/Call ratio to generate
counter-trend signals. The premise: extreme fear = buying opportunity,
extreme greed = selling opportunity.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.backtesting.strategy.base import BaseStrategy, Signal, SignalType


class SentimentContrarianStrategy(BaseStrategy):
    """Buy when sentiment is extremely fearful, sell when extremely greedy.

    Args:
        fear_threshold: F&G score below this triggers BUY (default 25).
        greed_threshold: F&G score above this triggers SELL (default 75).
        putcall_fear: Put/Call ratio above this triggers BUY (default 1.2).
        putcall_greed: Put/Call ratio below this triggers SELL (default 0.5).
        allocation: Fraction of portfolio per trade (default 0.2).
    """

    def __init__(
        self,
        *,
        fear_threshold: float = 25,
        greed_threshold: float = 75,
        putcall_fear: float = 1.2,
        putcall_greed: float = 0.5,
        allocation: float = 0.2,
    ) -> None:
        self.fear_threshold = fear_threshold
        self.greed_threshold = greed_threshold
        self.putcall_fear = putcall_fear
        self.putcall_greed = putcall_greed
        self.allocation = allocation

    @property
    def name(self) -> str:
        return "sentiment_contrarian"

    @property
    def description(self) -> str:
        return (
            f"Buy when F&G < {self.fear_threshold} or P/C > {self.putcall_fear}, "
            f"Sell when F&G > {self.greed_threshold} or P/C < {self.putcall_greed}"
        )

    def generate_signals(
        self,
        date: str,
        prices: dict[str, pd.DataFrame],
        context: dict[str, Any] | None = None,
    ) -> list[Signal]:
        """Generate contrarian signals based on sentiment data.

        Expected context keys:
            - fear_greed_score: float (0-100)
            - putcall_ratio: float (optional)
        """
        if not context:
            return []

        fg_score = context.get("fear_greed_score")
        pc_ratio = context.get("putcall_ratio")

        signals: list[Signal] = []

        for ticker in prices:
            df = prices[ticker]
            if df.empty or date not in df.index.strftime("%Y-%m-%d").values:
                continue

            # Determine signal from Fear & Greed
            fg_signal = SignalType.HOLD
            fg_strength = 0.0
            if fg_score is not None:
                if fg_score <= self.fear_threshold:
                    fg_signal = SignalType.BUY
                    fg_strength = 1.0 - (fg_score / self.fear_threshold)
                elif fg_score >= self.greed_threshold:
                    fg_signal = SignalType.SELL
                    fg_strength = (fg_score - self.greed_threshold) / (
                        100 - self.greed_threshold
                    )

            # Determine signal from Put/Call
            pc_signal = SignalType.HOLD
            pc_strength = 0.0
            if pc_ratio is not None:
                if pc_ratio >= self.putcall_fear:
                    pc_signal = SignalType.BUY
                    pc_strength = min(1.0, (pc_ratio - self.putcall_fear) / 0.5)
                elif pc_ratio <= self.putcall_greed:
                    pc_signal = SignalType.SELL
                    pc_strength = min(
                        1.0, (self.putcall_greed - pc_ratio) / 0.3,
                    )

            # Combine signals — both agree = strong, one alone = moderate
            final_signal = SignalType.HOLD
            strength = 0.0
            reasons: list[str] = []

            if fg_signal == SignalType.BUY:
                reasons.append(f"F&G={fg_score:.0f} (Extreme Fear)")
            if pc_signal == SignalType.BUY:
                reasons.append(f"P/C={pc_ratio:.2f} (High Fear)")
            if fg_signal == SignalType.SELL:
                reasons.append(f"F&G={fg_score:.0f} (Extreme Greed)")
            if pc_signal == SignalType.SELL:
                reasons.append(f"P/C={pc_ratio:.2f} (Low Fear)")

            buy_signals = sum(
                1
                for s in [fg_signal, pc_signal]
                if s == SignalType.BUY
            )
            sell_signals = sum(
                1
                for s in [fg_signal, pc_signal]
                if s == SignalType.SELL
            )

            if buy_signals > sell_signals:
                final_signal = SignalType.BUY
                strength = max(fg_strength, pc_strength)
            elif sell_signals > buy_signals:
                final_signal = SignalType.SELL
                strength = max(fg_strength, pc_strength)

            if final_signal != SignalType.HOLD:
                signals.append(
                    Signal(
                        date=date,
                        ticker=ticker,
                        signal_type=final_signal,
                        strength=round(strength, 2),
                        reason=" + ".join(reasons),
                        allocation=self.allocation,
                    )
                )

        return signals
