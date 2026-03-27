#!/bin/bash
# 시황 브리핑 파이프라인 — cron에서 호출
# Usage: ./scripts/run_briefing.sh morning|evening
#
# 오전 6시 KST: 뉴스 수집 → enrich → 팩트 추출 → 모닝 브리핑
# 오후 6시 KST: 뉴스 수집 → enrich → 팩트 추출 → 이브닝 브리핑

set -euo pipefail

SCHEDULE="${1:-morning}"
PROJECT_DIR="/home/gint_pcd/projects/주식부자프로젝트"
VENV_DIR="$PROJECT_DIR/.venv-wsl"
LOG_DIR="$PROJECT_DIR/logs"
PYTHON="$VENV_DIR/bin/python"

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/briefing_$(date +%Y%m%d)_${SCHEDULE}.log"

cd "$PROJECT_DIR"

{
    echo "=== Briefing Pipeline: $SCHEDULE ($(date)) ==="

    # 뉴스 수집은 별도 cron(매시 13분/43분)으로 이미 돌고 있음 — 여기서는 스킵

    echo "[1/3] Enriching articles (본문 보강)..."
    $PYTHON scripts/extract_facts.py enrich --market all --limit 30 --delay 2.0 2>&1 | tail -3

    echo "[2/3] Extracting facts..."
    $PYTHON scripts/extract_facts.py auto --market all --min-confidence 0.5 2>&1 | tail -1

    echo "[3/4] Generating briefing..."
    $PYTHON scripts/generate_briefing.py --schedule "$SCHEDULE" --hours 12 --save 2>&1

    echo "[4/4] Generating Naver HTML..."
    $PYTHON scripts/generate_briefing.py --schedule "$SCHEDULE" --hours 12 --naver 2>&1

    echo "=== Done ($(date)) ==="
} >> "$LOG_FILE" 2>&1
