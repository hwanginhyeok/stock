"""Generator test fixtures — mock ClaudeClient."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_claude_client():
    """Patch ClaudeClient so BaseGenerator.__init__ succeeds."""
    mock_client = MagicMock()
    mock_response = SimpleNamespace(content="Generated content here.")
    mock_client.generate.return_value = mock_response

    with patch("src.generators.base.ClaudeClient", return_value=mock_client):
        yield mock_client
