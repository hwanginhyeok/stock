"""Collector test fixtures — mock RSS entries."""

from __future__ import annotations

from types import SimpleNamespace

import pytest


@pytest.fixture
def mock_rss_entry() -> SimpleNamespace:
    """A mock feedparser entry with typical attributes."""
    return SimpleNamespace(
        title="  Fed Holds Rates Steady Amid Inflation Concerns  ",
        link="https://example.com/news/fed-rates",
        summary="<p>The Federal Reserve held rates <b>steady</b> today.</p>",
        content=[{"value": "<p>Full article content about the Fed decision.</p>"}],
        published_parsed=(2026, 2, 22, 10, 30, 0, 0, 0, 0),
    )


@pytest.fixture
def mock_rss_entry_minimal() -> SimpleNamespace:
    """Minimal RSS entry with only title."""
    return SimpleNamespace(
        title="Breaking: Market Crash",
        link="",
    )


@pytest.fixture
def mock_rss_entry_no_title() -> SimpleNamespace:
    """RSS entry with empty title."""
    return SimpleNamespace(
        title="",
        link="https://example.com/empty",
        summary="Some content",
    )
