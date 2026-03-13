"""Liquidity & market trend chart generator for email reports.

Produces 4 base64-encoded PNG charts:

- ``liquidity``   : 2-panel — Net Liquidity (single line) + Component breakdown
- ``mmf``         : 2-panel — MMF balance (line) + Net Cash Flow (bar)
- ``currencies``  : 3-panel — DXY / USD/JPY / USD/KRW (1 year)
- ``destinations``: 1-panel — 6 assets normalized to 100 (1 year)

Usage::

    from src.generators.liquidity_chart import build_all_charts

    fred_series = FREDCollector().collect_series(lookback_years=2)
    fx_series   = FXCollector().collect_series(period="1y")
    charts = build_all_charts(fred_series, fx_series)
    # charts["liquidity"] → base64 PNG string
"""

from __future__ import annotations

import base64
import io
import os
from typing import Any

import matplotlib.dates as mdates
import matplotlib.font_manager as _fm
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# ── Korean font setup ────────────────────────────────────────────────────────
# Rule: On Linux/WSL, register Noto CJK font directly via file path before use.
# Using rcParams["font.family"] alone fails when font is not in matplotlib's
# default search path. addfont() + explicit family name is the reliable pattern.
_KOREAN_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_KOREAN_FONT_PATH):
    # addfont() on a .ttc collection registers only the first sub-font,
    # which is "Noto Sans CJK JP". The JP variant still contains all Hangul
    # glyphs, so it renders Korean correctly despite the name.
    _fm.fontManager.addfont(_KOREAN_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False  # prevent minus sign (−) from rendering as □


# ── Theme ───────────────────────────────────────────────────────────────────

_BG       = "#0f1117"
_BG2      = "#131929"
_GRID     = "#1a2236"
_TEXT     = "#94a3b8"
_TEXT2    = "#475569"
_GREEN    = "#34d399"
_RED      = "#f87171"
_BLUE     = "#60a5fa"
_ORANGE   = "#fb923c"
_PURPLE   = "#a78bfa"
_YELLOW   = "#fbbf24"
_CYAN     = "#22d3ee"

_DEST_COLORS = [_GREEN, _YELLOW, _ORANGE, _BLUE, _PURPLE, _CYAN]
_DEST_LABELS = ["S&P 500", "금(Gold)", "비트코인", "미채권TLT", "EM ETF", "구리"]


# ── Y-axis padding ───────────────────────────────────────────────────────────

def _set_ylim_padded(
    ax: plt.Axes,
    data_min: float,
    data_max: float,
    pad: float = 0.10,
) -> None:
    """Set y-axis limits to data_min - pad*range ~ data_max + pad*range.

    Rule: Never use 0~max for y-axis — it hides trend changes.
    Standard is min-10% ~ max+10% of the data range.

    Args:
        ax: Axes to update.
        data_min: Minimum data value plotted on this axis.
        data_max: Maximum data value plotted on this axis.
        pad: Fraction of range to add as padding on each side (default 0.10 = 10%).
    """
    rng = data_max - data_min
    if rng == 0:
        rng = abs(data_min) if data_min != 0 else 1.0
    ax.set_ylim(data_min - pad * rng, data_max + pad * rng)


def _apply_theme(fig: plt.Figure, axes: list[plt.Axes]) -> None:
    """Apply dark theme to figure and all axes."""
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


def _add_title(ax: plt.Axes, title: str, subtitle: str = "") -> None:
    ax.set_title(
        f"{title}\n{subtitle}" if subtitle else title,
        color=_TEXT, fontsize=9, pad=6, loc="left",
    )


def _fill_between_series(
    ax: plt.Axes, s: pd.Series, base: pd.Series | None, color: str, alpha: float = 0.15,
) -> None:
    """Fill area between series and base (or 0)."""
    if base is None:
        ax.fill_between(s.index, s.values, alpha=alpha, color=color)
    else:
        ax.fill_between(s.index, s.values, base.reindex(s.index).ffill().values,
                        alpha=alpha, color=color)


# ── Chart 1: Liquidity ──────────────────────────────────────────────────────

def chart_liquidity(fred_series: dict[str, pd.Series]) -> str:
    """2-panel liquidity chart.

    Panel 1 (top):    Net Liquidity — single clean line.
    Panel 2 (bottom): Component breakdown — Fed BS / TGA / RRP stacked view.
    """
    net    = fred_series.get("net_liquidity")
    walcl  = fred_series.get("walcl")
    tga    = fred_series.get("tga")
    rrp    = fred_series.get("rrp")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), facecolor=_BG,
                                    gridspec_kw={"hspace": 0.45})

    # ── Panel 1: Net Liquidity ─────────────────────────────────────────────
    if net is not None and not net.empty:
        net_smooth = net.resample("W").last().ffill()
        vals1 = net_smooth.values / 1000
        ax1.plot(net_smooth.index, vals1,
                 color=_GREEN, linewidth=1.8, label="Net Liquidity")
        _fill_between_series(ax1, net_smooth / 1000, None, _GREEN, alpha=0.12)

        # Highlight latest value
        last_val = vals1[-1]
        ax1.axhline(last_val, color=_GREEN, linewidth=0.5, linestyle="--", alpha=0.4)
        ax1.annotate(
            f"  ${last_val:.2f}T",
            xy=(net_smooth.index[-1], last_val),
            color=_GREEN, fontsize=8, va="center",
        )

        # Y-axis: min-10% ~ max+10% (never 0~max)
        _set_ylim_padded(ax1, vals1.min(), vals1.max())

    _add_title(ax1, "Net Liquidity  (Fed BS − TGA − RRP)", "단위: $T")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.1f}T"))

    # ── Panel 2: Component Breakdown ──────────────────────────────────────
    all_vals2: list[float] = []

    if walcl is not None:
        walcl_w = walcl.resample("W").last().ffill()
        v = walcl_w.values / 1000
        ax2.plot(walcl_w.index, v,
                 color=_BLUE, linewidth=1.6, label="Fed 자산 총계", zorder=3)
        all_vals2.extend(v.tolist())

    if net is not None:
        net_w = net.resample("W").last().ffill()
        v = net_w.values / 1000
        ax2.plot(net_w.index, v,
                 color=_GREEN, linewidth=1.8, linestyle="--", label="Net Liquidity", zorder=4)
        all_vals2.extend(v.tolist())

    # TGA drag: shade between Fed BS and (Fed BS - TGA)
    if walcl is not None and tga is not None:
        w = walcl.resample("W").last().ffill()
        t = tga.resample("W").last().ffill()
        idx = w.index.intersection(t.index)
        mid = (w[idx] - t[idx]) / 1000
        ax2.fill_between(idx, w[idx] / 1000, mid,
                         alpha=0.25, color=_RED, label="TGA (흡수)")

    # RRP drag: shade between (Fed BS - TGA) and Net
    if walcl is not None and tga is not None and rrp is not None:
        w = walcl.resample("W").last().ffill()
        t = tga.resample("W").last().ffill()
        r = rrp.resample("W").last().ffill()
        idx = w.index.intersection(t.index).intersection(r.index)
        upper = (w[idx] - t[idx]) / 1000
        lower = (w[idx] - t[idx] - r[idx]) / 1000
        ax2.fill_between(idx, upper, lower,
                         alpha=0.35, color=_ORANGE, label="RRP (흡수)")

    # Y-axis: min-10% ~ max+10%
    if all_vals2:
        _set_ylim_padded(ax2, min(all_vals2), max(all_vals2))

    _add_title(ax2, "구성요소 분해  (Fed BS / TGA / RRP)", "단위: $T")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.1f}T"))
    ax2.legend(fontsize=7, facecolor=_BG, edgecolor=_GRID, labelcolor=_TEXT,
               loc="lower left", ncol=2)

    _apply_theme(fig, [ax1, ax2])
    fig.suptitle("유동성 공급 측", color=_TEXT, fontsize=10, y=1.01, x=0.02, ha="left")
    return _fig_to_b64(fig)


# ── Chart 2: MMF ────────────────────────────────────────────────────────────

def chart_mmf(fred_series: dict[str, pd.Series]) -> str:
    """2-panel MMF chart.

    Panel 1: MMF weekly balance level (line).
    Panel 2: MMF net cash flow per week (bar — green=inflow, red=outflow).
    """
    mmf   = fred_series.get("mmf_weekly")
    flow  = fred_series.get("mmf_flow")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5), facecolor=_BG,
                                    gridspec_kw={"hspace": 0.45, "height_ratios": [2, 1]})

    # ── Panel 1: Balance ──────────────────────────────────────────────────
    if mmf is not None and not mmf.empty:
        ax1.plot(mmf.index, mmf.values, color=_BLUE, linewidth=1.8)
        _fill_between_series(ax1, mmf, None, _BLUE, alpha=0.1)
        last = mmf.iloc[-1]
        ax1.annotate(f"  ${last:,.0f}B", xy=(mmf.index[-1], last),
                     color=_BLUE, fontsize=8, va="center")
        # Y-axis: min-10% ~ max+10%
        _set_ylim_padded(ax1, mmf.values.min(), mmf.values.max())

    _add_title(ax1, "MMF 잔고 (ICI 주간)", "단위: $B")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}B"))

    # ── Panel 2: Net Cash Flow bars ───────────────────────────────────────
    if flow is not None and not flow.empty:
        colors = [_GREEN if v >= 0 else _RED for v in flow.values]
        ax2.bar(flow.index, flow.values, color=colors, width=5, alpha=0.85)
        ax2.axhline(0, color=_TEXT2, linewidth=0.7)

        # 4-week rolling average
        roll = flow.rolling(4).mean().dropna()
        ax2.plot(roll.index, roll.values, color=_YELLOW, linewidth=1.2,
                 linestyle="--", label="4주 이동평균")
        ax2.legend(fontsize=7, facecolor=_BG, edgecolor=_GRID, labelcolor=_TEXT)

        # Y-axis: always include 0, then apply padding
        lo = min(flow.values.min(), 0)
        hi = max(flow.values.max(), 0)
        _set_ylim_padded(ax2, lo, hi)

    _add_title(ax2, "MMF 주간 순유입/유출", "단위: $B  (초록=유입, 빨강=유출)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:+.0f}B"))

    _apply_theme(fig, [ax1, ax2])
    fig.suptitle("MMF 자금 동향", color=_TEXT, fontsize=10, y=1.01, x=0.02, ha="left")
    return _fig_to_b64(fig)


# ── Chart 3: Currencies (normalized) ────────────────────────────────────────

_CURR_LABELS = ["DXY", "USD/JPY", "USD/KRW", "EUR/USD", "USD/CNY"]
_CURR_COLORS = [_BLUE, _RED, _ORANGE, _GREEN, _YELLOW]
_CURR_NOTES  = {
    "DXY":     "달러강세↑",
    "USD/JPY": "캐리확대↑",
    "USD/KRW": "EM이탈↑",
    "EUR/USD": "유로강세↑",
    "USD/CNY": "위안약세↑",
}


def chart_currencies(fx_series: dict[str, pd.Series]) -> str:
    """Single-panel currency flow signal chart normalized to 100 (1 year).

    All 5 currencies are plotted on one axis after normalizing to 100 at the
    start of the period, making relative % moves directly comparable — the
    same approach used in chart_destinations().
    """
    fig, ax = plt.subplots(1, 1, figsize=(7, 4), facecolor=_BG)

    norm_min_vals: list[float] = []
    norm_max_vals: list[float] = []

    for label, color in zip(_CURR_LABELS, _CURR_COLORS):
        s = fx_series.get(label)
        if s is None or s.empty:
            continue
        base = s.iloc[0]
        if base == 0:
            continue
        normalized = s / base * 100
        note = _CURR_NOTES.get(label, "")
        ax.plot(normalized.index, normalized.values, color=color,
                linewidth=1.5, label=f"{label}  ({note})")
        last = normalized.iloc[-1]
        ax.annotate(f"  {last:.0f}", xy=(normalized.index[-1], last),
                    color=color, fontsize=7.5, va="center")
        norm_min_vals.append(float(normalized.min()))
        norm_max_vals.append(float(normalized.max()))

    ax.axhline(100, color=_TEXT2, linewidth=0.7, linestyle="--", alpha=0.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}"))
    ax.legend(fontsize=7.5, facecolor=_BG, edgecolor=_GRID, labelcolor=_TEXT,
              loc="upper left", ncol=2, framealpha=0.8)

    # Y-axis: min-10% ~ max+10% across all normalized series
    if norm_min_vals:
        _set_ylim_padded(ax, min(norm_min_vals), max(norm_max_vals))

    _add_title(ax, "흐름 신호 — 통화  (기준=100, 1년)",
               "DXY / USD/JPY / USD/KRW / EUR/USD / USD/CNY")
    _apply_theme(fig, [ax])
    fig.suptitle("환율 흐름 신호", color=_TEXT, fontsize=10, y=1.01, x=0.02, ha="left")
    return _fig_to_b64(fig)


# ── Chart 4: Destinations (normalized) ─────────────────────────────────────

def chart_destinations(fx_series: dict[str, pd.Series]) -> str:
    """Single-panel destination assets normalized to 100 (1 year)."""
    fig, ax = plt.subplots(1, 1, figsize=(7, 4), facecolor=_BG)

    plotted = []
    norm_min_vals: list[float] = []
    norm_max_vals: list[float] = []

    for label, color in zip(_DEST_LABELS, _DEST_COLORS):
        s = fx_series.get(label)
        if s is None or s.empty:
            continue
        base = s.iloc[0]
        if base == 0:
            continue
        normalized = (s / base * 100)
        ax.plot(normalized.index, normalized.values, color=color,
                linewidth=1.5, label=label)
        last = normalized.iloc[-1]
        ax.annotate(f"  {last:.0f}", xy=(normalized.index[-1], last),
                    color=color, fontsize=7.5, va="center")
        plotted.append(label)
        norm_min_vals.append(float(normalized.min()))
        norm_max_vals.append(float(normalized.max()))

    ax.axhline(100, color=_TEXT2, linewidth=0.7, linestyle="--", alpha=0.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}"))
    ax.legend(fontsize=7.5, facecolor=_BG, edgecolor=_GRID, labelcolor=_TEXT,
              loc="upper left", ncol=3, framealpha=0.8)

    # Y-axis: min-10% ~ max+10% across all normalized series
    if norm_min_vals:
        _set_ylim_padded(ax, min(norm_min_vals), max(norm_max_vals))

    _add_title(ax, "도착지 자산 성과  (기준=100, 1년)", "S&P500 / 금 / BTC / 채권 / EM / 구리")
    _apply_theme(fig, [ax])
    fig.suptitle("돈이 어디에 도착했나", color=_TEXT, fontsize=10, y=1.01, x=0.02, ha="left")
    return _fig_to_b64(fig)


# ── Chart 5: Sector ETFs ────────────────────────────────────────────────────

_SECTOR_ITEMS: list[tuple[str, str, str]] = [
    ("XLK",  "기술",        "#60a5fa"),   # blue
    ("XLC",  "커뮤니케이션", "#a78bfa"),  # purple
    ("XLF",  "금융",        "#34d399"),   # green
    ("XLY",  "임의소비재",  "#fb923c"),   # orange
    ("XLV",  "헬스케어",    "#f472b6"),   # pink
    ("XLP",  "필수소비재",  "#fbbf24"),   # yellow
    ("XLE",  "에너지",      "#f87171"),   # red
    ("XLI",  "산업재",      "#22d3ee"),   # cyan
    ("XLB",  "소재",        "#a3e635"),   # lime
    ("XLU",  "유틸리티",    "#94a3b8"),   # slate
    ("XLRE", "리츠",        "#e879f9"),   # fuchsia
]


def chart_sectors(fx_series: dict[str, pd.Series]) -> str:
    """Single-panel sector ETF chart: 1-week % change horizontal bar.

    Sectors sorted best→worst so the rotation direction is visible at a glance.
    Multi-period comparison (1W/1M/3M/1Y) is provided as an HTML table in the
    email template — the chart focuses on the most recent weekly momentum signal.
    """
    fig, ax = plt.subplots(1, 1, figsize=(7, 4.5), facecolor=_BG)

    bar_data: list[tuple[str, float, str]] = []
    for ticker, kor, color in _SECTOR_ITEMS:
        s = fx_series.get(ticker)
        if s is None or len(s) < 6:
            continue
        pct_1w = (float(s.iloc[-1]) / float(s.iloc[-6]) - 1) * 100
        bar_data.append((f"{ticker}  {kor}", pct_1w, color))

    if bar_data:
        # Sort best → worst (barh: best at top)
        bar_data.sort(key=lambda x: x[1])
        labels = [b[0] for b in bar_data]
        values = [b[1] for b in bar_data]
        colors = [_GREEN if v >= 0 else _RED for v in values]

        y_pos = list(range(len(labels)))
        bars = ax.barh(y_pos, values, color=colors, alpha=0.85, height=0.62)
        ax.axvline(0, color=_TEXT2, linewidth=0.8)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8)

        # Value labels at end of bars
        x_pad = (max(abs(v) for v in values) or 1) * 0.05
        for i, v in enumerate(values):
            ha = "left" if v >= 0 else "right"
            ax.text(v + (x_pad if v >= 0 else -x_pad), i,
                    f"{v:+.1f}%", va="center", ha=ha, fontsize=7.5, color=_TEXT)

        hi = max(abs(v) for v in values)
        ax.set_xlim(-(hi * 1.35), hi * 1.35)
        _set_ylim_padded(ax, -0.5, len(labels) - 0.5, pad=0.04)

    _add_title(ax, "섹터별 1주 성과  (최강→최약 정렬)", "초록=강세 / 빨강=약세")
    _apply_theme(fig, [ax])
    # Override x-axis: percentage format, not date
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:+.1f}%"))
    ax.xaxis.set_major_locator(mticker.MaxNLocator(6))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)

    fig.suptitle("섹터 순환 신호", color=_TEXT, fontsize=10, y=1.01, x=0.02, ha="left")
    return _fig_to_b64(fig)


# ── Public API ───────────────────────────────────────────────────────────────

def build_all_charts(
    fred_series: dict[str, pd.Series],
    fx_series: dict[str, pd.Series],
) -> dict[str, str]:
    """Generate all 4 charts and return base64 PNG strings.

    Args:
        fred_series: Output of FREDCollector.collect_series().
        fx_series:   Output of FXCollector.collect_series().

    Returns:
        Dict with keys: ``liquidity``, ``mmf``, ``currencies``, ``destinations``.
        Values are base64-encoded PNG strings ready for HTML ``<img src=...>``.
    """
    charts: dict[str, str] = {}

    charts["liquidity"]    = chart_liquidity(fred_series)
    charts["mmf"]          = chart_mmf(fred_series)
    charts["currencies"]   = chart_currencies(fx_series)
    charts["destinations"] = chart_destinations(fx_series)
    charts["sectors"]      = chart_sectors(fx_series)

    return charts
