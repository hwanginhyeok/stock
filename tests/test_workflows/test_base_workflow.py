"""Tests for BaseWorkflow step execution logic."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core.exceptions import WorkflowError
from src.workflows.base import BaseWorkflow, WorkflowResult


class ConcreteWorkflow(BaseWorkflow):
    """Concrete workflow for testing."""

    name = "test_workflow"

    def __init__(self):
        super().__init__()
        self.step_results = {}

    def execute(self) -> WorkflowResult:
        result = WorkflowResult(workflow_name=self.name)
        return result


class TestRunStep:
    """Test _run_step for critical and non-critical steps."""

    def test_successful_step(self):
        wf = ConcreteWorkflow()
        value = wf._run_step("my_step", lambda: 42)
        assert value == 42

    def test_successful_step_returns_list(self):
        wf = ConcreteWorkflow()
        value = wf._run_step("list_step", lambda: [1, 2, 3])
        assert value == [1, 2, 3]

    def test_non_critical_failure_returns_none(self):
        wf = ConcreteWorkflow()

        def failing():
            raise ValueError("oops")

        value = wf._run_step("bad_step", failing, critical=False)
        assert value is None

    def test_non_critical_failure_records_error(self):
        wf = ConcreteWorkflow()

        def failing():
            raise RuntimeError("boom")

        wf._run_step("bad_step", failing, critical=False)
        assert len(wf._errors) == 1
        assert wf._errors[0]["step"] == "bad_step"
        assert "boom" in wf._errors[0]["error"]

    def test_critical_failure_raises_workflow_error(self):
        wf = ConcreteWorkflow()

        def failing():
            raise ValueError("critical fail")

        with pytest.raises(WorkflowError) as exc_info:
            wf._run_step("critical_step", failing, critical=True)
        assert "critical_step" in str(exc_info.value)

    def test_critical_failure_records_error(self):
        wf = ConcreteWorkflow()

        def failing():
            raise ValueError("fail")

        try:
            wf._run_step("step", failing, critical=True)
        except WorkflowError:
            pass
        assert len(wf._errors) == 1

    def test_step_timing_recorded(self):
        wf = ConcreteWorkflow()
        wf._run_step("timed_step", lambda: "ok")
        assert len(wf._step_timings) == 1
        assert wf._step_timings[0]["step"] == "timed_step"
        assert wf._step_timings[0]["success"] is True

    def test_failed_step_timing_recorded(self):
        wf = ConcreteWorkflow()
        wf._run_step("fail_step", lambda: 1 / 0, critical=False)
        assert len(wf._step_timings) == 1
        assert wf._step_timings[0]["success"] is False


class TestWorkflowRun:
    """Test the run() wrapper method."""

    def test_successful_run(self):
        wf = ConcreteWorkflow()
        result = wf.run()
        assert result.success is True
        assert result.workflow_name == "test_workflow"
        assert result.elapsed_sec >= 0

    def test_run_with_workflow_error(self):
        class FailingWorkflow(BaseWorkflow):
            name = "failing"

            def execute(self) -> WorkflowResult:
                raise WorkflowError("abort!")

        wf = FailingWorkflow()
        result = wf.run()
        assert result.success is False
        assert result.workflow_name == "failing"

    def test_run_with_unexpected_error(self):
        class CrashWorkflow(BaseWorkflow):
            name = "crash"

            def execute(self) -> WorkflowResult:
                raise RuntimeError("unexpected!")

        wf = CrashWorkflow()
        result = wf.run()
        assert result.success is False
        assert len(result.errors) >= 1

    def test_run_records_elapsed(self):
        wf = ConcreteWorkflow()
        result = wf.run()
        assert isinstance(result.elapsed_sec, float)
