"""SMA 정배열 + 눌림목 매수 전략 백테스트.

1-52: 사용자 트레이딩 스타일 기반
- 매수: 정배열(SMA5>10>20>50>VWMA100) 상태에서 SMA20/50 눌림목 터치 후 양봉 반등
- 매도: 역배열 진입 (추세 붕괴)
- 홀드: 정배열 유지 중 (추세 견조)
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.analyzers.sma_signals import classify_sma_alignment, detect_pullback_buy_signal
from src.backtesting.strategy.base import BaseStrategy, Signal, SignalType


class SMAAlignmentStrategy(BaseStrategy):
    """SMA 정배열 + 눌림목 매수 전략.

    Args:
        allocation: 매수 시 투입 비율 (default 0.8 = 현금의 80%).
        lookback: 눌림목 터치 탐색 봉 수 (default 5).
        touch_tolerance: 터치 허용 폭 (default 0.005 = ±0.5%).
        target_smas: 눌림목 대상 SMA (default [20, 50]).
    """

    def __init__(
        self,
        allocation: float = 0.8,
        lookback: int = 5,
        touch_tolerance: float = 0.005,
        target_smas: list[int] | None = None,
    ) -> None:
        self.allocation = allocation
        self.lookback = lookback
        self.touch_tolerance = touch_tolerance
        self.target_smas = target_smas or [20, 50]
        self._in_position: set[str] = set()

    @property
    def name(self) -> str:
        return "SMAAlignmentPullback"

    @property
    def description(self) -> str:
        return (
            f"정배열(SMA5>10>20>50>VWMA100) 구간 SMA{self.target_smas} "
            f"눌림목 매수 / 역배열 진입 매도"
        )

    def initialize(self, tickers: list[str], **kwargs: Any) -> None:
        self._in_position = set()

    def on_trade(self, ticker: str, signal_type: SignalType, date: str) -> None:
        if signal_type == SignalType.BUY:
            self._in_position.add(ticker)
        elif signal_type == SignalType.SELL:
            self._in_position.discard(ticker)

    def generate_signals(
        self,
        date: str,
        prices: dict[str, pd.DataFrame],
        context: dict[str, Any] | None = None,
    ) -> list[Signal]:
        signals: list[Signal] = []

        for ticker, df in prices.items():
            if len(df) < 110:
                continue

            # BacktestEngine은 소문자 컬럼 전달 → sma_signals는 대문자 필요
            df_upper = df.rename(
                columns={"open": "Open", "high": "High", "low": "Low",
                         "close": "Close", "volume": "Volume"}
            )

            align = classify_sma_alignment(df_upper)
            alignment = align.get("alignment", "N/A")

            if ticker in self._in_position:
                # 보유 중: 역배열 진입 시 매도
                if alignment == "역배열":
                    signals.append(Signal(
                        date=date,
                        ticker=ticker,
                        signal_type=SignalType.SELL,
                        strength=0.9,
                        reason=f"역배열 진입 — 추세 붕괴 ({date})",
                        allocation=1.0,
                    ))
            else:
                # 미보유: 정배열 + 눌림목 매수 시그널
                if alignment != "정배열":
                    continue

                sig = detect_pullback_buy_signal(
                    df_upper,
                    target_smas=self.target_smas,
                    lookback=self.lookback,
                    touch_tolerance=self.touch_tolerance,
                    alignment_result=align,
                )

                if sig.get("signal"):
                    touched = sig.get("touched_sma", "")
                    signals.append(Signal(
                        date=date,
                        ticker=ticker,
                        signal_type=SignalType.BUY,
                        strength=0.8,
                        reason=sig.get("reason", f"{touched} 눌림목 매수"),
                        allocation=self.allocation,
                    ))

        return signals
