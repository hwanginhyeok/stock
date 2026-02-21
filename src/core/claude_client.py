"""Claude API client with task-based model selection and retry logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import anthropic
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.core.config import get_config
from src.core.exceptions import ClaudeAPIError, RateLimitError
from src.core.logger import get_logger
from src.core.models import ClaudeTask

logger = get_logger(__name__)


@dataclass(slots=True)
class ClaudeResponse:
    """Response wrapper for Claude API calls."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str


@dataclass
class _TokenUsage:
    """Cumulative token usage tracker."""

    total_input: int = 0
    total_output: int = 0
    call_count: int = 0


class ClaudeClient:
    """Claude API client with task-based model/parameter auto-selection.

    Uses the task type to automatically select the appropriate model,
    max_tokens, and temperature from configuration.

    Example::

        client = ClaudeClient()
        response = client.generate(
            ClaudeTask.GENERAL,
            "오늘의 한국 주식 시장 요약을 작성해 주세요.",
            system_prompt="당신은 주식 시장 전문 분석가입니다.",
        )
        print(response.content)
    """

    def __init__(self) -> None:
        config = get_config()
        if not config.anthropic_api_key:
            raise ClaudeAPIError(
                "ANTHROPIC_API_KEY is not set",
                {"hint": "Set ANTHROPIC_API_KEY in your .env file"},
            )
        self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self._config = config.claude
        self._retry_config = config.retry
        self._usage = _TokenUsage()
        logger.info(
            "claude_client_initialized",
            default_model=self._config.default_model,
        )

    def _resolve_params(self, task: ClaudeTask) -> tuple[str, int, float]:
        """Resolve model, max_tokens, and temperature for a task.

        Args:
            task: The Claude task type.

        Returns:
            Tuple of (model_id, max_tokens, temperature).
        """
        task_key = task.value
        model = self._config.models.get(task_key, self._config.default_model)
        max_tokens = self._config.max_tokens.get(task_key, 4096)
        temperature = self._config.temperature.get(task_key, 0.7)
        return model, max_tokens, temperature

    def generate(
        self,
        task: ClaudeTask,
        user_message: str,
        system_prompt: str = "",
    ) -> ClaudeResponse:
        """Generate a single-turn response.

        Args:
            task: Task type for model/parameter selection.
            user_message: The user message to send.
            system_prompt: Optional system prompt.

        Returns:
            ClaudeResponse with the generated content.

        Raises:
            ClaudeAPIError: On non-retryable API errors.
            RateLimitError: If rate limited after all retries.
        """
        messages = [{"role": "user", "content": user_message}]
        return self.generate_with_messages(task, messages, system_prompt)

    def generate_with_messages(
        self,
        task: ClaudeTask,
        messages: list[dict[str, str]],
        system_prompt: str = "",
    ) -> ClaudeResponse:
        """Generate a response from a multi-turn conversation.

        Args:
            task: Task type for model/parameter selection.
            messages: List of message dicts with 'role' and 'content'.
            system_prompt: Optional system prompt.

        Returns:
            ClaudeResponse with the generated content.

        Raises:
            ClaudeAPIError: On non-retryable API errors.
            RateLimitError: If rate limited after all retries.
        """
        model, max_tokens, temperature = self._resolve_params(task)

        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        logger.debug(
            "claude_api_call",
            task=task.value,
            model=model,
            message_count=len(messages),
        )

        response = self._call_api(**kwargs)

        content = response.content[0].text if response.content else ""
        result = ClaudeResponse(
            content=content,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason or "",
        )

        # Track cumulative token usage
        self._usage.total_input += result.input_tokens
        self._usage.total_output += result.output_tokens
        self._usage.call_count += 1

        logger.info(
            "claude_api_response",
            task=task.value,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            stop_reason=result.stop_reason,
        )

        return result

    @retry(
        retry=retry_if_exception_type((
            anthropic.RateLimitError,
            anthropic.APIConnectionError,
            anthropic.InternalServerError,
        )),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        reraise=True,
    )
    def _call_api(self, **kwargs: Any) -> anthropic.types.Message:
        """Call the Claude API with retry logic.

        Retries on RateLimitError, APIConnectionError, and
        InternalServerError with exponential backoff.

        Args:
            **kwargs: Arguments to pass to messages.create().

        Returns:
            The API Message response.

        Raises:
            RateLimitError: If rate limited after all retries.
            ClaudeAPIError: For other API errors.
        """
        try:
            return self._client.messages.create(**kwargs)
        except anthropic.RateLimitError as e:
            logger.warning("claude_rate_limited", error=str(e))
            raise
        except anthropic.APIConnectionError as e:
            logger.warning("claude_connection_error", error=str(e))
            raise
        except anthropic.InternalServerError as e:
            logger.warning("claude_internal_error", error=str(e))
            raise
        except anthropic.APIStatusError as e:
            raise ClaudeAPIError(
                f"Claude API error: {e.status_code}",
                {"status_code": e.status_code, "message": str(e)},
            ) from e

    @property
    def token_usage(self) -> dict[str, int]:
        """Get cumulative token usage statistics.

        Returns:
            Dict with total_input_tokens, total_output_tokens, and call_count.
        """
        return {
            "total_input_tokens": self._usage.total_input,
            "total_output_tokens": self._usage.total_output,
            "call_count": self._usage.call_count,
        }
