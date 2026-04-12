"""TSLA 자체 차트 API — OHLCV + 기술 지표 + 이벤트 마커.

lightweight-charts 프론트엔드에 데이터를 공급한다.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/chart", tags=["chart"])

# OHLCV 캐시 (메모리, 5분 TTL)
_ohlcv_cache: dict[str, tuple[float, list[dict]]] = {}
_CACHE_TTL = 300


def _fetch_ohlcv(symbol: str, period: str, interval: str) -> list[dict]:
    """yfinance에서 OHLCV를 가져와 lightweight-charts 포맷으로 반환."""
    import time

    cache_key = f"{symbol}_{period}_{interval}"
    now = time.time()

    if cache_key in _ohlcv_cache:
        cached_ts, cached_data = _ohlcv_cache[cache_key]
        if now - cached_ts < _CACHE_TTL:
            return cached_data

    # 1h/4h는 period를 2y로 캡 (yfinance 제한)
    actual_period = period
    if interval in ("1h", "4h"):
        period_days = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825, "max": 3650}
        req_days = period_days.get(period, 180)
        actual_period = "2y" if req_days > 730 else period

    # 4h는 yfinance가 지원 안 함 → 1h로 받아서 resample
    yf_interval = "1h" if interval == "4h" else interval
    df = yf.download(symbol, period=actual_period, interval=yf_interval, progress=False)
    if df.empty:
        return []

    # MultiIndex 컬럼 처리 (yfinance 1.2+)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # 4h resample
    if interval == "4h":
        df = df.resample("4h").agg({
            "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum",
        }).dropna()

    records = []
    for idx, row in df.iterrows():
        ts = idx
        if hasattr(ts, "strftime"):
            if interval in ("1h", "4h"):
                time_val = int(ts.timestamp())
            else:
                time_val = ts.strftime("%Y-%m-%d")
        else:
            time_val = str(ts)

        records.append({
            "time": time_val,
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        })

    _ohlcv_cache[cache_key] = (now, records)
    return records


def _compute_indicators(records: list[dict]) -> dict:
    """pandas-ta로 기술 지표를 계산한다."""
    if not records:
        return {}

    df = pd.DataFrame(records)
    close = df["close"]

    result: dict = {}

    try:
        import pandas_ta as ta

        # RSI
        rsi = ta.rsi(close, length=14)
        if rsi is not None and len(rsi) > 0:
            result["rsi"] = round(float(rsi.iloc[-1]), 2) if pd.notna(rsi.iloc[-1]) else None
            result["rsi_series"] = [
                {"time": records[i]["time"], "value": round(float(v), 2)}
                for i, v in enumerate(rsi)
                if pd.notna(v)
            ]

        # MACD
        macd_df = ta.macd(close)
        if macd_df is not None:
            macd_col = [c for c in macd_df.columns if "MACD_" in c and "MACDs" not in c and "MACDh" not in c]
            signal_col = [c for c in macd_df.columns if "MACDs" in c]
            hist_col = [c for c in macd_df.columns if "MACDh" in c]

            if macd_col:
                macd_vals = macd_df[macd_col[0]]
                result["macd"] = round(float(macd_vals.iloc[-1]), 2) if pd.notna(macd_vals.iloc[-1]) else None
                result["macd_series"] = [
                    {"time": records[i]["time"], "value": round(float(v), 2)}
                    for i, v in enumerate(macd_vals)
                    if pd.notna(v)
                ]
            if signal_col:
                signal_vals = macd_df[signal_col[0]]
                result["signal_series"] = [
                    {"time": records[i]["time"], "value": round(float(v), 2)}
                    for i, v in enumerate(signal_vals)
                    if pd.notna(v)
                ]
            if hist_col:
                hist_vals = macd_df[hist_col[0]]
                result["histogram_series"] = [
                    {"time": records[i]["time"], "value": round(float(v), 2)}
                    for i, v in enumerate(hist_vals)
                    if pd.notna(v)
                ]

        # SMA 이평선 (5, 10, 20, 50, 100, 200)
        sma_lengths = [5, 10, 20, 50, 100, 200]
        sma_colors = {
            5: "#ef5350", 10: "#f59e0b", 20: "#3fb950",
            50: "#58a6ff", 100: "#a78bfa", 200: "#e6edf3",
        }
        result["sma"] = {}
        for length in sma_lengths:
            if len(close) < length:
                continue
            sma = ta.sma(close, length=length)
            if sma is not None:
                result["sma"][str(length)] = {
                    "value": round(float(sma.iloc[-1]), 2) if pd.notna(sma.iloc[-1]) else None,
                    "color": sma_colors[length],
                    "series": [
                        {"time": records[i]["time"], "value": round(float(v), 2)}
                        for i, v in enumerate(sma)
                        if pd.notna(v)
                    ],
                }

        # VWMA 100 (거래량 가중 이동평균)
        volume = df["volume"].astype(float)
        if len(close) >= 100:
            vwma = ta.vwma(close, volume, length=100)
            if vwma is not None:
                result["vwma100"] = {
                    "value": round(float(vwma.iloc[-1]), 2) if pd.notna(vwma.iloc[-1]) else None,
                    "series": [
                        {"time": records[i]["time"], "value": round(float(v), 2)}
                        for i, v in enumerate(vwma)
                        if pd.notna(v)
                    ],
                }

        # Volume Profile (가격대별 거래량 집계 — VPVR)
        price_min = float(df["low"].min())
        price_max = float(df["high"].max())
        num_bins = 30
        bin_size = (price_max - price_min) / num_bins if price_max > price_min else 1
        vpvr_bins: dict[int, float] = {}
        for _, row in df.iterrows():
            mid_price = (float(row["high"]) + float(row["low"])) / 2
            bin_idx = int((mid_price - price_min) / bin_size)
            bin_idx = min(bin_idx, num_bins - 1)
            vpvr_bins[bin_idx] = vpvr_bins.get(bin_idx, 0) + float(row["volume"])

        max_vol = max(vpvr_bins.values()) if vpvr_bins else 1
        result["volume_profile"] = [
            {
                "price": round(price_min + (i + 0.5) * bin_size, 2),
                "volume": round(vpvr_bins.get(i, 0)),
                "pct": round(vpvr_bins.get(i, 0) / max_vol * 100, 1),
            }
            for i in range(num_bins)
        ]

        # ADX
        adx = ta.adx(df["high"], df["low"], close)
        if adx is not None:
            adx_col = [c for c in adx.columns if c.startswith("ADX")]
            if adx_col:
                result["adx"] = round(float(adx[adx_col[0]].iloc[-1]), 2) if pd.notna(adx[adx_col[0]].iloc[-1]) else None

        # Supertrend
        st = ta.supertrend(df["high"], df["low"], close)
        if st is not None:
            st_col = [c for c in st.columns if "SUPERT_" in c and "SUPERTd" not in c and "SUPERTl" not in c and "SUPERTs" not in c]
            st_dir = [c for c in st.columns if "SUPERTd" in c]
            if st_col:
                result["supertrend"] = round(float(st[st_col[0]].iloc[-1]), 2) if pd.notna(st[st_col[0]].iloc[-1]) else None
            if st_dir:
                result["supertrend_direction"] = int(st[st_dir[0]].iloc[-1]) if pd.notna(st[st_dir[0]].iloc[-1]) else None

    except ImportError:
        pass

    # 현재가 정보
    if records:
        last = records[-1]
        prev = records[-2] if len(records) > 1 else last
        change = last["close"] - prev["close"]
        change_pct = (change / prev["close"]) * 100 if prev["close"] != 0 else 0
        result["last_price"] = last["close"]
        result["change"] = round(change, 2)
        result["change_pct"] = round(change_pct, 2)

    return result


@router.get("/ohlcv")
def get_ohlcv(
    symbol: str = "TSLA",
    period: str = Query("6mo", pattern="^(1mo|3mo|6mo|1y|2y|5y|max)$"),
    interval: str = Query("1d", pattern="^(1h|4h|1d|1wk|1mo)$"),
) -> dict:
    """OHLCV 데이터 + 기술 지표를 반환한다."""
    interval_labels = {"1h": "1시간", "4h": "4시간", "1d": "일봉", "1wk": "주봉", "1mo": "월봉"}
    records = _fetch_ohlcv(symbol, period, interval)
    indicators = _compute_indicators(records)

    return {
        "symbol": symbol,
        "period": period,
        "interval": interval,
        "interval_label": interval_labels.get(interval, interval),
        "count": len(records),
        "ohlcv": records,
        "indicators": indicators,
    }


# 이벤트 마커 카테고리 매핑
EVENT_CATEGORIES = {
    "earnings": {"label": "실적", "color": "#d29922"},
    "product": {"label": "제품", "color": "#3fb950"},
    "policy": {"label": "정책", "color": "#58a6ff"},
    "regulatory": {"label": "규제", "color": "#58a6ff"},
    "regulation": {"label": "규제", "color": "#58a6ff"},
    "macro": {"label": "거시", "color": "#bc8cff"},
    "military": {"label": "군사", "color": "#f85149"},
    "diplomatic": {"label": "외교", "color": "#56d4dd"},
    "sanctions": {"label": "제재", "color": "#f85149"},
    "deal": {"label": "딜", "color": "#3fb950"},
    "trade": {"label": "무역", "color": "#db6d28"},
    "sector": {"label": "섹터", "color": "#8b949e"},
    "analyst": {"label": "분석", "color": "#8b949e"},
    "war": {"label": "전쟁", "color": "#f85149"},
    "energy": {"label": "에너지", "color": "#db6d28"},
    "territorial": {"label": "영토", "color": "#f85149"},
}

# 마커 shape 매핑 (severity)
SEVERITY_SHAPES = {
    "critical": "arrowDown",
    "major": "circle",
    "moderate": "square",
    "minor": "square",
}


@router.get("/events")
def get_chart_events(
    symbol: str = "TSLA",
    period: str = Query("6mo", pattern="^(1mo|3mo|6mo|1y|2y|5y|max)$"),
    severity_min: str = Query("major", pattern="^(critical|major|moderate|minor)$"),
    tesla_only: bool = False,
) -> dict:
    """차트에 표시할 이벤트 마커를 반환한다.

    필터링 전략 (B안):
    1. Tesla 엔티티 직접 연결 이벤트 (항상 포함)
    2. macro critical 이벤트 (거시 영향)
    3. severity_min 이상만
    """
    from src.core.database import get_session, init_db
    from src.storage import OntologyEntityRepository, OntologyEventRepository, OntologyLinkRepository

    init_db()

    # 기간 계산
    period_days = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825, "max": 3650}
    cutoff = datetime.now() - timedelta(days=period_days.get(period, 180))

    severity_order = ["critical", "major", "moderate", "minor"]
    min_idx = severity_order.index(severity_min) if severity_min in severity_order else 1

    # Tesla 관련 엔티티 ID
    entity_repo = OntologyEntityRepository()
    tesla_keywords = ["Tesla", "TSLA", "Musk", "xAI", "SpaceX", "FSD", "Optimus", "Cybertruck", "Megapack"]
    tesla_entity_ids: set[str] = set()
    for ent in entity_repo.get_active():
        if any(kw.lower() in ent.name.lower() for kw in tesla_keywords) or ent.ticker == "TSLA":
            tesla_entity_ids.add(ent.id)

    # Tesla 연결 이벤트 ID
    link_repo = OntologyLinkRepository()
    tesla_event_ids: set[str] = set()
    for eid in tesla_entity_ids:
        for lk in link_repo.get_many(filters={"source_id": eid}, limit=200):
            if lk.target_type == "event":
                tesla_event_ids.add(lk.target_id)
        for lk in link_repo.get_many(filters={"target_id": eid}, limit=200):
            if lk.source_type == "event":
                tesla_event_ids.add(lk.source_id)

    # 이벤트 수집
    event_repo = OntologyEventRepository()
    all_events = event_repo.get_active()
    markers = []

    for ev in all_events:
        # 기간 필터
        if ev.started_at and ev.started_at < cutoff:
            continue

        sev_idx = severity_order.index(ev.severity) if ev.severity in severity_order else 3
        is_tesla = ev.id in tesla_event_ids
        is_macro_critical = ev.event_type == "macro" and ev.severity == "critical"

        # 필터링 로직 (B안)
        if tesla_only and not is_tesla:
            continue
        if not is_tesla and not is_macro_critical and sev_idx > min_idx:
            continue
        # moderate 이하 비테슬라 비크리티컬은 제외
        if not is_tesla and not is_macro_critical and sev_idx >= 2:
            continue

        cat_info = EVENT_CATEGORIES.get(ev.event_type, {"label": ev.event_type, "color": "#8b949e"})
        shape = SEVERITY_SHAPES.get(ev.severity, "square")

        # 날짜 포맷
        date_str = ev.started_at.strftime("%Y-%m-%d") if ev.started_at else ""
        if not date_str:
            continue

        markers.append({
            "time": date_str,
            "position": "aboveBar" if sev_idx <= 1 else "belowBar",
            "color": cat_info["color"],
            "shape": shape,
            "text": f"[{cat_info['label']}] {ev.title[:40]}",
            "id": ev.id,
            "title": ev.title,
            "event_type": ev.event_type,
            "severity": ev.severity,
            "is_tesla": is_tesla,
            "category_label": cat_info["label"],
            "story_thread": getattr(ev, "story_thread", "") or "",
        })

    # 날짜순 정렬 (lightweight-charts 요구사항)
    markers.sort(key=lambda m: m["time"])

    # 같은 날짜에 너무 많으면 중요한 것만 (최대 3개/일)
    from collections import defaultdict
    by_date: dict[str, list] = defaultdict(list)
    for m in markers:
        by_date[m["time"]].append(m)

    filtered = []
    for date, items in by_date.items():
        # critical 우선, tesla 우선 정렬
        items.sort(key=lambda x: (
            0 if x["severity"] == "critical" else 1 if x["severity"] == "major" else 2,
            0 if x["is_tesla"] else 1,
        ))
        filtered.extend(items[:3])

    filtered.sort(key=lambda m: m["time"])

    return {
        "symbol": symbol,
        "period": period,
        "total_events": len(all_events),
        "tesla_events": len(tesla_event_ids),
        "filtered_count": len(filtered),
        "markers": filtered,
    }
