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


# 확장 기간 매핑 (SMA200 등 지표 워밍업용)
_EXTENDED_PERIOD = {
    "1mo": "1y", "3mo": "1y", "6mo": "2y", "1y": "2y",
    "2y": "5y", "5y": "max", "max": "max",
}
_PERIOD_DAYS = {
    "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365,
    "2y": 730, "5y": 1825, "max": 999999,
}


@router.get("/ohlcv")
def get_ohlcv(
    symbol: str = "TSLA",
    period: str = Query("6mo", pattern="^(1mo|3mo|6mo|1y|2y|5y|max)$"),
    interval: str = Query("1d", pattern="^(1h|4h|1d|1wk|1mo)$"),
) -> dict:
    """OHLCV 데이터 + 기술 지표를 반환한다.

    지표 워밍업을 위해 요청 기간보다 더 긴 데이터를 fetch한 후,
    지표 계산 → 요청 기간으로 트림하여 반환.
    """
    # 1. 확장 기간으로 데이터 fetch (SMA200 워밍업)
    extended_period = _EXTENDED_PERIOD.get(period, period)
    extended_records = _fetch_ohlcv(symbol, extended_period, interval)

    # 2. 전체 데이터로 지표 계산
    indicators = _compute_indicators(extended_records)

    # 3. 요청 기간으로 트림
    period_days = _PERIOD_DAYS.get(period, 999999)
    if period_days < 999999 and extended_records:
        last_time = extended_records[-1]["time"]
        if isinstance(last_time, int):
            start_ts = last_time - (period_days * 24 * 3600)
            trimmed = [r for r in extended_records if r["time"] >= start_ts]
        else:
            start_ts = int(datetime.strptime(str(last_time), "%Y-%m-%d").timestamp()) - (period_days * 86400)
            trimmed = [
                r for r in extended_records
                if int(datetime.strptime(str(r["time"]), "%Y-%m-%d").timestamp()) >= start_ts
            ]
        start_time = trimmed[0]["time"] if trimmed else None
    else:
        trimmed = extended_records
        start_time = None

    # 4. 지표 시리즈 트림
    def _trim(series: list[dict]) -> list[dict]:
        if not start_time or not series:
            return series
        if isinstance(start_time, int):
            return [s for s in series if s["time"] >= start_time]
        st = int(datetime.strptime(str(start_time), "%Y-%m-%d").timestamp())
        return [
            s for s in series
            if (s["time"] if isinstance(s["time"], int)
                else int(datetime.strptime(str(s["time"]), "%Y-%m-%d").timestamp())) >= st
        ]

    for key in ("rsi_series", "macd_series", "signal_series", "histogram_series"):
        if key in indicators:
            indicators[key] = _trim(indicators[key])

    if "sma" in indicators:
        for sma_key in indicators["sma"]:
            if "series" in indicators["sma"][sma_key]:
                indicators["sma"][sma_key]["series"] = _trim(indicators["sma"][sma_key]["series"])

    if "vwma100" in indicators and indicators["vwma100"] and "series" in indicators["vwma100"]:
        indicators["vwma100"]["series"] = _trim(indicators["vwma100"]["series"])

    interval_labels = {"1h": "1시간", "4h": "4시간", "1d": "일봉", "1wk": "주봉", "1mo": "월봉"}

    return {
        "symbol": symbol,
        "period": period,
        "interval": interval,
        "interval_label": interval_labels.get(interval, interval),
        "count": len(trimmed),
        "ohlcv": trimmed,
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


def _detect_pivot_points(records: list[dict], window: int = 5) -> dict:
    """OHLCV 레코드에서 피봇 하이/로우를 감지한다."""
    if len(records) < window * 2 + 1:
        return {"pivot_highs": [], "pivot_lows": []}

    pivot_highs = []
    pivot_lows = []

    for i in range(window, len(records) - window):
        curr_high = records[i]["high"]
        curr_low = records[i]["low"]

        is_pivot_high = all(
            records[j]["high"] < curr_high
            for j in range(i - window, i + window + 1)
            if j != i
        )
        is_pivot_low = all(
            records[j]["low"] > curr_low
            for j in range(i - window, i + window + 1)
            if j != i
        )

        if is_pivot_high:
            pivot_highs.append({"time": records[i]["time"], "price": curr_high, "index": i})
        if is_pivot_low:
            pivot_lows.append({"time": records[i]["time"], "price": curr_low, "index": i})

    return {"pivot_highs": pivot_highs, "pivot_lows": pivot_lows}


def _find_inbeom_trendlines(records: list[dict], pivot_window: int = 30) -> list[dict]:
    """인범 스타일 빗각 (고고저/저저고) — 거래량 변곡점 기반."""
    if len(records) < pivot_window * 2 + 1:
        return []

    pivots = _detect_pivot_points(records, window=pivot_window)
    pivot_highs = pivots["pivot_highs"]
    pivot_lows = pivots["pivot_lows"]
    if not pivot_highs or not pivot_lows:
        return []

    atr = sum(r["high"] - r["low"] for r in records) / len(records)
    tolerance = atr * 0.5
    current_time = records[-1]["time"]
    current_idx = len(records) - 1

    # 거래량 필터: 주변 20봉 평균 대비 1.3배 이상
    def _vol_filter(pvts: list[dict]) -> list[dict]:
        out = []
        for p in pvts:
            i = p["index"]
            ws, we = max(0, i - 10), min(len(records), i + 11)
            avg_vol = sum(records[k]["volume"] for k in range(ws, we)) / max(we - ws, 1)
            if avg_vol > 0 and records[i]["volume"] >= avg_vol * 1.3:
                out.append(p)
        return out if len(out) >= 2 else pvts

    vol_highs = _vol_filter(pivot_highs)
    vol_lows = _vol_filter(pivot_lows)

    def _pick_pair(pts: list[dict], top_pct: float = 0.7, recent_frac: float = 1.0) -> tuple | None:
        if len(pts) < 2:
            return None
        if recent_frac < 1.0:
            cutoff = int(len(records) * (1 - recent_frac))
            pts = [p for p in pts if p["index"] >= cutoff]
        else:
            prices = sorted(p["price"] for p in pts)
            thr = prices[int(len(prices) * top_pct)] if top_pct < 1.0 else 0
            pts = [p for p in pts if p["price"] >= thr]
        if len(pts) < 2:
            return None
        recent = sorted(pts, key=lambda x: x["index"], reverse=True)
        for i in range(len(recent)):
            for j in range(i + 1, len(recent)):
                if abs(recent[i]["index"] - recent[j]["index"]) >= 60:
                    return tuple(sorted([recent[i], recent[j]], key=lambda x: x["index"]))
        return tuple(sorted(recent[:2], key=lambda x: x["index"]))

    result = []

    # 고고저: 상위 30% 고점 2개 연결 → 하강 저항
    pair = _pick_pair(vol_highs, top_pct=0.7)
    if pair:
        p1, p2 = pair
        slope = (p2["price"] - p1["price"]) / (p2["index"] - p1["index"])
        ext = p1["price"] + slope * (current_idx - p1["index"])
        tc = sum(1 for ph in vol_highs if abs(ph["price"] - (p1["price"] + slope * (ph["index"] - p1["index"]))) <= tolerance)
        result.append({
            "pattern": "고고저", "type": "resistance",
            "start": {"time": p1["time"], "price": p1["price"], "index": p1["index"]},
            "end": {"time": p2["time"], "price": p2["price"], "index": p2["index"]},
            "slope": slope, "touch_count": tc,
            "extended": {"time": current_time, "price": ext},
            "target_label": "미래 저점 타겟", "volume_confirmed": True,
        })

    # 저저고: 후반 60% 저점 2개 연결 → 상승 지지
    pair = _pick_pair(vol_lows, top_pct=1.0, recent_frac=0.6)
    if pair:
        p1, p2 = pair
        slope = (p2["price"] - p1["price"]) / (p2["index"] - p1["index"])
        ext = p1["price"] + slope * (current_idx - p1["index"])
        tc = sum(1 for pl in vol_lows if abs(pl["price"] - (p1["price"] + slope * (pl["index"] - p1["index"]))) <= tolerance)
        result.append({
            "pattern": "저저고", "type": "support",
            "start": {"time": p1["time"], "price": p1["price"], "index": p1["index"]},
            "end": {"time": p2["time"], "price": p2["price"], "index": p2["index"]},
            "slope": slope, "touch_count": tc,
            "extended": {"time": current_time, "price": ext},
            "target_label": "미래 고점 타겟", "volume_confirmed": True,
        })

    return result


def _compute_inbeom_channel(records: list[dict], trendline: dict, pivot_window: int = 30) -> dict:
    """인범 빗각 기반 평행 채널 — 빗각을 복사해서 반대편에 붙임."""
    start_idx = trendline["start"]["index"]
    start_price = trendline["start"]["price"]
    slope = trendline["slope"]
    pattern = trendline["pattern"]
    last_idx = len(records) - 1

    def line_at(idx: int) -> float:
        return start_price + slope * (idx - start_idx)

    pivots = _detect_pivot_points(records, window=pivot_window)
    # 고고저 → 아래 피봇 로우 거리, 저저고 → 위 피봇 하이 거리
    if pattern == "고고저":
        dists = [line_at(p["index"]) - p["price"] for p in pivots["pivot_lows"]
                 if p["index"] >= start_idx and p["price"] < line_at(p["index"])]
    else:
        dists = [p["price"] - line_at(p["index"]) for p in pivots["pivot_highs"]
                 if p["index"] >= start_idx and p["price"] > line_at(p["index"])]

    if dists:
        dists.sort()
        ch_width = dists[min(int(len(dists) * 0.9), len(dists) - 1)]
    else:
        ch_width = sum(r["high"] - r["low"] for r in records) / len(records) * 10

    offset = -ch_width if pattern == "고고저" else ch_width

    def mk(extra: float) -> list[dict]:
        return [
            {"time": trendline["start"]["time"], "value": round(line_at(start_idx) + extra, 2)},
            {"time": trendline["end"]["time"], "value": round(line_at(trendline["end"]["index"]) + extra, 2)},
            {"time": records[last_idx]["time"], "value": round(line_at(last_idx) + extra, 2)},
        ]

    cur = records[last_idx]["close"]
    lo = min(line_at(last_idx), line_at(last_idx) + offset)
    hi = max(line_at(last_idx), line_at(last_idx) + offset)
    thr = abs(ch_width) * 0.1
    if cur > hi + thr: pos, lbl = "above_channel", "채널 상방 돌파"
    elif cur < lo - thr: pos, lbl = "below_channel", "채널 하방 이탈"
    elif cur >= hi - thr: pos, lbl = "near_resistance", "저항 근접"
    elif cur <= lo + thr: pos, lbl = "near_support", "지지 근접"
    elif cur > (lo + hi) / 2: pos, lbl = "upper_half", "채널 상부"
    else: pos, lbl = "lower_half", "채널 하부"

    # VP 교차
    atr = sum(r["high"] - r["low"] for r in records) / len(records)
    pmin, pmax = min(r["low"] for r in records), max(r["high"] for r in records)
    bsz = (pmax - pmin) / 30 if pmax > pmin else 1
    vb: dict[int, float] = {}
    for r in records:
        bi = min(int(((r["high"] + r["low"]) / 2 - pmin) / bsz), 29)
        vb[bi] = vb.get(bi, 0) + r["volume"]
    top3 = sorted(vb.items(), key=lambda x: x[1], reverse=True)[:3]
    vpp = [pmin + (b + 0.5) * bsz for b, _ in top3]
    cur_prim = line_at(last_idx)
    vpc = any(abs(cur_prim - v) <= atr * 0.5 for v in vpp)
    vpc_p = round(min(vpp, key=lambda v: abs(cur_prim - v)), 2) if vpc else None

    return {
        "primary": {"type": trendline["type"], "pattern": pattern,
                     "slope": round(slope, 4), "touch_count": trendline["touch_count"],
                     "line": mk(0)},
        "opposite": {"line": mk(offset)},
        "center": {"line": mk(offset / 2)},
        "channel_width": round(abs(ch_width), 2),
        "position": pos, "position_label": lbl,
        "current_primary_price": round(cur_prim, 2),
        "current_opposite_price": round(cur_prim + offset, 2),
        "current_center_price": round(cur_prim + offset / 2, 2),
        "vp_confluence": vpc, "vp_confluence_price": vpc_p,
    }


@router.get("/trendlines")
def get_trendlines(
    symbol: str = "TSLA",
    period: str = Query("1y", pattern="^(3mo|6mo|1y|2y|5y|max)$"),
    interval: str = Query("1d", pattern="^(1h|4h|1d|1wk|1mo)$"),
    pivot_window: int = Query(30, ge=5, le=50),
) -> dict:
    """인범 스타일 빗각(고고저/저저고) + 평행 채널 — 항상 MAX 데이터 기반."""
    max_records = _fetch_ohlcv(symbol, "max", interval)
    if len(max_records) < 100:
        return {"symbol": symbol, "channels": [], "trendlines": []}

    trendlines = _find_inbeom_trendlines(max_records, pivot_window=pivot_window)
    channels = [_compute_inbeom_channel(max_records, tl, pivot_window=pivot_window) for tl in trendlines]

    return {
        "symbol": symbol, "period": period, "interval": interval,
        "trendlines": [{
            "pattern": tl["pattern"], "type": tl["type"],
            "slope": round(tl["slope"], 4), "touch_count": tl["touch_count"],
            "start": tl["start"], "end": tl["end"],
            "extended": {"time": tl["extended"]["time"], "price": round(tl["extended"]["price"], 2)},
            "volume_confirmed": tl["volume_confirmed"],
        } for tl in trendlines],
        "channels": channels,
    }


@router.get("/signals")
def get_trend_signals(
    symbol: str = "TSLA",
    period: str = Query("6mo", pattern="^(1mo|3mo|6mo|1y|2y|5y|max)$"),
    interval: str = Query("1d", pattern="^(1h|4h|1d|1wk|1mo)$"),
) -> dict:
    """추세 매수 시그널 — VWMA100 크로스오버 기반."""
    records = _fetch_ohlcv(symbol, period, interval)

    if len(records) < 100:
        return {
            "symbol": symbol, "interval": interval, "signals": [],
            "current_trend": "INSUFFICIENT_DATA", "total_signals": 0,
        }

    import pandas_ta as ta

    df = pd.DataFrame(records)
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    volume = df["volume"].astype(float)

    vwma100 = ta.vwma(close, volume, length=100)
    rsi = ta.rsi(close, length=14)
    adx_result = ta.adx(high, low, close)
    adx = adx_result.iloc[:, 0] if adx_result is not None else None
    sma20 = ta.sma(close, length=20)
    sma50 = ta.sma(close, length=50)
    volume_ma20 = ta.sma(volume, length=20)

    signals = []
    for i in range(1, len(df)):
        curr_close = close.iloc[i]
        prev_close = close.iloc[i - 1]
        curr_vwma = vwma100.iloc[i] if pd.notna(vwma100.iloc[i]) else None
        prev_vwma = vwma100.iloc[i - 1] if pd.notna(vwma100.iloc[i - 1]) else None
        curr_rsi = rsi.iloc[i] if pd.notna(rsi.iloc[i]) else None
        curr_adx = adx.iloc[i] if adx is not None and pd.notna(adx.iloc[i]) else None
        curr_vol = volume.iloc[i]
        avg_vol = volume_ma20.iloc[i] if pd.notna(volume_ma20.iloc[i]) else curr_vol
        vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1

        if curr_vwma is None or prev_vwma is None or curr_rsi is None or curr_adx is None:
            continue

        cross_above = prev_close < prev_vwma and curr_close > curr_vwma
        cross_below = prev_close > prev_vwma and curr_close < curr_vwma
        time_val = records[i]["time"]

        if cross_above and curr_rsi > 40 and curr_adx > 20:
            sig_type = "STRONG_BUY" if vol_ratio >= 1.5 else "BUY"
            desc = "VWMA100 돌파 강력 매수 (거래량 확보)" if vol_ratio >= 1.5 else "VWMA100 돌파 매수"
            signals.append({
                "time": time_val, "type": sig_type, "price": round(curr_close, 2),
                "vwma100": round(curr_vwma, 2), "rsi": round(curr_rsi, 2),
                "adx": round(curr_adx, 2), "volume_ratio": round(vol_ratio, 2),
                "description": desc,
            })
        elif cross_below and curr_rsi < 60:
            signals.append({
                "time": time_val, "type": "SELL", "price": round(curr_close, 2),
                "vwma100": round(curr_vwma, 2), "rsi": round(curr_rsi, 2),
                "adx": round(curr_adx, 2), "volume_ratio": round(vol_ratio, 2),
                "description": "VWMA100 이탈 매도",
            })

    # 현재 추세
    last_close = close.iloc[-1]
    last_vwma = vwma100.iloc[-1] if pd.notna(vwma100.iloc[-1]) else None
    last_sma20 = sma20.iloc[-1] if pd.notna(sma20.iloc[-1]) else None
    last_sma50 = sma50.iloc[-1] if pd.notna(sma50.iloc[-1]) else None

    current_trend = "NEUTRAL"
    if last_vwma and last_sma20 and last_sma50:
        if last_close > last_vwma and last_sma20 > last_sma50:
            current_trend = "TREND_UP"
        elif last_close < last_vwma and last_sma20 < last_sma50:
            current_trend = "TREND_DOWN"

    return {
        "symbol": symbol, "interval": interval, "signals": signals,
        "current_trend": current_trend,
        "current_rsi": round(float(rsi.iloc[-1]), 2) if pd.notna(rsi.iloc[-1]) else None,
        "current_adx": round(float(adx.iloc[-1]), 2) if adx is not None and pd.notna(adx.iloc[-1]) else None,
        "total_signals": len(signals),
    }
