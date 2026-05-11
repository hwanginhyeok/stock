#!/usr/bin/env python3
"""테슬라 인도량 선행 지표 수집 wrapper.

cron: 0 10 * * * cd ~/stock && python3 scripts/collect_delivery_signals.py >> ~/.pm_logs/delivery_signals.log 2>&1
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _run(script: str) -> int:
    """스크립트 실행 후 종료 코드 반환."""
    result = subprocess.run(
        ["python3", script],
        capture_output=False,
        cwd=str(_PROJECT_ROOT),
        timeout=120,
    )
    return result.returncode


def main() -> None:
    print(f"\n[{_now()}] === 테슬라 인도량 선행 지표 수집 시작 ===")

    scripts = [
        ("CPCA (중국)", "src/collectors/delivery/cpca_collector.py"),
        ("EU 등록",    "src/collectors/delivery/eu_reg_collector.py"),
    ]

    for label, script in scripts:
        print(f"\n--- {label} ---")
        try:
            rc = _run(script)
            status = "완료" if rc == 0 else f"오류 (rc={rc})"
            print(f"  [{label}] {status}")
        except subprocess.TimeoutExpired:
            print(f"  [{label}] 타임아웃 (120초)")
        except Exception as e:
            print(f"  [{label}] 실패: {e}")

    print(f"\n[{_now()}] === 수집 완료 ===")


if __name__ == "__main__":
    main()
