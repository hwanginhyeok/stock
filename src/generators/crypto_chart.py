"""Crypto market chart generator for email reports.

Produces 2 base64-encoded PNG charts:

- ``crypto_price``: BTC and ETH normalized to 100 (1 year, single panel)
- ``eth_tvl``:      ETH DeFi TVL trend ($B, 1 year) — only if data available

Usage::

    from src.generators.crypto_chart import build_crypto_charts

    crypto_series = CryptoCollector().collect_series(period="1y")
    charts = build_crypto_charts(crypto_series)
    # charts["crypto_price"] → base64 PNG string
    # charts.get("eth_tvl")  → base64 PNG string or absent
"""

from __future__ import annotations

import base64
import io
import os

import matplotlib.dates as mdates
import matplotlib.font_manager as _fm
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

# ── Korean font setup (same pattern as liquidity_chart.py) ──────────────────
_KOREAN_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_KOREAN_FONT_PATH):
    _fm.fontManager.addfont(_KOREAN_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False


# ── Theme (shared with liquidity_chart.py) ───────────────────────────────────
_BG     = "#0f1117"
_BG2    = "#131929"
_GRID   = "#1a2236"
_TEXT   = "#94a3b8"
_TEXT2  = "#475569"
# Brand colors: BTC orange, ETH blue-purple
_BTC    = "#f7931a"
_ETH    = "#627eea"
_GREEN  = "#34d399"


# ── Shared helpers ───────────────────────────────────────────────────────────

def _set_ylim_padded(
    ax: plt.Axes,
    data_min: float,
    data_max: float,
    pad: float = 0.10,
) -> None:
    """Set y-axis limits with ±pad*range padding (never 0~max)."""
    rng = data_max - data_min
    if rng == 0:
        rng = abs(data_min) if data_min != 0 else 1.0
    ax.set_ylim(data_min - pad * rng, data_max + pad * rng)


def _apply_theme(fig: plt.Figure, axes: list[plt.Axes]) -> None:
    """Apply dark theme consistent with liquidity_chart.py."""
    fig.patch.set_facecolor(_BG)
    for ax in axes:
        ax.set_facecolor(_BG2)
        ax.tick_params(colors=_TEXT, labelsize=8)
        ax.xaxis.label.set_color(_TEXT)
        ax.yaxis.label.set_color(_TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(_GRID)
        ax.grid(color=_GRID, linewidth=0.5, alpha=0.8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%y/%m"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha="center")


def _fig_to_b64(fig: plt.Figure) -> str:
    """Render figure to base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


# ── Chart 1: BTC / ETH normalized price ─────────────────────────────────────

def chart_crypto_price(crypto_series: dict[str, pd.Series]) -> str:
    """BTC and ETH normalized to 100 at start of period (1 year).

    Normalization lets us compare relative % moves on a single axis —
    same approach as chart_destinations() in liquidity_chart.py.
    BTC uses brand orange (#f7931a), ETH uses brand blue-purple (#627eea).

    Args:
        crypto_series: Output of CryptoCollector.collect_series().
                       Must contain 'BTC-USD' and/or 'ETH-USD' keys.

    Returns:
        Base64-encoded PNG string.
    """
    fig, ax = plt.subplots(1, 1, figsize=(7, 4), facecolor=_BG)

    items = [
        ("BTC-USD", "BTC (비트코인)", _BTC),
        ("ETH-USD", "ETH (이더리움)", _ETH),
    ]

    norm_min_vals: list[float] = []
    norm_max_vals: list[float] = []

    for key, label, color in items:
        s = crypto_series.get(key)
        if s is None or s.empty:
            continue
        base = s.iloc[0]
        if base == 0:
            continue
        normalized = s / base * 100
        ax.plot(normalized.index, normalized.values, color=color,
                linewidth=1.8, label=label)
        last = normalized.iloc[-1]
        ax.annotate(f"  {last:.0f}", xy=(normalized.index[-1], last),
                    color=color, fontsize=8, va="center")
        norm_min_vals.append(float(normalized.min()))
        norm_max_vals.append(float(normalized.max()))

    ax.axhline(100, color=_TEXT2, linewidth=0.7, linestyle="--", alpha=0.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}"))
    ax.legend(fontsize=8, facecolor=_BG, edgecolor=_GRID, labelcolor=_TEXT,
              loc="upper left", ncol=2, framealpha=0.8)

    if norm_min_vals:
        _set_ylim_padded(ax, min(norm_min_vals), max(norm_max_vals))

    ax.set_title("BTC / ETH 가격 추이  (기준=100, 1년)",
                 color=_TEXT, fontsize=9, pad=6, loc="left")
    _apply_theme(fig, [ax])
    fig.suptitle("크립토 가격 흐름", color=_TEXT, fontsize=10, y=1.01, x=0.02, ha="left")
    return _fig_to_b64(fig)


# ── Chart 2: ETH DeFi TVL ────────────────────────────────────────────────────

def chart_eth_tvl(crypto_series: dict[str, pd.Series]) -> str | None:
    """ETH DeFi TVL trend chart (1 year, $B).

    Shows the health of the Ethereum DeFi ecosystem over time.
    Returns None if ETH-TVL data is not available in crypto_series.

    Args:
        crypto_series: Must contain 'ETH-TVL' key (from CryptoCollector).

    Returns:
        Base64-encoded PNG string, or None if no TVL data.
    """
    tvl = crypto_series.get("ETH-TVL")
    if tvl is None or tvl.empty:
        return None

    fig, ax = plt.subplots(1, 1, figsize=(7, 3.5), facecolor=_BG)

    ax.plot(tvl.index, tvl.values, color=_ETH, linewidth=1.8)
    ax.fill_between(tvl.index, tvl.values, alpha=0.12, color=_ETH)

    last = float(tvl.iloc[-1])
    ax.annotate(f"  ${last:.1f}B", xy=(tvl.index[-1], last),
                color=_ETH, fontsize=8, va="center")

    _set_ylim_padded(ax, float(tvl.min()), float(tvl.max()))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}B"))
    ax.set_title("ETH DeFi TVL  (1년)", color=_TEXT, fontsize=9, pad=6, loc="left")
    _apply_theme(fig, [ax])
    fig.suptitle("이더리움 생태계 TVL", color=_TEXT, fontsize=10, y=1.01, x=0.02, ha="left")
    return _fig_to_b64(fig)


# ── Public API ────────────────────────────────────────────────────────────────

def build_crypto_charts(crypto_series: dict[str, pd.Series]) -> dict[str, str]:
    """Generate all crypto charts and return base64 PNG strings.

    Args:
        crypto_series: Output of CryptoCollector.collect_series().

    Returns:
        Dict with keys:
            - ``crypto_price``: BTC/ETH normalized chart (always present if data exists)
            - ``eth_tvl``:      ETH DeFi TVL chart (only if ETH-TVL series available)
    """
    charts: dict[str, str] = {}

    charts["crypto_price"] = chart_crypto_price(crypto_series)

    eth_tvl_b64 = chart_eth_tvl(crypto_series)
    if eth_tvl_b64:
        charts["eth_tvl"] = eth_tvl_b64

    return charts
