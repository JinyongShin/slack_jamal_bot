"""Tests for ADKAgent class."""

import pytest


def test_adk_agent_initializes_with_api_key():
    """Test that ADKAgent can be initialized with an API key."""
    from src.llm.adk_agent import ADKAgent

    agent = ADKAgent(api_key="test-key", model="gemini-2.0-flash")

    assert agent is not None
    assert agent.agent is not None
