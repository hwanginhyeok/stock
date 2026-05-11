#!/usr/bin/env python3
"""Rule of 40 — 실패 종목 재시도 (배치 + 캐시 리셋)"""

import io
import json
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests
import warnings

warnings.filterwarnings("ignore")

# 메인 스크립트에서 fetch 함수 재사용
import sys
sys.path.insert(0, str(Path(__file__).parent))
from rule_of_40_screen import fetch_ticker, _wiki_table, generate_report

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_PATH = BASE_DIR / "data" / "cache" / "rule_of_40" / "results.json"
REPORT_PATH = BASE_DIR / "docs" / "research" / "rule_of_40_report.md"
YF_CACHE = os.path.expanduser("~/.cache/py-yfinance")

HEADERS = {"User-Agent": "Mozilla/5.0"}
BATCH_SIZE = 40
BATCH_DELAY = 3  # 배치 사이 대기(초)
MAX_WORKERS = 5


def get_all_tickers_with_indices() -> dict[str, list[str]]:
    """구성종목 + 인덱스 매핑 재수집"""
    indices = {}
    nq = _wiki_table("https://en.wikipedia.org/wiki/Nasdaq-100", "Ticker")
    if not nq:
        nq = _wiki_table("https://en.wikipedia.org/wiki/Nasdaq-100", "Symbol")
    indices["NASDAQ100"] = nq

    sp5 = _wiki_table("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    indices["SP500"] = sp5

    r2k = []
    try:
        sp4 = _wiki_table("https://en.wikipedia.org/wiki/List_of_S%26P_400_companies", table_idx=1)
        r2k.extend(sp4)
    except:
        pass
    try:
        sp6 = _wiki_table("https://en.wikipedia.org/wiki/List_of_S%26P_600_companies")
        r2k.extend(sp6)
    except:
        pass
    seen = set(sp5)
    indices["RUSSELL2000_PROXY"] = list(dict.fromkeys(t for t in r2k if t not in seen))

    # ticker → indices 매핑
    ticker_map: dict[str, list[str]] = {}
    for idx_name, tickers in indices.items():
        for tk in tickers:
            ticker_map.setdefault(tk, []).append(idx_name)

    return ticker_map, indices


def clear_yf_cache():
    """yfinance 캐시 삭제"""
    if os.path.exists(YF_CACHE):
        shutil.rmtree(YF_CACHE)


def main():
    # 기존 캐시 로드
    with open(CACHE_PATH) as f:
        existing = json.load(f)
    success_set = {r["ticker"] for r in existing}
    print(f"기존 성공: {len(success_set)}개")

    # 전체 종목 + 인덱스 매핑
    ticker_map, indices = get_all_tickers_with_indices()
    all_tickers = list(ticker_map.keys())
    missing = [t for t in all_tickers if t not in success_set]
    print(f"재시도 대상: {len(missing)}개")

    if not missing:
        print("재시도 대상 없음.")
        return

    # 배치 처리
    new_results = []
    new_failed = []
    total = len(missing)

    for batch_start in range(0, total, BATCH_SIZE):
        batch = missing[batch_start:batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

        # 매 3배치마다 캐시 삭제 (크럼 갱신)
        if batch_num % 3 == 1:
            clear_yf_cache()

        print(f"  배치 {batch_num}/{total_batches} ({len(batch)}개)")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(fetch_ticker, tk): tk for tk in batch}
            for future in as_completed(futures):
                tk = futures[future]
                try:
                    data = future.result()
                    if data:
                        data["indices"] = sorted(ticker_map.get(tk, []))
                        new_results.append(data)
                    else:
                        new_failed.append(tk)
                except Exception:
                    new_failed.append(tk)

        done = batch_start + len(batch)
        print(f"    누적: 신규 성공 {len(new_results)}, 실패 {len(new_failed)} (진행: {done}/{total})")

        if batch_start + BATCH_SIZE < total:
            time.sleep(BATCH_DELAY)

    # 병합
    merged = existing + new_results
    print(f"\n병합 결과: {len(merged)}개 (기존 {len(existing)} + 신규 {len(new_results)})")
    print(f"최종 실패: {len(new_failed)}개")

    # 캐시 저장
    with open(CACHE_PATH, "w") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # 보고서 재생성
    report = generate_report(merged, indices)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"보고서 갱신: {REPORT_PATH}")


if __name__ == "__main__":
    main()
