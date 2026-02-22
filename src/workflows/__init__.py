"""Workflow orchestration layer for the Stock Rich Project.

Provides workflow classes that chain collectors, analyzers, and generators
into end-to-end pipelines for scheduled and on-demand content production.

Usage::

    from src.workflows import MorningBriefingWorkflow, ClosingReviewWorkflow
    result = MorningBriefingWorkflow().run()
"""

from src.workflows.base import BaseWorkflow, WorkflowResult
from src.workflows.breaking import BreakingNewsWorkflow, BreakingNewsTrigger
from src.workflows.closing import ClosingReviewWorkflow
from src.workflows.morning import MorningBriefingWorkflow
from src.workflows.research import ResearchRequest, ResearchWorkflow
from src.workflows.weekly import WeeklyReviewWorkflow

__all__ = [
    "BaseWorkflow",
    "WorkflowResult",
    "MorningBriefingWorkflow",
    "ClosingReviewWorkflow",
    "WeeklyReviewWorkflow",
    "BreakingNewsWorkflow",
    "BreakingNewsTrigger",
    "ResearchWorkflow",
    "ResearchRequest",
]
