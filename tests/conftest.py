"""Pytest configuration and common fixtures."""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-bot-token")
    monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-test-app-token")
    monkeypatch.setenv("GOOGLE_GENAI_API_KEY", "test-google-genai-api-key")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")  # Quiet logs during tests


@pytest.fixture
def mock_slack_event():
    """Mock Slack event data."""
    return {
        "type": "app_mention",
        "user": "U12345678",
        "text": "<@U87654321> Hello, bot!",
        "ts": "1234567890.123456",
        "channel": "C11111111",
        "event_ts": "1234567890.123456"
    }


@pytest.fixture
def mock_feedparser_entry():
    """Mock feedparser entry."""
    entry = Mock()
    entry.title = "Test News Title"
    entry.link = "https://example.com/news"
    entry.summary = "Test summary"
    entry.description = "Test description"
    entry.published = "2025-10-29T10:00:00"
    entry.updated = "2025-10-29T10:00:00"
    return entry


@pytest.fixture
def mock_feedparser_feed():
    """Mock feedparser feed."""
    feed = Mock()
    feed.bozo = False
    feed.feed = Mock()
    feed.feed.title = "Test Feed"
    return feed
