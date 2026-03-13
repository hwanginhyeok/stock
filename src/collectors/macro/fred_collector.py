"""FRED macroeconomic liquidity data collector.

Fetches Fed balance sheet, TGA, RRP, MMF, yield curve, and credit spreads
directly from the FRED public CSV endpoint — no API key required.

MMF weekly data is sourced directly from ICI (Investment Company Institute)
XLS, which is ~23 days more current than FRED and covers total MMF assets
(institutional + retail, ~$7.8T) rather than retail-only ($2.3T).

Usage::

    collector = FREDCollector()
    data = collector.collect()
    print(data["net_liquidity_b"])   # Net liquidity in $B
    print(data["mmf_weekly_b"])      # Total MMF assets in $B (ICI source)
    print(data["mmf_flow_b"])        # MMF weekly net cash flow in $B
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

import pandas as pd
import requests

from src.core.logger import get_logger

logger = get_logger(__name__)

_FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"
_ICI_MMF_URL = "https://www.ici.org/mm_summary_data_{year}.xls"
_ICI_HEADERS = {"User-Agent": "Mozilla/5.0"}
_TIMEOUT = 10  # seconds per request


# Series definitions: (fred_id, unit_divisor_to_billions, description)
# mmf_weekly is excluded — fetched directly from ICI for fresher data.
_SERIES: dict[str, tuple[str, float, str]] = {
    # Supply side
    "walcl":      ("WALCL",         1_000,    "Fed 자산 총계 (주간, $M → $B)"),
    "tga":        ("WTREGEN",        1_000,    "TGA 잔고 (주간, $M → $B)"),
    "rrp":        ("RRPONTSYD",          1,    "RRP 잔고 (일별, $B)"),
    "mmf_total":  ("MMMFFAQ027S",   1_000,    "MMF 전체 잔고 (분기, $M → $B)"),
    # Yield curve & credit
    "dgs2":       ("DGS2",              1,    "2년물 국채금리 (%)"),
    "dgs10":      ("DGS10",             1,    "10년물 국채금리 (%)"),
    "yield_2s10s":("T10Y2Y",            1,    "2s10s 스프레드 (%)"),
    "hy_spread":  ("BAMLH0A0HYM2",      1,    "HY 크레딧 스프레드 (%)"),
}


def _fetch_series(fred_id: str, divisor: float) -> pd.Series | None:
    """Fetch a single FRED series as a pandas Series indexed by date.

    Args:
        fred_id: FRED series identifier.
        divisor: Divide raw values by this to convert units to $B.

    Returns:
        Numeric pandas Series or None on failure.
    """
    try:
        url = f"{_FRED_CSV}?id={fred_id}"
        r = requests.get(url, timeout=_TIMEOUT)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "value"]
        df = df[df["value"] != "."].copy()
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"]) / divisor
        return df.set_index("date")["value"]
    except Exception as e:
        logger.warning("fred_fetch_failed", series=fred_id, error=str(e))
        return None


def _fetch_ici_mmf_weekly() -> pd.Series | None:
    """Fetch total weekly MMF assets from ICI XLS (institutional + retail).

    ICI publishes every Thursday with ~1 week lag, compared to FRED's ~4 week
    lag. Covers total MMF (~$7.8T) vs FRED WRMFNS retail-only (~$2.3T).

    URL pattern: https://www.ici.org/mm_summary_data_{year}.xls
    Falls back to previous year if current year file is not yet available.

    Returns:
        pd.Series indexed by date, values in $B, or None on failure.
    """
    for year in [datetime.now().year, datetime.now().year - 1]:
        try:
            url = _ICI_MMF_URL.format(year=year)
            r = requests.get(url, timeout=_TIMEOUT, headers=_ICI_HEADERS)
            r.raise_for_status()
            df = pd.read_excel(io.BytesIO(r.content), sheet_name="Public Report", header=None)
            # Data rows start at index 8: col 0=DATE, col 2=Total TNA (millions)
            data = df.iloc[8:].reset_index(drop=True)[[0, 2]].copy()
            data.columns = ["date", "tna_m"]
            data["tna_m"] = pd.to_numeric(data["tna_m"], errors="coerce")
            data["date"] = pd.to_datetime(data["date"], errors="coerce")
            data = data.dropna().sort_values("date")
            if data.empty:
                continue
            return (data.set_index("date")["tna_m"] / 1_000).rename("mmf_weekly")
        except Exception as e:
            logger.warning("ici_mmf_fetch_failed", year=year, error=str(e))
    return None


def _last(series: pd.Series | None) -> float | None:
    """Return the most recent non-null value."""
    if series is None or series.empty:
        return None
    val = series.dropna()
    return float(val.iloc[-1]) if not val.empty else None


def _last_date(series: pd.Series | None) -> str | None:
    """Return the date of the most recent non-null value."""
    if series is None or series.empty:
        return None
    val = series.dropna()
    return str(val.index[-1].date()) if not val.empty else None


def _wow_change(series: pd.Series | None, weeks: int = 1) -> float | None:
    """Week-over-week change (last value minus N weeks ago).

    Args:
        series: Indexed time series.
        weeks: Number of periods back (assumes weekly spacing).

    Returns:
        Absolute change in same units, or None.
    """
    if series is None:
        return None
    val = series.dropna()
    if len(val) < weeks + 1:
        return None
    return float(val.iloc[-1] - val.iloc[-(weeks + 1)])


class FREDCollector:
    """Collects FRED macroeconomic liquidity data.

    All data is fetched from the public FRED CSV endpoint.
    No API key required.
    """

    def collect_series(self, lookback_years: int = 2) -> dict[str, pd.Series]:
        """Return full time series for each FRED key, filtered to lookback window.

        Adds a ``net_liquidity`` key computed as WALCL - TGA - RRP
        (all resampled to weekly to align frequencies).

        Args:
            lookback_years: How many years of history to include.

        Returns:
            Dict mapping series key → pandas Series indexed by datetime.
        """
        cutoff = pd.Timestamp.now() - pd.DateOffset(years=lookback_years)
        raw: dict[str, pd.Series] = {}
        for key, (fred_id, divisor, _) in _SERIES.items():
            s = _fetch_series(fred_id, divisor)
            if s is not None:
                raw[key] = s[s.index >= cutoff]

        # MMF weekly: ICI direct (fresher than FRED WRMFNS)
        ici = _fetch_ici_mmf_weekly()
        if ici is not None:
            raw["mmf_weekly"] = ici[ici.index >= cutoff]

        # Net Liquidity on weekly-aligned basis
        if all(k in raw for k in ("walcl", "tga", "rrp")):
            walcl_w = raw["walcl"].resample("W").last().ffill()
            tga_w   = raw["tga"].resample("W").last().ffill()
            rrp_w   = raw["rrp"].resample("W").last().ffill()
            combined = pd.concat([walcl_w, tga_w, rrp_w], axis=1, join="inner")
            combined.columns = ["walcl", "tga", "rrp"]
            raw["net_liquidity"] = (
                combined["walcl"] - combined["tga"] - combined["rrp"]
            ).dropna()

        # MMF net cash flow (weekly diff of mmf_weekly)
        if "mmf_weekly" in raw:
            raw["mmf_flow"] = raw["mmf_weekly"].diff().dropna()

        return raw

    def collect(self) -> dict[str, Any]:
        """Fetch all liquidity series and return a flat result dict.

        Returns:
            Dict with keys:
                - ``<key>_b``: Latest value in $B (or % for rates).
                - ``<key>_date``: Date string of latest value.
                - ``<key>_wow``: Week-over-week change.
                - ``net_liquidity_b``: Fed BS - TGA - RRP.
                - ``net_liquidity_wow``: Net liquidity WoW change.
                - ``mmf_flow_b``: MMF weekly net cash flow ($B).
                - ``fetched_at``: ISO timestamp.
        """
        logger.info("fred_collect_start")
        raw: dict[str, pd.Series | None] = {}

        for key, (fred_id, divisor, _) in _SERIES.items():
            raw[key] = _fetch_series(fred_id, divisor)

        # MMF weekly: ICI direct (23 days fresher than FRED, total assets)
        raw["mmf_weekly"] = _fetch_ici_mmf_weekly()

        result: dict[str, Any] = {"fetched_at": datetime.now().isoformat()}

        for key in _SERIES:
            s = raw[key]
            result[f"{key}_b"] = _last(s)
            result[f"{key}_date"] = _last_date(s)
            result[f"{key}_wow"] = _wow_change(s)

        # MMF weekly (ICI) — handled separately as it's not in _SERIES
        s = raw["mmf_weekly"]
        result["mmf_weekly_b"]    = _last(s)
        result["mmf_weekly_date"] = _last_date(s)
        result["mmf_weekly_wow"]  = _wow_change(s)

        # Net Liquidity = Fed BS - TGA - RRP
        walcl = _last(raw["walcl"])
        tga   = _last(raw["tga"])
        rrp   = _last(raw["rrp"])
        if all(v is not None for v in [walcl, tga, rrp]):
            result["net_liquidity_b"] = round(walcl - tga - rrp, 1)
        else:
            result["net_liquidity_b"] = None

        # Net liquidity WoW (approximate: walcl_wow - tga_wow - rrp_wow)
        w_wow = _wow_change(raw["walcl"])
        t_wow = _wow_change(raw["tga"])
        r_wow = _wow_change(raw["rrp"])
        if all(v is not None for v in [w_wow, t_wow, r_wow]):
            result["net_liquidity_wow"] = round(w_wow - t_wow - r_wow, 1)
        else:
            result["net_liquidity_wow"] = None

        # MMF Net Cash Flow: weekly diff of mmf_weekly series
        mmf_flow = _wow_change(raw["mmf_weekly"])
        result["mmf_flow_b"] = round(mmf_flow, 1) if mmf_flow is not None else None

        logger.info(
            "fred_collect_done",
            net_liquidity_b=result.get("net_liquidity_b"),
            rrp_b=result.get("rrp_b"),
            mmf_flow_b=result.get("mmf_flow_b"),
        )
        return result
