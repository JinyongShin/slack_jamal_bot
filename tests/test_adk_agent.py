"""Tests for ADKAgent class."""


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
