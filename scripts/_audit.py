#!/usr/bin/env python3
"""DB 빈 테이블 + FK 참조 감사"""
import sqlite3, sys

DB = "data/db/stock_rich.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

print("=== 빈 테이블 (0행) ===")
empty_tables = []
for (t,) in sorted(tables):
    cnt = cur.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
    if cnt == 0:
        empty_tables.append(t)
        print(f"  {t}")
print(f"\n총 {len(empty_tables)}개\n")

print("=== FK 참조 관계 ===")
for (t,) in sorted(tables):
    row = cur.execute(f"SELECT sql FROM sqlite_master WHERE name='{t}'").fetchone()
    if row and row[0] and 'REFERENCES' in row[0]:
        refs = [l.strip().rstrip(',') for l in row[0].split('\n') if 'REFERENCES' in l]
        if refs:
            print(f"  {t}:")
            for r in refs:
                print(f"    {r}")

conn.close()
