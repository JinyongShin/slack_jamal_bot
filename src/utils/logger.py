"""Logging configuration for AgentJamal bot."""

import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Set log level
        log_level = getattr(logging, (level or "INFO").upper())
        logger.setLevel(log_level)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger
