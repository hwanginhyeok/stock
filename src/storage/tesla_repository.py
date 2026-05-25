"""Tesla 도메인 Repository — issues / milestones / tagged_issues."""

from __future__ import annotations

from src.core.models import TeslaIssue, TeslaMilestone, TeslaTaggedIssue
from src.storage.base import BaseRepository


class TeslaIssueRepository(BaseRepository[TeslaIssue]):
    """Tesla 본질론 이슈 CRUD Repository.

    향후 find_by_category / find_by_thesis_side 등 도메인 전용 쿼리 추가 가능.
    현재 Phase 2 범위: 마이그레이션용 기본 CRUD (upsert 포함).
    """

    pass


class TeslaMilestoneRepository(BaseRepository[TeslaMilestone]):
    """Tesla 이슈 하위 마일스톤 CRUD Repository.

    향후 find_by_issue_id 등 추가 가능.
    """

    pass


class TeslaTaggedIssueRepository(BaseRepository[TeslaTaggedIssue]):
    """Tesla tagged issue CRUD Repository.

    향후 find_by_sentiment / get_latest 등 추가 가능.
    """

    pass
