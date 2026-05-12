#!/usr/bin/env python3
"""GeoInvest DB 마이그레이션 — 기존 테이블에 컬럼 추가 + 신규 테이블 생성.

Usage:
    python scripts/migrate_geoinvest.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = _PROJECT_ROOT / "data" / "db" / "stock_rich.db"


def run_migration() -> None:
    """GeoInvest 마이그레이션 실행."""
    if not DB_PATH.exists():
        print(f"ERROR: DB 파일 없음: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    migrations = [
        # 1. OntologyEntity에 aliases 컬럼 추가
        (
            "ontology_entities",
            "aliases",
            "ALTER TABLE ontology_entities ADD COLUMN aliases TEXT DEFAULT '[]'",
        ),
        # 2. OntologyLink에 source_urls 컬럼 추가
        (
            "ontology_links",
            "source_urls",
            "ALTER TABLE ontology_links ADD COLUMN source_urls TEXT DEFAULT '[]'",
        ),
    ]

    for table, column, sql in migrations:
        # 컬럼 존재 여부 확인
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if column in columns:
            print(f"  SKIP: {table}.{column} 이미 존재")
        else:
            cursor.execute(sql)
            print(f"  ADD:  {table}.{column}")

    # 3. geo_issues 테이블 생성
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='geo_issues'
    """)
    if cursor.fetchone():
        print("  SKIP: geo_issues 테이블 이미 존재")
    else:
        cursor.execute("""
            CREATE TABLE geo_issues (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                description TEXT DEFAULT '',
                severity VARCHAR(20) DEFAULT 'moderate',
                status VARCHAR(20) DEFAULT 'active',
                event_ids TEXT DEFAULT '[]',
                created_at DATETIME
            )
        """)
        cursor.execute("CREATE INDEX ix_geo_issue_status ON geo_issues(status)")
        cursor.execute("CREATE INDEX ix_geo_issue_severity ON geo_issues(severity)")
        print("  CREATE: geo_issues 테이블 + 인덱스")

    conn.commit()
    conn.close()
    print("\n마이그레이션 완료.")


if __name__ == "__main__":
    print("GeoInvest DB 마이그레이션 시작...")
    run_migration()
