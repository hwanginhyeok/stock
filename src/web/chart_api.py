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
    importance_level: str = Query("important", pattern="^(core|important|all)$"),
) -> dict:
    """차트에 표시할 이벤트 마커를 importance 점수 기반으로 필터링하여 반환한다.

    importance = severity_score × relevance_score × freshness_score
    """
    from src.core.database import get_session, init_db
    from src.storage import OntologyEventRepository

    init_db()

    # 기간 계산
    period_days = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825, "max": 3650}
    cutoff = datetime.now() - timedelta(days=period_days.get(period, 180))

    # severity_score 매핑
    severity_scores = {
        "critical": 10,
        "major": 5,
        "moderate": 2,
        "minor": 1,
    }

    # relevance_score 키워드 매핑
    direct_keywords = [
        "Tesla", "TSLA", "테슬라", "Musk", "머스크", "FSD", "Robotaxi", "로보택시",
        "Cybertruck", "사이버트럭", "Optimus", "옵티머스", "Megapack", "메가팩",
        "Gigafactory", "기가팩토리", "xAI", "SpaceX", "스페이스X",
    ]
    indirect_keywords = [
        "EV", "전기차", "자율주행", "autonomous", "AI 반도체", "AI chip",
        "엔비디아", "NVIDIA", "관세", "tariff", "EV 보조금", "배터리",
        "리튬", "lithium", "충전", "charging",
    ]
    macro_keywords = [
        "inflation", "인플레이션", "recession", "침체", "GDP", "유동성",
        "liquidity", "S&P", "NASDAQ", "나스닥", "Fed", "연준", "금리",
        "FOMC", "환율",
    ]

    def _calculate_relevance(title: str) -> tuple[int, str]:
        """제목에서 relevance_score와 라벨을 계산."""
        title_lower = title.lower()
        for kw in direct_keywords:
            if kw.lower() in title_lower:
                return 5, "직접"
        for kw in indirect_keywords:
            if kw.lower() in title_lower:
                return 3, "간접"
        for kw in macro_keywords:
            if kw.lower() in title_lower:
                return 2, "거시"
        return 1, "기타"

    def _calculate_freshness(started_at: datetime | None) -> float:
        """신선도 점수 계산."""
        if not started_at:
            return 0.1
        now = datetime.now()
        delta = (now - started_at).days
        if delta <= 1:
            return 1.0
        elif delta <= 7:
            return 0.8
        elif delta <= 30:
            return 0.5
        elif delta <= 90:
            return 0.3
        else:
            return 0.1

    # 이벤트 수집 및 점수 계산
    event_repo = OntologyEventRepository()
    all_events = event_repo.get_active()
    scored_markers = []

    for ev in all_events:
        # 기간 필터
        if ev.started_at and ev.started_at < cutoff:
            continue

        # severity_score
        sev_score = severity_scores.get(ev.severity, 1)

        # relevance_score
        rel_score, rel_label = _calculate_relevance(ev.title)

        # freshness_score
        fresh_score = _calculate_freshness(ev.started_at)

        # importance 계산
        importance = sev_score * rel_score * fresh_score

        # 점수가 0이면 스킵
        if importance < 1:
            continue

        # 날짜 포맷
        date_str = ev.started_at.strftime("%Y-%m-%d") if ev.started_at else ""
        if not date_str:
            continue

        cat_info = EVENT_CATEGORIES.get(ev.event_type, {"label": ev.event_type, "color": "#8b949e"})
        shape = SEVERITY_SHAPES.get(ev.severity, "square")

        scored_markers.append({
            "time": date_str,
            "title": ev.title,
            "category_label": cat_info["label"],
            "color": cat_info["color"],
            "severity": ev.severity,
            "event_type": ev.event_type,
            "importance": importance,
            "relevance_label": rel_label,
            "is_tesla_direct": rel_score == 5,
            "shape": shape,
            "position": "aboveBar" if importance >= 10 else "belowBar",
            "story_thread": getattr(ev, "story_thread", "") or "",
            "id": ev.id,
        })

    # importance_level 기반 필터
    if importance_level == "core":
        min_importance = 15
        max_per_day = 2
        max_total = 5
    elif importance_level == "important":
        min_importance = 6
        max_per_day = 3
        max_total = 15
    else:  # all
        min_importance = 1
        max_per_day = 3
        max_total = 50

    # 점수 기준 필터
    filtered = [m for m in scored_markers if m["importance"] >= min_importance]

    # 같은 날짜 중복 제거 (최대 N개/일)
    from collections import defaultdict
    by_date: dict[str, list] = defaultdict(list)
    for m in filtered:
        by_date[m["time"]].append(m)

    deduped = []
    for date, items in by_date.items():
        # importance 내림차순 정렬
        items.sort(key=lambda x: x["importance"], reverse=True)
        deduped.extend(items[:max_per_day])

    # importance 내림차순 정렬 후 상위 N개
    deduped.sort(key=lambda m: m["importance"], reverse=True)
    final_markers = deduped[:max_total]

    # 다시 �짜순 정렬
    final_markers.sort(key=lambda m: m["time"])

    return {
        "symbol": symbol,
        "period": period,
        "importance_level": importance_level,
        "total_events": len(all_events),
        "scored_count": len(scored_markers),
        "filtered_count": len(final_markers),
        "markers": final_markers,
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


@router.get("/strategy")
def get_trend_strategy(
    symbol: str = "TSLA",
    period: str = Query("6mo", pattern="^(1mo|3mo|6mo|1y|2y|5y|max)$"),
    interval: str = Query("1d", pattern="^(1h|4h|1d|1wk|1mo)$"),
) -> dict:
    """정배열/역배열 + 눌림목 시그널 — 빅테크 눌림목 매수 전략."""
    extended_period = _EXTENDED_PERIOD.get(period, period)
    records = _fetch_ohlcv(symbol, extended_period, interval)

    if len(records) < 100:
        return {
            "symbol": symbol,
            "interval": interval,
            "current_state": "INSUFFICIENT_DATA",
            "current_state_label": "데이터 부족",
            "current_sma": {},
            "signals": [],
            "state_history": [],
            "total_signals": 0,
        }

    import pandas_ta as ta

    df = pd.DataFrame(records)
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)

    sma5 = ta.sma(close, length=5)
    sma10 = ta.sma(close, length=10)
    sma20 = ta.sma(close, length=20)
    sma50 = ta.sma(close, length=50)
    sma100 = ta.sma(close, length=100)

    def _get_state(idx: int) -> str | None:
        if not all(pd.notna([sma5.iloc[idx], sma10.iloc[idx], sma20.iloc[idx], sma50.iloc[idx], sma100.iloc[idx]])):
            return None
        s5, s10, s20, s50, s100 = sma5.iloc[idx], sma10.iloc[idx], sma20.iloc[idx], sma50.iloc[idx], sma100.iloc[idx]
        if s5 > s10 > s20 > s50 > s100:
            return "PERFECT_ORDER"
        elif s5 < s10 < s20 < s50 < s100:
            return "REVERSE_ORDER"
        else:
            return "TRANSITION"

    signals = []
    state_history = []
    prev_state = None

    for i in range(1, len(df)):
        state = _get_state(i)
        if state is None:
            continue

        time_val = records[i]["time"]
        curr_close = close.iloc[i]
        curr_low = low.iloc[i]
        curr_high = high.iloc[i]
        prev_close = close.iloc[i - 1]

        state_history.append({"time": time_val, "state": state})

        if prev_state != state:
            if state == "PERFECT_ORDER" and prev_state in (None, "TRANSITION", "REVERSE_ORDER"):
                signals.append({
                    "time": time_val,
                    "type": "PERFECT_ORDER_START",
                    "label": "정배열 진입",
                    "price": round(curr_close, 2),
                    "color": "#26a69a",
                    "text": "PO",
                })
            elif state == "TRANSITION" and prev_state == "PERFECT_ORDER":
                signals.append({
                    "time": time_val,
                    "type": "WEAK_SELL",
                    "label": "점진 매도",
                    "price": round(curr_close, 2),
                    "color": "#f59e0b",
                    "text": "W",
                })
            elif state == "REVERSE_ORDER" and prev_state in ("PERFECT_ORDER", "TRANSITION"):
                signals.append({
                    "time": time_val,
                    "type": "STRONG_SELL",
                    "label": "추세 붕괴",
                    "price": round(curr_close, 2),
                    "color": "#ef5350",
                    "text": "BR",
                })

        prev_state = state

    for i in range(2, len(df)):
        state = _get_state(i)
        prev_state = _get_state(i - 1)
        if state != "PERFECT_ORDER" or state is None:
            continue

        time_val = records[i]["time"]
        curr_low = low.iloc[i]
        curr_close = close.iloc[i]
        next_close = close.iloc[i + 1] if i + 1 < len(df) else None

        if next_close is None:
            continue

        s20 = sma20.iloc[i] if pd.notna(sma20.iloc[i]) else None
        s50 = sma50.iloc[i] if pd.notna(sma50.iloc[i]) else None

        touched_ma = None
        ma_value = None

        if s20 and abs(curr_low - s20) / s20 <= 0.02:
            touched_ma = "SMA20"
            ma_value = s20
        elif s50 and abs(curr_low - s50) / s50 <= 0.02:
            touched_ma = "SMA50"
            ma_value = s50

        if touched_ma and next_close > curr_close:
            signals.append({
                "time": time_val,
                "type": "PULLBACK_BUY",
                "label": "눌림목 매수",
                "price": round(curr_close, 2),
                "touched_ma": touched_ma,
                "ma_value": round(ma_value, 2),
                "color": "#3fb950",
                "text": "PB",
            })

    for i in range(1, len(df)):
        state = _get_state(i)
        if state != "REVERSE_ORDER" or state is None:
            continue

        time_val = records[i]["time"]
        curr_high = high.iloc[i]
        curr_close = close.iloc[i]
        prev_close = close.iloc[i - 1]

        s20 = sma20.iloc[i] if pd.notna(sma20.iloc[i]) else None

        if s20 and abs(curr_high - s20) / s20 <= 0.02 and curr_close < prev_close:
            signals.append({
                "time": time_val,
                "type": "BOUNCE_SELL",
                "label": "반등 매도",
                "price": round(curr_close, 2),
                "touched_ma": "SMA20",
                "ma_value": round(s20, 2),
                "color": "#ef5350",
                "text": "RS",
            })

    signals.sort(key=lambda x: x["time"])

    current_state = _get_state(len(df) - 1)
    state_labels = {
        "PERFECT_ORDER": "정배열",
        "REVERSE_ORDER": "역배열",
        "TRANSITION": "과도기",
    }

    current_sma = {}
    if all(pd.notna([sma5.iloc[-1], sma10.iloc[-1], sma20.iloc[-1], sma50.iloc[-1], sma100.iloc[-1]])):
        current_sma = {
            "5": round(float(sma5.iloc[-1]), 2),
            "10": round(float(sma10.iloc[-1]), 2),
            "20": round(float(sma20.iloc[-1]), 2),
            "50": round(float(sma50.iloc[-1]), 2),
            "100": round(float(sma100.iloc[-1]), 2),
        }

    return {
        "symbol": symbol,
        "interval": interval,
        "current_state": current_state or "UNKNOWN",
        "current_state_label": state_labels.get(current_state, "알 수 없음"),
        "current_sma": current_sma,
        "signals": signals,
        "state_history": state_history[-30:] if len(state_history) > 30 else state_history,
        "total_signals": len(signals),
    }
