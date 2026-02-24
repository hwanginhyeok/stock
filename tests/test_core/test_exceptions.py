"""Tests for the custom exception hierarchy."""

from __future__ import annotations

import pytest

from src.core.exceptions import (
    AnalysisError,
    APIError,
    ClaudeAPIError,
    CollectionError,
    ConfigError,
    ContentError,
    DatabaseError,
    PublishError,
    RateLimitError,
    StockRichError,
    WorkflowError,
)


class TestStockRichError:
    """Test root exception class."""

    def test_message_only(self):
        err = StockRichError("something broke")
        assert err.message == "something broke"
        assert err.details == {}
        assert str(err) == "something broke"

    def test_message_with_details(self):
        err = StockRichError("bad thing", {"key": "val"})
        assert err.details == {"key": "val"}
        assert "details=" in str(err)

    def test_is_exception(self):
        with pytest.raises(StockRichError):
            raise StockRichError("test")


class TestExceptionHierarchy:
    """Test that all exceptions inherit correctly."""

    def test_config_error_is_stock_rich(self):
        assert issubclass(ConfigError, StockRichError)

    def test_api_error_is_stock_rich(self):
        assert issubclass(APIError, StockRichError)

    def test_claude_api_error_is_api_error(self):
        assert issubclass(ClaudeAPIError, APIError)
        assert issubclass(ClaudeAPIError, StockRichError)

    def test_rate_limit_is_api_error(self):
        assert issubclass(RateLimitError, APIError)

    def test_collection_error(self):
        assert issubclass(CollectionError, StockRichError)

    def test_analysis_error(self):
        assert issubclass(AnalysisError, StockRichError)

    def test_content_error(self):
        assert issubclass(ContentError, StockRichError)

    def test_publish_error(self):
        assert issubclass(PublishError, StockRichError)

    def test_database_error(self):
        assert issubclass(DatabaseError, StockRichError)

    def test_workflow_error(self):
        assert issubclass(WorkflowError, StockRichError)


class TestExceptionDetails:
    """Test detail propagation in sub-exceptions."""

    def test_config_error_details(self):
        err = ConfigError("missing file", {"file": "settings.yaml"})
        assert err.details["file"] == "settings.yaml"

    def test_analysis_error_details(self):
        err = AnalysisError("no data", {"ticker": "AAPL"})
        assert err.details["ticker"] == "AAPL"

    def test_catch_base_catches_child(self):
        with pytest.raises(StockRichError):
            raise ClaudeAPIError("api failed")

    def test_catch_api_catches_claude(self):
        with pytest.raises(APIError):
            raise ClaudeAPIError("timeout")
