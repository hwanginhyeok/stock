"""Abstract base class for all analyzers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.core.config import get_config
from src.core.logger import get_logger


class BaseAnalyzer(ABC):
    """Base class for stock and market analyzers.

    Provides shared initialization for config and logging.
    """

    def __init__(self) -> None:
        self._config = get_config()
        self._logger = get_logger(type(self).__name__)
        self._logger.info("analyzer_initialized", analyzer=type(self).__name__)

    @abstractmethod
    def analyze(self, ticker: str, **kwargs: Any) -> dict[str, Any]:
        """Run analysis for a single ticker.

        Args:
            ticker: Stock ticker symbol.
            **kwargs: Additional parameters (e.g., OHLCV DataFrame).

        Returns:
            Dict with analysis results including at least a 'score' key.
        """
