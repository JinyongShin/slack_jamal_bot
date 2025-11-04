"""Tests for ADKAgent class."""

import pytest


def test_adk_agent_initializes_with_api_key():
    """Test that ADKAgent can be initialized with an API key."""
    from src.llm.adk_agent import ADKAgent

    agent = ADKAgent(api_key="test-key", model="gemini-2.0-flash")

    assert agent is not None
    assert agent.agent is not None


def test_generate_response_returns_text():
    """Test that generate_response returns a text response."""
    from src.llm.adk_agent import ADKAgent

    agent = ADKAgent(api_key="test-key")
    response = agent.generate_response("안녕")

    assert isinstance(response, str)
    assert len(response) > 0


def test_agent_initialization_with_roles():
    """Test agent initialization with different roles."""
    from src.llm.adk_agent import ADKAgent

    # Test proposer
    agent_jamal = ADKAgent(api_key="test_key", role="proposer")
    assert agent_jamal.role == "proposer"
    assert agent_jamal.agent_name == "AgentJamal"

    # Test opposer
    agent_ryan = ADKAgent(api_key="test_key", role="opposer")
    assert agent_ryan.role == "opposer"
    assert agent_ryan.agent_name == "AgentRyan"

    # Test mediator
    agent_james = ADKAgent(api_key="test_key", role="mediator")
    assert agent_james.role == "mediator"
    assert agent_james.agent_name == "AgentJames"


def test_invalid_role_raises_error():
    """Test that invalid role raises ValueError."""
    from src.llm.adk_agent import ADKAgent

    with pytest.raises(ValueError, match="Invalid role"):
        ADKAgent(api_key="test_key", role="invalid_role")


def test_session_service_accessible():
    """Test that session service is accessible via runner."""
    from src.llm.adk_agent import ADKAgent

    agent = ADKAgent(api_key="test_key", role="proposer")
    assert agent.runner.session_service is not None
