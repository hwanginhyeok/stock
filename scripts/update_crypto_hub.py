"""리서치 허브 크립토 현황 업데이트 스크립트.

CryptoCollector로 최신 데이터를 수집하여
data/research/crypto/bitcoin/current.md 및
data/research/crypto/ethereum/current.md 를 갱신한다.

기존 narrative 파일(overview.md, ecosystem.md 등)은 수동 관리 — 이 스크립트는 건드리지 않는다.
current.md 파일만 매번 덮어쓴다.

Usage::

    python scripts/update_crypto_hub.py
    python scripts/update_crypto_hub.py --dry-run   # 파일 저장 없이 출력만
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import certifi as _certifi

# Fix non-ASCII path issue for yfinance's curl_cffi
_cert_src = Path(_certifi.where())
try:
    str(_cert_src).encode("ascii")
except (UnicodeEncodeError, UnicodeDecodeError):
    _cert_dst = Path(os.environ.get("TEMP", "/tmp")) / "yf_certs" / "cacert.pem"
    if not _cert_dst.exists() or _cert_dst.stat().st_size != _cert_src.stat().st_size:
        _cert_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_cert_src, _cert_dst)
    os.environ.setdefault("CURL_CA_BUNDLE", str(_cert_dst))

from src.collectors.crypto.crypto_collector import CryptoCollector
from src.core.config import PROJECT_ROOT
from src.core.logger import get_logger

logger = get_logger("update_crypto_hub")

_CRYPTO_ROOT = PROJECT_ROOT / "data" / "research" / "crypto"
_BTC_DIR = _CRYPTO_ROOT / "bitcoin"
_ETH_DIR = _CRYPTO_ROOT / "ethereum"


def _fmt_pct(val: float | None) -> str:
    """Format a percentage change value with +/- sign."""
    if val is None:
        return "—"
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.1f}%"


def _build_btc_current(data: dict, now: datetime) -> str:
    """Render BTC current.md content from collected data."""
    btc = data.get("btc", {})
    price = btc.get("price")
    date  = btc.get("date", "—")

    price_str = f"${price:,.0f}" if price is not None else "—"

    lines = [
        f"# Bitcoin — 현재 시세 (자동 업데이트)",
        f"",
        f"> 마지막 업데이트: {now.strftime('%Y-%m-%d %H:%M')}",
        f"> 수집 출처: yfinance (BTC-USD)",
        f"> ⚠️ 이 파일은 자동 생성됩니다 — 직접 수정 금지",
        f"",
        f"---",
        f"",
        f"## 현재 가격",
        f"",
        f"| 항목 | 값 |",
        f"|------|-----|",
        f"| 현재가 | **{price_str}** |",
        f"| 기준일 | {date} |",
        f"",
        f"---",
        f"",
        f"## 가격 변화율",
        f"",
        f"| 기간 | 변화율 |",
        f"|------|--------|",
        f"| 1일 | {_fmt_pct(btc.get('pct_1d'))} |",
        f"| 1주 | {_fmt_pct(btc.get('pct_1w'))} |",
        f"| 1달 | {_fmt_pct(btc.get('pct_1m'))} |",
        f"| 3달 | {_fmt_pct(btc.get('pct_3m'))} |",
        f"| 1년 | {_fmt_pct(btc.get('pct_1y'))} |",
        f"",
    ]
    return "\n".join(lines)


def _build_eth_current(data: dict, now: datetime) -> str:
    """Render ETH current.md content from collected data."""
    eth           = data.get("eth", {})
    price         = eth.get("price")
    date          = eth.get("date", "—")
    eth_tvl_b     = data.get("eth_tvl_b")
    l2_tvl_b      = data.get("l2_tvl_b")
    total_tvl_b   = data.get("total_tvl_b")

    price_str     = f"${price:,.0f}" if price is not None else "—"
    eth_tvl_str   = f"${eth_tvl_b}B" if eth_tvl_b is not None else "—"
    l2_tvl_str    = f"${l2_tvl_b}B"  if l2_tvl_b  is not None else "—"
    total_tvl_str = f"${total_tvl_b:,.0f}B" if total_tvl_b is not None else "—"

    lines = [
        f"# Ethereum — 현재 시세 (자동 업데이트)",
        f"",
        f"> 마지막 업데이트: {now.strftime('%Y-%m-%d %H:%M')}",
        f"> 수집 출처: yfinance (ETH-USD), DeFiLlama API",
        f"> ⚠️ 이 파일은 자동 생성됩니다 — 직접 수정 금지",
        f"",
        f"---",
        f"",
        f"## 현재 가격",
        f"",
        f"| 항목 | 값 |",
        f"|------|-----|",
        f"| 현재가 | **{price_str}** |",
        f"| 기준일 | {date} |",
        f"",
        f"---",
        f"",
        f"## 가격 변화율",
        f"",
        f"| 기간 | 변화율 |",
        f"|------|--------|",
        f"| 1일 | {_fmt_pct(eth.get('pct_1d'))} |",
        f"| 1주 | {_fmt_pct(eth.get('pct_1w'))} |",
        f"| 1달 | {_fmt_pct(eth.get('pct_1m'))} |",
        f"| 3달 | {_fmt_pct(eth.get('pct_3m'))} |",
        f"| 1년 | {_fmt_pct(eth.get('pct_1y'))} |",
        f"",
        f"---",
        f"",
        f"## DeFi 생태계 TVL",
        f"",
        f"| 항목 | TVL |",
        f"|------|-----|",
        f"| ETH 체인 DeFi TVL | **{eth_tvl_str}** |",
        f"| L2 TVL 합계 (Base+Arb+OP+zkSync) | **{l2_tvl_str}** |",
        f"| 전체 DeFi TVL (전 체인) | {total_tvl_str} |",
        f"",
    ]
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="크립토 리서치 허브 현황 업데이트")
    parser.add_argument("--dry-run", action="store_true",
                        help="파일 저장 없이 출력만")
    args = parser.parse_args()

    print("=" * 56)
    print("  Crypto Hub Updater")
    print("=" * 56)

    print("\n크립토 데이터 수집 중...")
    collector = CryptoCollector()
    data = collector.collect()

    btc = data.get("btc", {})
    eth = data.get("eth", {})
    btc_ok = "error" not in btc
    eth_ok = "error" not in eth

    if btc_ok:
        print(f"  BTC: ${btc.get('price', '?'):,.0f}  "
              f"(1d {_fmt_pct(btc.get('pct_1d'))}, "
              f"1w {_fmt_pct(btc.get('pct_1w'))})")
    else:
        print(f"  BTC: 오류 — {btc.get('error')}")

    if eth_ok:
        print(f"  ETH: ${eth.get('price', '?'):,.0f}  "
              f"(1d {_fmt_pct(eth.get('pct_1d'))}, "
              f"1w {_fmt_pct(eth.get('pct_1w'))})")
    else:
        print(f"  ETH: 오류 — {eth.get('error')}")

    tvl = data.get("eth_tvl_b")
    if tvl is not None:
        print(f"  ETH TVL: ${tvl}B  |  L2: ${data.get('l2_tvl_b')}B  "
              f"|  Total: ${data.get('total_tvl_b', '?'):,.0f}B")
    else:
        print("  TVL: 수집 실패 (DeFiLlama API 오류)")

    now = datetime.now()
    btc_md = _build_btc_current(data, now)
    eth_md = _build_eth_current(data, now)

    if args.dry_run:
        print("\n[dry-run] BTC current.md 미리보기:")
        print(btc_md)
        print("\n[dry-run] ETH current.md 미리보기:")
        print(eth_md)
        return

    # Write files
    _BTC_DIR.mkdir(parents=True, exist_ok=True)
    _ETH_DIR.mkdir(parents=True, exist_ok=True)

    btc_path = _BTC_DIR / "current.md"
    eth_path = _ETH_DIR / "current.md"

    btc_path.write_text(btc_md, encoding="utf-8")
    eth_path.write_text(eth_md, encoding="utf-8")

    print(f"\n업데이트 완료:")
    print(f"  {btc_path}")
    print(f"  {eth_path}")


if __name__ == "__main__":
    main()
