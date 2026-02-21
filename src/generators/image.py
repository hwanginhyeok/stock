"""Chart image generator using matplotlib for SNS content."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from src.core.config import PROJECT_ROOT
from src.core.models import MarketSnapshot, StockAnalysis
from src.generators.base import BaseGenerator

matplotlib.use("Agg")

# Output directory for generated images
IMAGE_OUTPUT_DIR = PROJECT_ROOT / "data" / "generated" / "images"


class ImageGenerator(BaseGenerator):
    """Generate chart images for SNS posts using matplotlib.

    Does not use Claude API. Produces PNG images saved to
    ``data/generated/images/``.
    """

    def __init__(self) -> None:
        super().__init__()
        self._setup_korean_font()
        IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def generate(self, **kwargs: Any) -> Path:
        """Generate a chart image.

        Args:
            **kwargs: Must include ``chart_type`` (str). Additional args
                depend on chart type.

        Returns:
            Path to generated PNG file.
        """
        chart_type: str = kwargs.get("chart_type", "market_summary")
        if chart_type == "market_summary":
            return self.generate_market_summary_card(kwargs.get("snapshots", []))
        if chart_type == "stock_chart":
            return self.generate_stock_chart(
                kwargs["ticker"],
                kwargs["ohlcv"],
                kwargs.get("indicators", {}),
            )
        if chart_type == "performance_comparison":
            return self.generate_performance_comparison(kwargs.get("analyses", []))
        return self.generate_market_summary_card(kwargs.get("snapshots", []))

    def generate_market_summary_card(
        self,
        snapshots: list[MarketSnapshot],
    ) -> Path:
        """Generate a market summary infographic card.

        Shows index values and change percentages in a clean card format.

        Args:
            snapshots: List of market snapshots to display.

        Returns:
            Path to saved PNG file.
        """
        fig, ax = plt.subplots(figsize=(10, 6), facecolor="#1a1a2e")
        ax.set_facecolor("#1a1a2e")
        ax.axis("off")

        title = "시장 요약"
        ax.text(
            0.5, 0.95, title,
            transform=ax.transAxes,
            fontsize=24, fontweight="bold",
            color="white", ha="center", va="top",
        )

        if not snapshots:
            ax.text(
                0.5, 0.5, "데이터 없음",
                transform=ax.transAxes,
                fontsize=16, color="gray", ha="center", va="center",
            )
            return self._save_figure(fig, "market_summary")

        n = len(snapshots)
        for i, snap in enumerate(snapshots[:6]):
            y = 0.80 - i * (0.70 / max(n, 1))
            color = "#4ecca3" if snap.change_percent >= 0 else "#e84545"
            sign = "+" if snap.change_percent >= 0 else ""

            # Index name
            ax.text(
                0.05, y, snap.index_name,
                transform=ax.transAxes,
                fontsize=14, color="white", va="center",
            )
            # Index value
            ax.text(
                0.50, y, f"{snap.index_value:,.2f}",
                transform=ax.transAxes,
                fontsize=16, fontweight="bold", color="white",
                ha="center", va="center",
            )
            # Change percentage
            ax.text(
                0.85, y, f"{sign}{snap.change_percent:.2f}%",
                transform=ax.transAxes,
                fontsize=16, fontweight="bold", color=color,
                ha="center", va="center",
            )

        fig.tight_layout(pad=1.5)
        return self._save_figure(fig, "market_summary")

    def generate_stock_chart(
        self,
        ticker: str,
        ohlcv: dict[str, list[float]],
        indicators: dict[str, Any] | None = None,
    ) -> Path:
        """Generate a stock price chart with optional indicators.

        Args:
            ticker: Stock ticker symbol.
            ohlcv: Dict with keys "dates", "open", "high", "low", "close",
                "volume".
            indicators: Optional dict of indicator data (e.g., sma_20, rsi).

        Returns:
            Path to saved PNG file.
        """
        indicators = indicators or {}
        close = ohlcv.get("close", [])
        dates = list(range(len(close)))

        fig, axes = plt.subplots(
            2, 1, figsize=(12, 8),
            gridspec_kw={"height_ratios": [3, 1]},
            facecolor="#1a1a2e",
        )
        ax_price, ax_volume = axes

        # Date labels for X axis
        date_labels = ohlcv.get("dates", [])

        # Price chart
        ax_price.set_facecolor("#16213e")
        ax_price.plot(dates, close, color="#4ecca3", linewidth=1.5, label="종가")
        ax_price.set_title(f"{ticker} 차트", color="white", fontsize=16, pad=10)
        ax_price.set_ylabel("가격", color="gray", fontsize=11)
        ax_price.tick_params(axis="both", colors="gray", labelsize=9)
        ax_price.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: f"{v:,.0f}")
        )
        ax_price.grid(axis="y", color="gray", alpha=0.2, linestyle="--")
        ax_price.spines["bottom"].set_color("gray")
        ax_price.spines["left"].set_color("gray")
        ax_price.spines["top"].set_visible(False)
        ax_price.spines["right"].set_visible(False)
        # Hide x tick labels on price chart (shared with volume below)
        ax_price.tick_params(axis="x", labelbottom=False)

        # Overlay indicators
        if "sma_20" in indicators:
            sma = indicators["sma_20"]
            ax_price.plot(
                dates[:len(sma)], sma,
                color="#e84545", linewidth=1, linestyle="--", label="SMA 20",
            )
        if "sma_60" in indicators:
            sma = indicators["sma_60"]
            ax_price.plot(
                dates[:len(sma)], sma,
                color="#f0c929", linewidth=1, linestyle="--", label="SMA 60",
            )

        ax_price.legend(loc="upper left", facecolor="#16213e", edgecolor="gray",
                        labelcolor="white", fontsize=9)

        # Volume chart
        volume = ohlcv.get("volume", [])
        if volume:
            colors = []
            for j in range(len(volume)):
                if j == 0:
                    colors.append("#4ecca3")
                elif close[j] >= close[j - 1]:
                    colors.append("#4ecca3")
                else:
                    colors.append("#e84545")

            ax_volume.set_facecolor("#16213e")
            ax_volume.bar(dates[:len(volume)], volume, color=colors, alpha=0.7)
            ax_volume.set_ylabel("거래량", color="gray", fontsize=11)
            ax_volume.set_xlabel("일자", color="gray", fontsize=11)
            ax_volume.tick_params(axis="both", colors="gray", labelsize=9)
            ax_volume.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda v, _: f"{v / 1_000_000:.0f}M"
                                  if v >= 1_000_000 else f"{v / 1_000:.0f}K"
                                  if v >= 1_000 else f"{v:.0f}")
            )
            ax_volume.grid(axis="y", color="gray", alpha=0.2, linestyle="--")
            ax_volume.spines["bottom"].set_color("gray")
            ax_volume.spines["left"].set_color("gray")
            ax_volume.spines["top"].set_visible(False)
            ax_volume.spines["right"].set_visible(False)

            # X axis date labels (show ~8 evenly spaced ticks)
            if date_labels:
                n_ticks = min(8, len(date_labels))
                step = max(1, len(date_labels) // n_ticks)
                tick_positions = list(range(0, len(date_labels), step))
                tick_labels = [str(date_labels[i]) for i in tick_positions]
                ax_volume.set_xticks(tick_positions)
                ax_volume.set_xticklabels(tick_labels, rotation=30, ha="right")
            else:
                ax_volume.set_xlabel("거래일", color="gray", fontsize=11)

        fig.tight_layout(pad=1.5)
        return self._save_figure(fig, f"stock_{ticker}")

    def generate_performance_comparison(
        self,
        analyses: list[StockAnalysis],
    ) -> Path:
        """Generate a horizontal bar chart comparing stock scores.

        Args:
            analyses: List of StockAnalysis with composite scores.

        Returns:
            Path to saved PNG file.
        """
        fig, ax = plt.subplots(figsize=(10, max(4, len(analyses) * 0.6)),
                               facecolor="#1a1a2e")
        ax.set_facecolor("#1a1a2e")

        if not analyses:
            ax.axis("off")
            ax.text(
                0.5, 0.5, "데이터 없음",
                transform=ax.transAxes,
                fontsize=16, color="gray", ha="center", va="center",
            )
            return self._save_figure(fig, "performance_comparison")

        # Sort by composite_score descending
        sorted_analyses = sorted(analyses, key=lambda a: a.composite_score)
        names = [f"{a.name}\n({a.ticker})" for a in sorted_analyses]
        scores = [a.composite_score for a in sorted_analyses]

        # Color gradient based on score
        colors = []
        for s in scores:
            if s >= 70:
                colors.append("#4ecca3")
            elif s >= 50:
                colors.append("#f0c929")
            else:
                colors.append("#e84545")

        y_pos = np.arange(len(names))
        ax.barh(y_pos, scores, color=colors, height=0.6, edgecolor="none")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, color="white", fontsize=10)
        ax.set_xlabel("종합 점수", color="gray", fontsize=11)
        ax.set_xlim(0, 105)
        ax.set_xticks([0, 20, 40, 60, 80, 100])
        ax.set_title("종목 스코어 비교", color="white", fontsize=16, pad=10)
        ax.tick_params(axis="both", colors="gray", labelsize=9)
        ax.grid(axis="x", color="gray", alpha=0.2, linestyle="--")
        ax.spines["bottom"].set_color("gray")
        ax.spines["left"].set_color("gray")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Score labels
        for i, (score, color) in enumerate(zip(scores, colors)):
            ax.text(
                score + 1, i, f"{score:.1f}",
                va="center", color=color, fontsize=10, fontweight="bold",
            )

        fig.tight_layout(pad=1.5)
        return self._save_figure(fig, "performance_comparison")

    @staticmethod
    def _setup_korean_font() -> None:
        """Configure matplotlib to use a Korean font.

        Tries NanumGothic, Malgun Gothic, then falls back to
        default sans-serif.
        """
        import matplotlib.font_manager as fm

        korean_fonts = ["NanumGothic", "Malgun Gothic", "맑은 고딕", "AppleGothic"]
        available = {f.name for f in fm.fontManager.ttflist}

        for font_name in korean_fonts:
            if font_name in available:
                plt.rcParams["font.family"] = font_name
                plt.rcParams["axes.unicode_minus"] = False
                return

        # Fallback: use sans-serif
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["axes.unicode_minus"] = False

    @staticmethod
    def _save_figure(fig: plt.Figure, name: str, dpi: int = 150) -> Path:
        """Save a matplotlib figure as PNG.

        Args:
            fig: Matplotlib figure.
            name: Base filename (without extension).
            dpi: Resolution in dots per inch.

        Returns:
            Path to saved file.
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = IMAGE_OUTPUT_DIR / filename

        fig.savefig(str(filepath), dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)

        return filepath
