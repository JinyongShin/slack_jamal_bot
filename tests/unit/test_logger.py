"""Unit tests for logger utility."""

import logging
from src.utils.logger import setup_logger


def test_setup_logger_default_level():
    """Test logger setup with default level."""
    logger = setup_logger("test_logger", "INFO")

    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0


def test_setup_logger_debug_level():
    """Test logger setup with DEBUG level."""
    logger = setup_logger("test_debug", "DEBUG")

    assert logger.level == logging.DEBUG


def test_setup_logger_warning_level():
    """Test logger setup with WARNING level."""
    logger = setup_logger("test_warning", "WARNING")

    assert logger.level == logging.WARNING


def test_setup_logger_error_level():
    """Test logger setup with ERROR level."""
    logger = setup_logger("test_error", "ERROR")

    assert logger.level == logging.ERROR


def test_setup_logger_no_duplicate_handlers():
    """Test that calling setup_logger twice doesn't add duplicate handlers."""
    logger1 = setup_logger("test_no_dup", "INFO")
    handler_count1 = len(logger1.handlers)

    logger2 = setup_logger("test_no_dup", "INFO")
    handler_count2 = len(logger2.handlers)

    # Should be the same logger instance with same number of handlers
    assert logger1 is logger2
    assert handler_count1 == handler_count2


def test_logger_message_format():
    """Test logger message format includes all required fields."""
    logger = setup_logger("test_format", "INFO")

    # Check that handler has a formatter
    assert logger.handlers[0].formatter is not None

    # Check format string includes expected fields
    format_str = logger.handlers[0].formatter._fmt
    assert "%(asctime)s" in format_str
    assert "%(name)s" in format_str
    assert "%(levelname)s" in format_str
    assert "%(message)s" in format_str
