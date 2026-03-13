"""옵션 내재 변동성(IV) 기반 1σ/2σ 예상 가격대 리포트.

각 기간(1주일, 1개월)별 시그마 밴드를 산출한다.
- 장중: 옵션 ATM IV 사용
- 장외/데이터 미제공: 20일 실현 변동성(HV) 폴백

Usage::

    python scripts/iv_sigma_report.py AAPL NVDA TSLA       # 개별 종목
    python scripts/iv_sigma_report.py --top 20              # 시가총액 상위 20
    python scripts/iv_sigma_report.py --index ndx100        # NASDAQ 100 전체
    python scripts/iv_sigma_report.py AAPL --json           # JSON 출력
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from typing import Any

import numpy as np
import yfinance as yf

from src.core.logger import get_logger

logger = get_logger("iv_sigma_report")

# 목표 기간 (캘린더 일)
def _days_to_friday() -> int:
    """이번 주 금요일까지 캘린더 일수.

    월~금: 해당 주 금요일. 토·일: 다음 주 금요일.
    """
    weekday = datetime.now().weekday()  # 0=Mon ... 6=Sun
    if weekday <= 4:  # Mon~Fri → this Friday
        return 4 - weekday
    return 4 + (7 - weekday)  # Sat(6d) / Sun(5d) → next Friday


_PERIODS = {
    "주간": _days_to_friday(),
    "1개월": 30,
}

# 유효 IV 최소 기준 (이보다 낮으면 깨진 데이터)
_MIN_VALID_IV = 0.02  # 2%

# 만기 DTE 최소값 (0 = 당일 만기도 허용 — 주간 시그마에서 금요일 만기 사용)
_MIN_DTE = 0

# 시가총액 상위 20
_TOP20 = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
    "META", "TSLA", "BRK-B", "AVGO", "JPM",
    "LLY", "V", "UNH", "XOM", "MA",
    "COST", "HD", "PG", "JNJ", "NFLX",
]


# ─── 변동성 산출 ────────────────────────────────────────────


def _compute_hv(ticker_obj: Any, window: int = 20) -> float | None:
    """20일 실현 변동성(HV)을 연율화하여 산출.

    Args:
        ticker_obj: yfinance Ticker 객체.
        window: 이동 기간 (거래일).

    Returns:
        연율화 HV (소수) 또는 None.
    """
    hist = ticker_obj.history(period="3mo")
    if len(hist) < window + 1:
        return None

    log_returns = np.log(hist["Close"] / hist["Close"].shift(1)).dropna()
    if len(log_returns) < window:
        return None

    hv = float(log_returns.rolling(window).std().iloc[-1]) * math.sqrt(252)
    return round(hv, 4) if not math.isnan(hv) else None


def _get_atm_iv_from_chain(
    chain_calls: Any,
    chain_puts: Any,
    price: float,
) -> float | None:
    """콜/풋 ATM IV 평균 산출. 유효하지 않으면 None.

    Args:
        chain_calls: 콜 체인 DataFrame.
        chain_puts: 풋 체인 DataFrame.
        price: 현재 주가.

    Returns:
        ATM IV (소수) 또는 None.
    """
    ivs: list[float] = []

    for chain in [chain_calls, chain_puts]:
        if chain.empty or "strike" not in chain.columns:
            continue
        c = chain.copy()
        c["dist"] = (c["strike"] - price).abs()
        atm = c.loc[c["dist"].idxmin()]
        iv = atm.get("impliedVolatility")
        if iv is not None and not math.isnan(iv) and iv >= _MIN_VALID_IV:
            ivs.append(float(iv))

    return sum(ivs) / len(ivs) if ivs else None


def _get_options_iv(
    ticker_obj: Any,
    price: float,
    target_days: int,
    *,
    friday_only: bool = False,
) -> tuple[float | None, str | None, int | None]:
    """목표 기간에 근접한 만기의 ATM IV를 반환.

    Args:
        ticker_obj: yfinance Ticker.
        price: 현재 주가.
        target_days: 목표 캘린더 일.
        friday_only: True이면 금요일 만기만 후보로 사용.
            금요일 만기가 없으면 전체 후보로 폴백.

    Returns:
        (IV, 사용된 만기 문자열, DTE) 또는 (None, None, None).
    """
    try:
        exps = ticker_obj.options
    except Exception:
        return None, None, None

    if not exps:
        return None, None, None

    now = datetime.now(tz=timezone.utc)
    candidates = []
    for exp_str in exps:
        exp_date = datetime.strptime(exp_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        dte = (exp_date - now).days
        if dte >= _MIN_DTE:
            candidates.append((exp_str, dte, exp_date.weekday()))

    if not candidates:
        return None, None, None

    # 금요일 만기 필터 (weekday 4 = Friday)
    if friday_only:
        fri_candidates = [(e, d, w) for e, d, w in candidates if w == 4]
        if fri_candidates:
            candidates = fri_candidates

    # target_days에 가장 가까운 만기
    best_exp, best_dte, _ = min(candidates, key=lambda x: abs(x[1] - target_days))

    try:
        chain = ticker_obj.option_chain(best_exp)
    except Exception:
        return None, None, None

    iv = _get_atm_iv_from_chain(chain.calls, chain.puts, price)
    return iv, best_exp, best_dte


# ─── 시그마 밴드 계산 ───────────────────────────────────────


def _compute_sigma_bands(
    price: float,
    vol: float,
    days: int,
) -> dict[str, Any]:
    """고정 기간에 대한 1σ/2σ 가격대 산출.

    Args:
        price: 현재 주가.
        vol: 연간 변동성 (소수).
        days: 캘린더 일 수.

    Returns:
        시그마 밴드.
    """
    sigma = price * vol * math.sqrt(days / 365)

    return {
        "sigma_move": round(sigma, 2),
        "sigma_move_pct": round(sigma / price * 100, 2),
        "sigma_1": {
            "upper": round(price + sigma, 2),
            "lower": round(price - sigma, 2),
        },
        "sigma_2": {
            "upper": round(price + sigma * 2, 2),
            "lower": round(price - sigma * 2, 2),
        },
    }


# ─── 종목 분석 ──────────────────────────────────────────────


def analyze_ticker(ticker: str) -> dict[str, Any]:
    """단일 종목의 시그마 밴드 분석.

    옵션 IV를 우선 사용하고, 유효하지 않으면 20일 HV로 폴백.

    Args:
        ticker: 미국 주식 티커.

    Returns:
        분석 결과 딕셔너리.
    """
    try:
        yf_ticker = yf.Ticker(ticker)
        hist = yf_ticker.history(period="3mo")
        if hist.empty:
            return {"ticker": ticker, "status": "error", "error": "가격 데이터 없음"}
        price = float(hist["Close"].iloc[-1])
    except Exception as e:
        return {"ticker": ticker, "status": "error", "error": str(e)}

    # 20일 실현 변동성 (항상 계산)
    hv = _compute_hv(yf_ticker)

    periods: dict[str, Any] = {}

    for label, target_days in _PERIODS.items():
        # 1) 옵션 IV 시도 (주간 → 금요일 만기만 사용)
        opt_iv, exp_used, exp_dte = _get_options_iv(
            yf_ticker, price, target_days, friday_only=(label == "주간"),
        )

        # 2) 사용할 변동성 결정
        if opt_iv is not None:
            vol = opt_iv
            vol_source = "IV"
            vol_detail = f"만기 {exp_used} (DTE {exp_dte})"
        elif hv is not None:
            vol = hv
            vol_source = "HV20"
            vol_detail = "20일 실현 변동성"
        else:
            periods[label] = {"error": "변동성 데이터 없음"}
            continue

        # 주간: 실제 만기 DTE로 시그마 계산
        sigma_days = exp_dte if exp_dte else target_days
        band = _compute_sigma_bands(price, vol, sigma_days)
        band["vol"] = round(vol, 4)
        band["vol_pct"] = round(vol * 100, 1)
        band["vol_source"] = vol_source
        band["vol_detail"] = vol_detail
        if exp_used:
            band["expiry_used"] = exp_used
            band["expiry_dte"] = exp_dte
        # 주간 라벨에 실제 만기일/DTE 표시
        actual_label = f"{label}({exp_used},{sigma_days}d)" if exp_used and label == "주간" else label
        periods[actual_label] = band

    has_valid = any("sigma_1" in v for v in periods.values())
    if not has_valid:
        return {"ticker": ticker, "status": "no_data", "error": "분석 불가"}

    return {
        "ticker": ticker,
        "status": "ok",
        "current_price": price,
        "hv20": round(hv * 100, 1) if hv else None,
        "periods": periods,
    }


# ─── 출력 ───────────────────────────────────────────────────


def _print_table(results: list[dict[str, Any]]) -> None:
    """분석 결과를 테이블 형식으로 출력."""
    ok_results = [r for r in results if r.get("status") == "ok"]
    failed = [r for r in results if r.get("status") != "ok"]

    if not ok_results:
        print("\n[!] 분석 가능한 종목이 없습니다.")
        for f in failed:
            print(f"  {f['ticker']}: {f.get('error', 'unknown')}")
        return

    print()
    print("=" * 115)
    print("  옵션 IV / 실현 변동성 기반 시그마 가격대 리포트")
    print("  1σ = 68.2% 확률 구간  |  2σ = 95.4% 확률 구간")
    print("=" * 115)

    for r in ok_results:
        ticker = r["ticker"]
        price = r["current_price"]
        hv_str = f"HV20: {r['hv20']:.1f}%" if r.get("hv20") else ""

        print()
        print(f"  {ticker:<6}  현재가: ${price:>10,.2f}   {hv_str}")
        print(f"  {'─' * 111}")
        print(
            f"  {'기간':<7}{'소스':>5}{'연율 Vol':>10}"
            f"  {'±1σ':>8}"
            f"  {'1σ 하단':>11} ~ {'1σ 상단':<11}"
            f"  {'±2σ':>8}"
            f"  {'2σ 하단':>11} ~ {'2σ 상단':<11}"
        )
        print(f"  {'─' * 111}")

        for label, band in r["periods"].items():
            if "error" in band:
                print(f"  {label:<7} {band['error']}")
                continue

            s1 = band["sigma_1"]
            s2 = band["sigma_2"]
            src = band["vol_source"]
            vol_pct = band["vol_pct"]
            move = band["sigma_move"]
            move_pct = band["sigma_move_pct"]

            print(
                f"  {label:<7}"
                f" {src:>4}"
                f"  {vol_pct:>6.1f}%"
                f"  ${move:>6.2f}"
                f"  ${s1['lower']:>10,.2f} ~ ${s1['upper']:>10,.2f}"
                f"  ${move * 2:>6.2f}"
                f"  ${s2['lower']:>10,.2f} ~ ${s2['upper']:>10,.2f}"
            )

    if failed:
        print(f"\n  실패 ({len(failed)}개):", end="")
        print("  " + ", ".join(f['ticker'] for f in failed))

    print()


# ─── CLI ─────────────────────────────────────────────────────


def _get_tickers(args: argparse.Namespace) -> list[str]:
    """CLI 인자에서 티커 목록 결정."""
    if args.tickers:
        return [t.upper() for t in args.tickers]

    if args.index:
        from src.collectors.market.constituents import (
            fetch_ndx100_tickers,
            fetch_sp500_tickers,
            get_combined_universe,
        )
        if args.index == "sp500":
            return fetch_sp500_tickers()
        if args.index == "ndx100":
            return fetch_ndx100_tickers()
        return get_combined_universe()

    if args.top:
        return _TOP20[:args.top]

    return _TOP20


def main() -> None:
    """CLI 엔트리포인트."""
    parser = argparse.ArgumentParser(
        description="옵션 IV 기반 1σ/2σ 예상 가격대 리포트",
    )
    parser.add_argument(
        "tickers", nargs="*", help="분석할 티커 (예: AAPL NVDA TSLA)",
    )
    parser.add_argument(
        "--top", type=int, default=None,
        help="시가총액 상위 N개 (기본 20)",
    )
    parser.add_argument(
        "--index", choices=["sp500", "ndx100", "all"], default=None,
        help="인덱스 전체 종목",
    )
    parser.add_argument(
        "--delay", type=float, default=1.0,
        help="요청 간 딜레이(초) (기본: 1.0)",
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="JSON 형식 출력",
    )
    args = parser.parse_args()

    tickers = _get_tickers(args)
    if not tickers:
        print("[!] 분석할 종목이 없습니다.")
        sys.exit(1)

    print(f"[*] {len(tickers)}개 종목 시그마 분석 시작...")

    results: list[dict[str, Any]] = []
    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i}/{len(tickers)}] {ticker}...", end="", flush=True)
        result = analyze_ticker(ticker)
        results.append(result)

        if result["status"] == "ok":
            first_period = next(iter(result.get("periods", {}).values()), {})
            src = first_period.get("vol_source", "?")
            vol = first_period.get("vol_pct", 0)
            print(f" {src} {vol:.1f}%")
        else:
            print(f" {result.get('error', 'failed')}")

        if i < len(tickers):
            time.sleep(args.delay)

    if args.json_output:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        _print_table(results)


if __name__ == "__main__":
    main()
