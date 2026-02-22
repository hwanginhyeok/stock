"""Abstract base class for all workflow orchestrators."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from src.core.config import get_config
from src.core.exceptions import WorkflowError
from src.core.logger import get_logger

T = TypeVar("T")


@dataclass
class WorkflowResult:
    """Result of a workflow execution.

    Attributes:
        workflow_name: Identifier for the workflow.
        success: Whether the workflow completed without critical errors.
        elapsed_sec: Total execution time in seconds.
        articles_generated: Number of articles generated.
        images_generated: Number of images generated.
        news_collected: Number of news items collected.
        snapshots_collected: Number of market snapshots collected.
        analyses_produced: Number of stock analyses produced.
        errors: List of error dicts with step name and message.
        data: Arbitrary result data from the workflow.
    """

    workflow_name: str
    success: bool = True
    elapsed_sec: float = 0.0
    articles_generated: int = 0
    images_generated: int = 0
    news_collected: int = 0
    snapshots_collected: int = 0
    analyses_produced: int = 0
    errors: list[dict[str, Any]] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


class BaseWorkflow(ABC):
    """Base class for workflow orchestrators.

    Provides shared infrastructure for step execution with timing,
    logging, and error handling. Critical steps abort the workflow;
    non-critical steps log errors and continue.
    """

    name: str = "base_workflow"

    def __init__(self) -> None:
        self._config = get_config()
        self._logger = get_logger(type(self).__name__)
        self._errors: list[dict[str, Any]] = []
        self._step_timings: list[dict[str, Any]] = []

    @abstractmethod
    def execute(self) -> WorkflowResult:
        """Execute the workflow steps.

        Subclasses implement this to define their step sequence
        using ``_run_step()`` calls.

        Returns:
            WorkflowResult with collected metrics.
        """

    def run(self) -> WorkflowResult:
        """Run the workflow with timing and top-level error handling.

        Returns:
            WorkflowResult with success flag, elapsed time, and errors.
        """
        self._errors = []
        self._step_timings = []
        self._logger.info("workflow_started", workflow=self.name)
        start = time.monotonic()

        try:
            result = self.execute()
        except WorkflowError as e:
            elapsed = round(time.monotonic() - start, 2)
            self._logger.error(
                "workflow_aborted",
                workflow=self.name,
                error=str(e),
                elapsed_sec=elapsed,
            )
            return WorkflowResult(
                workflow_name=self.name,
                success=False,
                elapsed_sec=elapsed,
                errors=self._errors,
            )
        except Exception as e:
            elapsed = round(time.monotonic() - start, 2)
            self._logger.error(
                "workflow_unexpected_error",
                workflow=self.name,
                error=str(e),
                error_type=type(e).__name__,
                elapsed_sec=elapsed,
            )
            self._errors.append({
                "step": "workflow",
                "error": str(e),
                "type": type(e).__name__,
            })
            return WorkflowResult(
                workflow_name=self.name,
                success=False,
                elapsed_sec=elapsed,
                errors=self._errors,
            )

        result.elapsed_sec = round(time.monotonic() - start, 2)
        result.errors = self._errors

        self._logger.info(
            "workflow_completed",
            workflow=self.name,
            success=result.success,
            elapsed_sec=result.elapsed_sec,
            articles=result.articles_generated,
            images=result.images_generated,
            news=result.news_collected,
            snapshots=result.snapshots_collected,
            analyses=result.analyses_produced,
            error_count=len(result.errors),
        )
        return result

    def _run_step(
        self,
        step_name: str,
        step_fn: Callable[[], T],
        critical: bool = False,
    ) -> T | None:
        """Execute a single workflow step with logging and error handling.

        Args:
            step_name: Human-readable name for the step.
            step_fn: Callable that performs the step work.
            critical: If True, raise WorkflowError on failure to abort
                the workflow. If False, log the error and return None.

        Returns:
            The step function's return value, or None on non-critical failure.

        Raises:
            WorkflowError: If the step fails and ``critical`` is True.
        """
        self._logger.info("step_started", workflow=self.name, step=step_name)
        start = time.monotonic()

        try:
            result = step_fn()
            elapsed = round(time.monotonic() - start, 2)
            self._step_timings.append({
                "step": step_name,
                "elapsed_sec": elapsed,
                "success": True,
            })
            self._logger.info(
                "step_completed",
                workflow=self.name,
                step=step_name,
                elapsed_sec=elapsed,
            )
            return result
        except Exception as e:
            elapsed = round(time.monotonic() - start, 2)
            error_info = {
                "step": step_name,
                "error": str(e),
                "type": type(e).__name__,
                "elapsed_sec": elapsed,
            }
            self._errors.append(error_info)
            self._step_timings.append({
                "step": step_name,
                "elapsed_sec": elapsed,
                "success": False,
            })

            if critical:
                self._logger.error(
                    "critical_step_failed",
                    workflow=self.name,
                    step=step_name,
                    error=str(e),
                    elapsed_sec=elapsed,
                )
                raise WorkflowError(
                    f"Critical step '{step_name}' failed: {e}",
                    {"step": step_name, "original_error": str(e)},
                ) from e

            self._logger.warning(
                "step_failed",
                workflow=self.name,
                step=step_name,
                error=str(e),
                elapsed_sec=elapsed,
            )
            return None
