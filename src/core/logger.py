"""Structured logging setup using structlog."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import structlog


def setup_logging(
    level: str = "INFO",
    format: str = "json",
    log_file: str | None = None,
) -> None:
    """Initialize structlog with the given configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format: Output format - "json" for production, "console" for development.
        log_file: Optional file path for log output.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Suppress noisy third-party loggers
    for name in ("httpx", "httpcore", "sqlalchemy.engine", "urllib3", "anthropic"):
        logging.getLogger(name).setLevel(logging.WARNING)

    # Shared structlog processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Renderer based on format
    if format == "json":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer(
            ensure_ascii=False,
        )
    else:
        renderer = structlog.dev.ConsoleRenderer()

    # Setup stdlib handlers
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
        file_handler.setLevel(log_level)
        handlers.append(file_handler)

    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=handlers,
        force=True,
    )

    # Configure structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Apply formatter to all root handlers
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)


def get_logger(name: str, **bindings: str) -> structlog.stdlib.BoundLogger:
    """Get a module-specific logger with optional bound context.

    Args:
        name: Logger name (typically __name__).
        **bindings: Additional key-value pairs to bind to the logger.

    Returns:
        A structlog BoundLogger instance.
    """
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    if bindings:
        logger = logger.bind(**bindings)
    return logger
