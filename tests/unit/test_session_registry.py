"""Tests for FileSessionRegistry."""

import pytest
from pathlib import Path
from src.utils.session_registry import FileSessionRegistry


def test_get_set_session_id(tmp_path):
    """Test basic get/set functionality."""
    registry_file = tmp_path / "test_sessions.json"
    registry = FileSessionRegistry(str(registry_file))

    # Initially empty
    assert registry.get_session_id("thread_123") is None

    # Set and retrieve
    registry.set_session_id("thread_123", "session_abc")
    assert registry.get_session_id("thread_123") == "session_abc"


def test_multiple_threads(tmp_path):
    """Test multiple thread sessions."""
    registry_file = tmp_path / "test_sessions.json"
    registry = FileSessionRegistry(str(registry_file))

    registry.set_session_id("thread_1", "session_1")
    registry.set_session_id("thread_2", "session_2")

    assert registry.get_session_id("thread_1") == "session_1"
    assert registry.get_session_id("thread_2") == "session_2"


def test_update_existing_session(tmp_path):
    """Test updating an existing session."""
    registry_file = tmp_path / "test_sessions.json"
    registry = FileSessionRegistry(str(registry_file))

    registry.set_session_id("thread_1", "session_old")
    assert registry.get_session_id("thread_1") == "session_old"

    # Update
    registry.set_session_id("thread_1", "session_new")
    assert registry.get_session_id("thread_1") == "session_new"


def test_file_creation(tmp_path):
    """Test that registry file is created if it doesn't exist."""
    registry_file = tmp_path / "new_sessions.json"
    assert not registry_file.exists()

    registry = FileSessionRegistry(str(registry_file))
    assert registry_file.exists()
