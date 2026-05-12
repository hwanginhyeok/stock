#!/usr/bin/env python3
"""기존 GeoIssue에 entity_ids를 채워넣는다."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.database import init_db
from src.storage import GeoIssueRepository, OntologyEntityRepository, OntologyLinkRepository


def fix() -> None:
    init_db()
    i_repo = GeoIssueRepository()
    e_repo = OntologyEntityRepository()
    l_repo = OntologyLinkRepository()

    # 이슈별 엔티티 매핑 (시딩 시 사용한 엔티티 이름들)
    issue_entities = {
        "이란 전쟁": [
            "United States", "Israel", "Iran", "Hezbollah", "Houthis",
            "Iraqi Shia Militias", "Hamas", "Syria", "Qatar", "Bahrain",
            "UAE", "Saudi Arabia", "Jordan", "South Korea", "China",
            "Japan", "Russia", "EU", "Strait of Hormuz", "IRGC Quds Force",
            "Crude Oil", "Gold",
        ],
        "비트코인 지정학": [
            "Bitcoin", "Ethereum", "United States", "US SEC", "US Treasury",
            "China", "El Salvador", "MicroStrategy", "Coinbase", "Tether",
            "Circle", "Russia", "EU", "South Korea", "Japan", "Digital Yuan",
        ],
        "IMEC 회랑": [
            "India", "Saudi Arabia", "UAE", "Israel", "Greece", "Italy",
            "EU", "United States", "China", "Iran", "Strait of Hormuz",
            "IMEC Corridor", "Belt and Road Initiative", "Haifa Port",
            "Piraeus Port", "Suez Canal",
        ],
    }

    for title, entity_names in issue_entities.items():
        issues = i_repo.get_many(filters={"title": title}, limit=1)
        if not issues:
            print(f"  SKIP: '{title}' 이슈 없음")
            continue

        issue = issues[0]
        entity_ids = []
        for name in entity_names:
            e = e_repo.find_by_name(name)
            if e:
                entity_ids.append(e.id)

        issue.entity_ids = entity_ids
        i_repo.update(issue.id, entity_ids=entity_ids)
        print(f"  UPDATE: '{title}' → {len(entity_ids)}개 엔티티 연결")


if __name__ == "__main__":
    print("GeoIssue entity_ids 보정 시작...\n")
    fix()
    print("\n완료!")
