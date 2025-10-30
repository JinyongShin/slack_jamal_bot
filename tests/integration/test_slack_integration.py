"""Integration tests for Slack bot with ADKAgent."""

import pytest
from unittest.mock import Mock, patch
from src.config import Config
from src.llm.adk_agent import ADKAgent
from src.bot.message_processor import MessageProcessor


@pytest.mark.integration
@pytest.mark.skipif(
    not Config.GOOGLE_GENAI_API_KEY or Config.GOOGLE_GENAI_API_KEY == "test-api-key",
    reason="Google API key not set or is test key"
)
def test_slack_mention_to_response_flow():
    """Test the full flow: Slack mention → ADKAgent → response."""
    # Initialize ADKAgent (real instance, will use real API)
    adk_agent = ADKAgent(api_key=Config.GOOGLE_GENAI_API_KEY)

    # Initialize MessageProcessor with ADKAgent
    processor = MessageProcessor(adk_agent)

    # Simulate Slack mention
    slack_text = "<@U12345678> 안녕! 간단히 인사해줘"
    user_id = "U_TEST_USER"
    channel_id = "C_TEST_CHANNEL"
    thread_ts = "1234567890.123456"

    # Process message
    response = processor.process_message(
        text=slack_text,
        user=user_id,
        channel=channel_id,
        thread_ts=thread_ts
    )

    # Verify response
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)
    assert "오류" not in response  # Should not be an error
    # Bot mention should be removed from input
    assert "<@U12345678>" not in response


@pytest.mark.integration
@pytest.mark.skipif(
    not Config.GOOGLE_GENAI_API_KEY or Config.GOOGLE_GENAI_API_KEY == "test-api-key",
    reason="Google API key not set or is test key"
)
def test_adk_agent_with_google_search():
    """Test ADKAgent can use google_search tool for latest information."""
    # Initialize ADKAgent
    adk_agent = ADKAgent(api_key=Config.GOOGLE_GENAI_API_KEY)

    # Initialize MessageProcessor
    processor = MessageProcessor(adk_agent)

    # Ask for information that requires search
    response = processor.process_message(
        text="오늘 날씨 어때?",  # Simple weather query
        user="U_TEST",
        channel="C_TEST",
        thread_ts="1234567890.123456"
    )

    # Verify response was generated
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)


@pytest.mark.integration
def test_message_processor_with_mock_adk_agent():
    """Test MessageProcessor integration with mocked ADKAgent."""
    # Create a mock ADKAgent
    with patch.object(ADKAgent, '__init__', return_value=None):
        mock_agent = ADKAgent(api_key="test-key")
        mock_agent.generate_response = Mock(return_value="건방진 AgentJamal의 응답이야!")

        # Initialize MessageProcessor with mock
        processor = MessageProcessor(mock_agent)

        # Process message
        response = processor.process_message(
            text="<@U12345> 테스트 메시지",
            user="U_TEST",
            channel="C_TEST",
            thread_ts="1234567890.123456"
        )

        # Verify
        assert response == "건방진 AgentJamal의 응답이야!"
        mock_agent.generate_response.assert_called_once_with("테스트 메시지")
