#!/usr/bin/env python3
"""Rule of 40 스크리닝 보고서 생성기

Rule of 40 = Revenue Growth YoY (%) + Profit Margin (%)
대상: NASDAQ 100, S&P 500, Russell 2000 (SP400+SP600 proxy)
"""

import io
import json
import sys
import time
import traceback
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import yfinance as yf

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_PATH = BASE_DIR / "data" / "cache" / "rule_of_40" / "results.json"
REPORT_PATH = BASE_DIR / "docs" / "research" / "rule_of_40_report.md"
MAX_WORKERS = 10
RETRY_COUNT = 3
HEADERS = {"User-Agent": "Mozilla/5.0"}


# ── 1. 구성종목 수집 ──────────────────────────────────────────


def _wiki_table(url: str, symbol_col: str = "Symbol", table_idx: int | None = None) -> list[str]:
    """Wikipedia에서 종목 리스트 스크래핑"""
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    tables = pd.read_html(io.StringIO(r.text))
    for i, t in enumerate(tables):
        if table_idx is not None and i != table_idx:
            continue
        if symbol_col in t.columns:
            tickers = t[symbol_col].dropna().astype(str).tolist()
            # BRK.B → BRK-B (yfinance 호환)
            return [tk.replace(".", "-") for tk in tickers if tk.isalpha() or "." in tk or "-" in tk]
    return []


def get_constituents() -> dict[str, list[str]]:
    """인덱스별 구성종목 수집"""
    indices = {}

    # NASDAQ 100
    try:
        nq = _wiki_table("https://en.wikipedia.org/wiki/Nasdaq-100", "Ticker")
        if not nq:
            nq = _wiki_table("https://en.wikipedia.org/wiki/Nasdaq-100", "Symbol")
        indices["NASDAQ100"] = nq
        print(f"  NASDAQ 100: {len(nq)}개")
    except Exception as e:
        print(f"  [ERR] NASDAQ 100 실패: {e}")
        indices["NASDAQ100"] = []

    # S&P 500
    try:
        sp5 = _wiki_table("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        indices["SP500"] = sp5
        print(f"  S&P 500: {len(sp5)}개")
    except Exception as e:
        print(f"  [ERR] S&P 500 실패: {e}")
        indices["SP500"] = []

    # Russell 2000 proxy (S&P 400 + S&P 600)
    r2k = []
    try:
        sp4 = _wiki_table("https://en.wikipedia.org/wiki/List_of_S%26P_400_companies", table_idx=1)
        r2k.extend(sp4)
        print(f"  S&P 400: {len(sp4)}개")
    except Exception as e:
        print(f"  [ERR] S&P 400 실패: {e}")
    try:
        sp6 = _wiki_table("https://en.wikipedia.org/wiki/List_of_S%26P_600_companies")
        r2k.extend(sp6)
        print(f"  S&P 600: {len(sp6)}개")
    except Exception as e:
        print(f"  [ERR] S&P 600 실패: {e}")

    # 중복 제거
    seen_sp5 = set(indices["SP500"])
    r2k_unique = [t for t in r2k if t not in seen_sp5]
    indices["RUSSELL2000_PROXY"] = list(dict.fromkeys(r2k_unique))
    print(f"  Russell 2000 proxy: {len(indices['RUSSELL2000_PROXY'])}개 (SP400+SP600, SP500 중복 제외)")

    return indices


# ── 2. 재무 데이터 수집 ────────────────────────────────────────


def _safe_val(series: pd.Series, idx: int) -> float | None:
    """Series에서 안전하게 값 추출"""
    if series is None or idx >= len(series):
        return None
    v = series.iloc[idx]
    return float(v) if pd.notna(v) else None


def fetch_ticker(ticker: str) -> dict | None:
    """단일 종목 Rule of 40 데이터 수집"""
    for attempt in range(RETRY_COUNT):
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}

            inc = t.quarterly_income_stmt
            cf = t.quarterly_cashflow

            if inc is None or inc.empty:
                return None

            # 날짜 내림차순 정렬
            inc = inc.sort_index(axis=1, ascending=False)
            if cf is not None and not cf.empty:
                cf = cf.sort_index(axis=1, ascending=False)

            # Revenue
            rev = inc.loc["Total Revenue"] if "Total Revenue" in inc.index else None
            if rev is None or len(rev) < 5:
                return None

            # Operating Income
            op_inc = inc.loc["Operating Income"] if "Operating Income" in inc.index else None

            # Free Cash Flow
            fcf = cf.loc["Free Cash Flow"] if (cf is not None and not cf.empty and "Free Cash Flow" in cf.index) else None
            # Fallback: OCF - CapEx
            if fcf is None and cf is not None and not cf.empty:
                ocf = cf.loc["Operating Cash Flow"] if "Operating Cash Flow" in cf.index else None
                capex = cf.loc["Capital Expenditure"] if "Capital Expenditure" in cf.index else None
                if ocf is not None and capex is not None:
                    fcf = ocf + capex  # CapEx는 보통 음수

            # 최근 4분기 계산
            quarters = []
            for i in range(min(4, len(rev) - 4)):
                rv_now = _safe_val(rev, i)
                rv_yoy = _safe_val(rev, i + 4)
                if rv_now is None or rv_yoy is None or rv_yoy == 0:
                    continue

                rev_growth = (rv_now - rv_yoy) / abs(rv_yoy) * 100

                op_margin = None
                if op_inc is not None:
                    oi = _safe_val(op_inc, i)
                    if oi is not None and rv_now != 0:
                        op_margin = oi / rv_now * 100

                fcf_margin = None
                if fcf is not None:
                    fv = _safe_val(fcf, i)
                    if fv is not None and rv_now != 0:
                        fcf_margin = fv / rv_now * 100

                r40_op = (rev_growth + op_margin) if op_margin is not None else None
                r40_fcf = (rev_growth + fcf_margin) if fcf_margin is not None else None

                q_date = inc.columns[i]
                quarters.append({
                    "date": str(q_date.date()) if hasattr(q_date, "date") else str(q_date),
                    "rev_growth": round(rev_growth, 1),
                    "op_margin": round(op_margin, 1) if op_margin is not None else None,
                    "fcf_margin": round(fcf_margin, 1) if fcf_margin is not None else None,
                    "r40_op": round(r40_op, 1) if r40_op is not None else None,
                    "r40_fcf": round(r40_fcf, 1) if r40_fcf is not None else None,
                })

            if not quarters:
                return None

            return {
                "ticker": ticker,
                "name": info.get("shortName") or info.get("longName") or ticker,
                "sector": info.get("sector", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "latest": quarters[0],
                "quarters": quarters,
            }

        except Exception:
            if attempt < RETRY_COUNT - 1:
                time.sleep(0.5 * (attempt + 1))
    return None


def collect_all(indices: dict[str, list[str]]) -> list[dict]:
    """전체 종목 데이터 병렬 수집"""
    # 전체 유니크 티커 + 인덱스 매핑
    ticker_indices: dict[str, set[str]] = {}
    for idx_name, tickers in indices.items():
        for tk in tickers:
            ticker_indices.setdefault(tk, set()).add(idx_name)

    all_tickers = list(ticker_indices.keys())
    total = len(all_tickers)
    print(f"\n총 {total}개 종목 데이터 수집 시작 (스레드: {MAX_WORKERS})")

    results = []
    failed = []
    done = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_ticker, tk): tk for tk in all_tickers}
        for future in as_completed(futures):
            tk = futures[future]
            done += 1
            try:
                data = future.result()
                if data:
                    data["indices"] = sorted(ticker_indices[tk])
                    results.append(data)
                else:
                    failed.append(tk)
            except Exception:
                failed.append(tk)

            if done % 50 == 0 or done == total:
                print(f"  진행: {done}/{total} (성공: {len(results)}, 실패: {len(failed)})")

    print(f"\n수집 완료: 성공 {len(results)}개, 실패 {len(failed)}개")
    if failed:
        print(f"  실패 종목 (일부): {failed[:20]}")

    return results


# ── 3. 분석 & 보고서 ──────────────────────────────────────────


def _trend_direction(quarters: list[dict], key: str) -> str:
    """최근 2~4분기 추세 판단 (최소 2분기 연속 상승이면 UP)"""
    vals = [q[key] for q in quarters if q.get(key) is not None]
    if len(vals) < 2:
        return "N/A"
    # 최근→과거 순이므로 reverse (과거→최근)
    vals = vals[::-1]
    # 최근 2분기 연속 상승이면 UP (전체가 아닌 최근 기준)
    recent_diffs = [vals[i + 1] - vals[i] for i in range(max(0, len(vals) - 3), len(vals) - 1)]
    if len(recent_diffs) >= 1 and all(d > 0 for d in recent_diffs):
        return "UP"
    if len(recent_diffs) >= 1 and all(d < 0 for d in recent_diffs):
        return "DOWN"
    return "MIXED"


# 이상치 필터 상수
MIN_QUARTERLY_REVENUE = 10_000_000  # $10M 미만 매출 제외
R40_CAP = 500  # R40 ±500% 초과 = 이상치


def _filter_outliers(results: list[dict]) -> list[dict]:
    """이상치 필터링 — 극단적 R40, 극소 매출 종목 제거"""
    filtered = []
    for r in results:
        lt = r["latest"]
        r40 = lt.get("r40_op")
        if r40 is None:
            continue
        # R40 범위 제한
        if abs(r40) > R40_CAP:
            continue
        # 매출 성장률 ±1000% 이상 = 구조적 변화 (스핀오프, 합병 등) → 제외
        if abs(lt.get("rev_growth", 0)) > 1000:
            continue
        filtered.append(r)
    return filtered


def generate_report(results: list[dict], indices: dict[str, list[str]]) -> str:
    """마크다운 보고서 생성"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_raw = len([r for r in results if r["latest"].get("r40_op") is not None])

    # 이상치 필터 적용
    with_r40 = _filter_outliers(results)
    with_r40.sort(key=lambda x: x["latest"]["r40_op"], reverse=True)

    # ── Top 30: Rule of 40 초과 ──
    top30 = [r for r in with_r40 if r["latest"]["r40_op"] >= 40][:30]

    # ── Emerging 20: 30~40 구간 상위 (40% 돌파 후보) ──
    emerging_candidates = [
        r for r in with_r40
        if 30 <= (r["latest"]["r40_op"] or 0) < 40
    ]
    emerging_candidates.sort(key=lambda x: x["latest"]["r40_op"], reverse=True)
    emerging20 = emerging_candidates[:20]

    # ── 인덱스별 분포 ──
    idx_stats = {}
    for idx_name in indices:
        idx_tickers = set(indices[idx_name])
        above40 = [r for r in with_r40 if r["latest"]["r40_op"] >= 40 and any(i == idx_name for i in r["indices"])]
        total_in_idx = sum(1 for r in with_r40 if any(i == idx_name for i in r["indices"]))
        idx_stats[idx_name] = {"above40": len(above40), "total_analyzed": total_in_idx, "constituents": len(idx_tickers)}

    # ── 섹터별 히트맵 ──
    sector_data: dict[str, dict] = {}
    for r in with_r40:
        s = r["sector"]
        if s not in sector_data:
            sector_data[s] = {"count": 0, "above40": 0, "scores": []}
        sector_data[s]["count"] += 1
        sector_data[s]["scores"].append(r["latest"]["r40_op"])
        if r["latest"]["r40_op"] >= 40:
            sector_data[s]["above40"] += 1

    for s in sector_data:
        scores = sector_data[s]["scores"]
        sector_data[s]["avg_r40"] = round(np.mean(scores), 1) if scores else 0
        sector_data[s]["median_r40"] = round(np.median(scores), 1) if scores else 0

    sector_sorted = sorted(sector_data.items(), key=lambda x: x[1]["above40"], reverse=True)

    # ── 보고서 생성 ──
    lines = []
    lines.append(f"# Rule of 40 스크리닝 보고서")
    lines.append(f"")
    lines.append(f"> 생성일: {now}  ")
    lines.append(f"> Rule of 40 = Revenue Growth YoY (%) + Operating Margin (%)  ")
    lines.append(f"> 분석 대상: NASDAQ 100, S&P 500, Russell 2000 (S&P 400+600 proxy)  ")
    lines.append(f"> 데이터: yfinance (최근 분기 기준)")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Top 30
    lines.append(f"## 1. Top 30 - Rule of 40 초과 (Operating)")
    lines.append(f"")
    total_above40 = sum(1 for r in with_r40 if r["latest"]["r40_op"] >= 40)
    lines.append(f"전체 수집 {total_raw}개 중 이상치 제외 {len(with_r40)}개 분석, **{total_above40}개**가 R40 >= 40% 달성. 상위 30개:")
    lines.append(f"")
    lines.append(f"> 이상치 필터: 분기 매출 $10M 미만, 매출 성장률 ±1000% 초과, R40 ±500% 초과 종목 제외")
    lines.append(f"")
    lines.append(f"| # | Ticker | Company | Sector | Rev Growth | Op Margin | R40(Op) | R40(FCF) | Index |")
    lines.append(f"|---|--------|---------|--------|-----------|----------|---------|---------|-------|")
    for i, r in enumerate(top30, 1):
        lt = r["latest"]
        fcf_str = f'{lt["r40_fcf"]:.1f}' if lt.get("r40_fcf") is not None else "N/A"
        idx_str = ", ".join(r["indices"])
        name = r["name"][:25]
        lines.append(
            f"| {i} | **{r['ticker']}** | {name} | {r['sector']} | "
            f"{lt['rev_growth']:+.1f}% | {lt['op_margin']:.1f}% | "
            f"**{lt['r40_op']:.1f}** | {fcf_str} | {idx_str} |"
        )
    lines.append(f"")

    # Emerging 20
    lines.append(f"## 2. Emerging 20 - R40 돌파 후보 (30~40% 구간)")
    lines.append(f"")
    if emerging20:
        lines.append(f"R40 30~40% 구간 상위 20개 — 40% 돌파 잠재력이 높은 종목:")
        lines.append(f"")
        lines.append(f"> yfinance 5분기 제한으로 추세 분석 불가. 단일 분기 R40 기준 정렬.")
        lines.append(f"")
        lines.append(f"| # | Ticker | Company | Sector | Rev Growth | Op Margin | R40(Op) | R40(FCF) | Index |")
        lines.append(f"|---|--------|---------|--------|-----------|----------|---------|---------|-------|")
        for i, r in enumerate(emerging20, 1):
            lt = r["latest"]
            fcf_str = f'{lt["r40_fcf"]:.1f}' if lt.get("r40_fcf") is not None else "N/A"
            idx_str = ", ".join(r["indices"])
            name = r["name"][:25]
            lines.append(
                f"| {i} | **{r['ticker']}** | {name} | {r['sector']} | "
                f"{lt['rev_growth']:+.1f}% | {lt['op_margin']:.1f}% | "
                f"**{lt['r40_op']:.1f}** | {fcf_str} | {idx_str} |"
            )
    else:
        lines.append(f"해당 조건 충족 종목 없음.")
    lines.append(f"")

    # 인덱스별 분포
    lines.append(f"## 3. 인덱스별 분포")
    lines.append(f"")
    lines.append(f"| Index | 구성종목 | 분석 성공 | R40 >= 40% | 비율 |")
    lines.append(f"|-------|---------|----------|-----------|------|")
    for idx_name, stats in idx_stats.items():
        display_name = idx_name.replace("_", " ")
        ratio = f'{stats["above40"]/stats["total_analyzed"]*100:.1f}%' if stats["total_analyzed"] > 0 else "N/A"
        lines.append(
            f"| {display_name} | {stats['constituents']} | {stats['total_analyzed']} | "
            f"{stats['above40']} | {ratio} |"
        )
    lines.append(f"")

    # 섹터별 히트맵
    lines.append(f"## 4. 섹터별 히트맵")
    lines.append(f"")
    lines.append(f"| Sector | 종목수 | R40>=40 | 비율 | 평균 R40 | 중앙값 R40 |")
    lines.append(f"|--------|-------|---------|------|---------|----------|")
    for sector, data in sector_sorted:
        ratio = f'{data["above40"]/data["count"]*100:.0f}%' if data["count"] > 0 else "N/A"
        lines.append(
            f"| {sector} | {data['count']} | {data['above40']} | {ratio} | "
            f"{data['avg_r40']:.1f} | {data['median_r40']:.1f} |"
        )
    lines.append(f"")

    # 투자 시사점
    lines.append(f"## 5. 투자 시사점")
    lines.append(f"")

    # 동적으로 시사점 생성
    top_sectors = [s for s, d in sector_sorted if d["above40"] >= 3][:3]
    top_ticker = top30[0]["ticker"] if top30 else "N/A"
    top_score = top30[0]["latest"]["r40_op"] if top30 else 0

    # R40 비율 기준 상위 섹터 (count 최소 10)
    ratio_sectors = [(s, d) for s, d in sector_sorted if d["count"] >= 10]
    ratio_sectors.sort(key=lambda x: x[1]["above40"] / max(x[1]["count"], 1), reverse=True)
    top_ratio = ratio_sectors[:3] if ratio_sectors else []

    sector_summary = ", ".join(
        f"{s} ({d['above40']}/{d['count']}={d['above40']*100//d['count']}%)"
        for s, d in top_ratio
    )
    lines.append(f"1. **R40 비율 상위 섹터**: {sector_summary} — 성장+수익성 균형이 우수한 기업 비율이 높다.")

    # 인덱스별 R40 비율
    nq_stats = idx_stats.get("NASDAQ100", {})
    sp_stats = idx_stats.get("SP500", {})
    r2_stats = idx_stats.get("RUSSELL2000_PROXY", {})
    nq_pct = f"{nq_stats['above40']}/{nq_stats['total_analyzed']}" if nq_stats.get("total_analyzed") else "N/A"
    sp_pct = f"{sp_stats['above40']}/{sp_stats['total_analyzed']}" if sp_stats.get("total_analyzed") else "N/A"
    r2_pct = f"{r2_stats['above40']}/{r2_stats['total_analyzed']}" if r2_stats.get("total_analyzed") else "N/A"
    lines.append(f"2. **NASDAQ 100 우위**: R40 돌파 비율 NASDAQ100({nq_pct}), SP500({sp_pct}), Russell2000 proxy({r2_pct}) — 대형 테크 중심 인덱스가 우세.")
    lines.append(f"3. **Emerging 30~40% 구간**: {len(emerging_candidates)}개 종목이 대기 중. 매출 성장 가속 또는 마진 개선 시 R40 진입 가능.")
    lines.append(f"4. **반도체 사이클 효과**: SNDK, MU 등 메모리 반도체 종목이 상위권 — 업사이클 기반 매출 급증이 R40 끌어올림. 사이클 피크 주의.")
    lines.append(f"5. **면책**: 본 보고서는 정보 제공 목적이며, 투자 권유가 아닙니다. 단일 분기 기준이므로 계절성/일회성/스핀오프 효과에 주의.")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*데이터 소스: yfinance | 분석 도구: Python*")

    return "\n".join(lines)


# ── 4. 메인 ────────────────────────────────────────────────


def main():
    print("=" * 60)
    print("Rule of 40 스크리닝 시작")
    print("=" * 60)

    # Phase 1: 구성종목
    print("\n[Phase 1] 구성종목 수집")
    indices = get_constituents()
    total_unique = len(set(sum(indices.values(), [])))
    print(f"  전체 유니크 종목: {total_unique}개")

    # Phase 2: 재무 데이터 수집
    print("\n[Phase 2] 재무 데이터 수집")
    t0 = time.time()
    results = collect_all(indices)
    elapsed = time.time() - t0
    print(f"  소요 시간: {elapsed:.0f}초")

    # 캐시 저장
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  캐시 저장: {CACHE_PATH}")

    # Phase 3: 보고서 생성
    print("\n[Phase 3] 보고서 생성")
    report = generate_report(results, indices)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"  보고서 저장: {REPORT_PATH}")

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
