"""Abstract base class for all data collectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.core.config import RetryConfig, get_config
from src.core.logger import get_logger


class BaseCollector(ABC):
    """Base class for data collectors.

    Provides shared initialization for config, retry settings, and logging.
    Subclasses must implement ``collect`` and ``collect_and_store``.
    """

    def __init__(self) -> None:
        self._config = get_config()
        self._retry_config: RetryConfig = self._config.retry
        self._logger = get_logger(type(self).__name__)
        self._logger.info("collector_initialized", collector=type(self).__name__)

    @abstractmethod
    def collect(self) -> list[Any]:
        """Collect data from external sources.

        Returns:
            List of collected domain models.
        """

    @abstractmethod
    def collect_and_store(self) -> list[Any]:
        """Collect data and persist to the database.

        Returns:
            List of persisted domain models.
        """
