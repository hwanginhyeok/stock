"""Custom exception hierarchy for the Stock Rich Project."""

from typing import Any


class StockRichError(Exception):
    """Root exception for all project-specific errors.

    Args:
        message: Human-readable error description.
        details: Optional dict with structured error context.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | details={self.details}"
        return self.message


class ConfigError(StockRichError):
    """Configuration loading or validation error."""


class APIError(StockRichError):
    """Generic external API error."""


class ClaudeAPIError(APIError):
    """Claude API specific error."""


class RateLimitError(APIError):
    """API rate limit exceeded."""


class CollectionError(StockRichError):
    """Data collection error (news, market data)."""


class AnalysisError(StockRichError):
    """Data analysis error."""


class ContentError(StockRichError):
    """Content generation or validation error."""


class PublishError(StockRichError):
    """SNS publishing error."""


class DatabaseError(StockRichError):
    """Database operation error."""
