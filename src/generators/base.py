"""Abstract base class for all content generators."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from src.core.claude_client import ClaudeClient
from src.core.config import PROJECT_ROOT, ArticleTypeConfig, ContentConfig, get_config
from src.core.exceptions import ClaudeAPIError, ContentError
from src.core.logger import get_logger
from src.core.models import ClaudeTask


class BaseGenerator(ABC):
    """Base class for content generators.

    Provides shared initialization for config, logging, Claude client,
    and Jinja2 template rendering. Also includes content validation
    utilities (prohibited expression check, disclaimer, quality scoring).
    """

    def __init__(self) -> None:
        self._config = get_config()
        self._content_config: ContentConfig = self._config.content
        self._logger = get_logger(type(self).__name__)
        self._client = ClaudeClient()
        self._jinja_env = self._init_jinja_env()
        self._logger.info("generator_initialized", generator=type(self).__name__)

    def _init_jinja_env(self) -> Environment:
        """Initialize Jinja2 environment with FileSystemLoader.

        Returns:
            Configured Jinja2 Environment.
        """
        env = Environment(
            loader=FileSystemLoader(str(PROJECT_ROOT / "templates")),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=False,
        )
        # Custom filters
        env.filters["format_number"] = self._filter_format_number
        env.filters["truncate_text"] = self._filter_truncate_text
        env.filters["sign"] = self._filter_sign
        return env

    @staticmethod
    def _filter_format_number(value: float | int, decimals: int = 2) -> str:
        """Format a number with comma separators."""
        if isinstance(value, int):
            return f"{value:,}"
        return f"{value:,.{decimals}f}"

    @staticmethod
    def _filter_truncate_text(text: str, length: int = 100) -> str:
        """Truncate text to a given length with ellipsis."""
        if len(text) <= length:
            return text
        return text[: length - 3] + "..."

    @staticmethod
    def _filter_sign(value: float) -> str:
        """Format a number with explicit sign."""
        if value > 0:
            return f"+{value}"
        return str(value)

    def _render_prompt(self, template_path: str, **context: Any) -> str:
        """Render a Jinja2 prompt template.

        Args:
            template_path: Path relative to templates/ or full path starting
                with ``templates/``. The ``templates/`` prefix is stripped
                automatically.
            **context: Template variables.

        Returns:
            Rendered template string.

        Raises:
            ContentError: If the template cannot be loaded.
        """
        # Strip "templates/" prefix if present
        rel_path = template_path
        if rel_path.startswith("templates/"):
            rel_path = rel_path[len("templates/"):]

        try:
            template = self._jinja_env.get_template(rel_path)
            return template.render(**context)
        except TemplateNotFound as e:
            raise ContentError(
                f"Prompt template not found: {rel_path}",
                {"template": rel_path, "error": str(e)},
            ) from e

    def _generate_content(
        self,
        task: ClaudeTask,
        user_message: str,
        system_prompt: str = "",
    ) -> str:
        """Call Claude API and return generated text.

        Wraps ClaudeAPIError into ContentError for consistent
        error handling in the generator layer.

        Args:
            task: Claude task type for model selection.
            user_message: The user message to send.
            system_prompt: Optional system prompt.

        Returns:
            Generated text content.

        Raises:
            ContentError: On API failure.
        """
        try:
            response = self._client.generate(
                task=task,
                user_message=user_message,
                system_prompt=system_prompt,
            )
            return response.content
        except ClaudeAPIError as e:
            raise ContentError(
                f"Content generation failed: {e.message}",
                {"task": task.value, "original_error": str(e)},
            ) from e

    def _check_prohibited(self, content: str) -> list[str]:
        """Check content for prohibited expressions.

        Args:
            content: Text to check.

        Returns:
            List of found prohibited expressions (empty if clean).
        """
        prohibited = self._content_config.prohibited_expressions
        found: list[str] = []
        for expr in prohibited:
            if expr in content:
                found.append(expr)
        return found

    def _append_disclaimer(self, content: str, lang: str = "ko") -> str:
        """Append disclaimer if not already present.

        Args:
            content: Article content.
            lang: Language code ("ko" or "en").

        Returns:
            Content with disclaimer appended (if missing).
        """
        disclaimer = (
            self._content_config.disclaimer.ko
            if lang == "ko"
            else self._content_config.disclaimer.en
        )
        if not disclaimer:
            return content

        # Check if disclaimer is already included (first line match)
        disclaimer_first_line = disclaimer.strip().split("\n")[0].strip()
        if disclaimer_first_line and disclaimer_first_line in content:
            return content

        return f"{content.rstrip()}\n\n---\n{disclaimer.strip()}\n"

    def _compute_quality_score(
        self,
        content: str,
        config: ArticleTypeConfig,
    ) -> float:
        """Compute a 0-100 quality score for generated content.

        Scoring breakdown:
        - Length compliance (25%): How well content length matches config range.
        - Prohibited expressions (30%): Penalty per found expression.
        - Disclaimer inclusion (20%): Whether disclaimer is present.
        - Structure (25%): Headings, paragraphs, formatting quality.

        Args:
            content: Generated text content.
            config: Article type configuration for length bounds.

        Returns:
            Quality score between 0.0 and 100.0.
        """
        char_count = len(content)

        # 1. Length score (25%)
        if config.min_length <= char_count <= config.max_length:
            length_score = 25.0
        elif char_count < config.min_length:
            ratio = char_count / config.min_length if config.min_length > 0 else 0
            length_score = 25.0 * ratio
        else:
            # Over max — gentle penalty
            over_ratio = config.max_length / char_count if char_count > 0 else 0
            length_score = 25.0 * max(over_ratio, 0.5)

        # 2. Prohibited expressions (30%)
        found = self._check_prohibited(content)
        prohibited_score = max(0.0, 30.0 - len(found) * 10.0)

        # 3. Disclaimer (20%)
        disclaimer_ko = self._content_config.disclaimer.ko.strip()
        disclaimer_first_line = disclaimer_ko.split("\n")[0].strip() if disclaimer_ko else ""
        has_disclaimer = disclaimer_first_line in content if disclaimer_first_line else True
        disclaimer_score = 20.0 if has_disclaimer else 0.0

        # 4. Structure (25%)
        structure_score = 0.0
        # Has headings
        if re.search(r"^#{1,3}\s+.+", content, re.MULTILINE):
            structure_score += 8.0
        # Has multiple paragraphs
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if len(paragraphs) >= 3:
            structure_score += 8.0
        elif len(paragraphs) >= 2:
            structure_score += 4.0
        # Has bullet points or numbered lists
        if re.search(r"^[\-\*]\s+.+|^\d+\.\s+.+", content, re.MULTILINE):
            structure_score += 5.0
        # Not a single giant block
        lines = content.strip().split("\n")
        if len(lines) >= 5:
            structure_score += 4.0

        total = length_score + prohibited_score + disclaimer_score + structure_score
        return round(min(100.0, max(0.0, total)), 1)

    @abstractmethod
    def generate(self, **kwargs: Any) -> Any:
        """Generate content. Subclasses must implement this.

        Args:
            **kwargs: Generator-specific arguments.

        Returns:
            Generated content (type varies by generator).
        """
