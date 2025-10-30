"""Unit tests for MessageProcessor."""

import pytest
from unittest.mock import Mock, patch
from src.bot.message_processor import MessageProcessor
from src.llm.adk_agent import ADKAgent


@pytest.fixture
def mock_llm_client():
    """Create mock LLM client."""
    client = Mock()
    client.generate_response.return_value = "Test response"
    client.generate_response_with_tools.return_value = "Test response with tools"
    return client


@pytest.fixture
def message_processor(mock_llm_client):
    """Create MessageProcessor instance."""
    return MessageProcessor(mock_llm_client)


@pytest.fixture
def message_processor_with_tools(mock_llm_client):
    """Create MessageProcessor with tool handlers."""
    tool_handlers = {
        "test_tool": Mock(return_value="Tool result")
    }
    return MessageProcessor(mock_llm_client, tool_handlers=tool_handlers)


def test_message_processor_initialization(mock_llm_client):
    """Test MessageProcessor initialization."""
    processor = MessageProcessor(mock_llm_client)

    assert processor.llm_client == mock_llm_client
    assert processor.tool_handlers == {}


def test_message_processor_initialization_with_tools(mock_llm_client):
    """Test MessageProcessor initialization with tool handlers."""
    tools = {"tool1": Mock()}
    processor = MessageProcessor(mock_llm_client, tool_handlers=tools)

    assert processor.tool_handlers == tools
    assert len(processor.tool_handlers) == 1


def test_clean_message_text_removes_mention(message_processor):
    """Test that bot mentions are removed from message text."""
    text = "<@U12345678> Hello, bot!"

    cleaned = message_processor._clean_message_text(text)

    assert cleaned == "Hello, bot!"
    assert "<@U12345678>" not in cleaned


def test_clean_message_text_removes_multiple_mentions(message_processor):
    """Test that multiple mentions are removed."""
    text = "<@U12345678> <@U87654321> Hey there"

    cleaned = message_processor._clean_message_text(text)

    assert "<@" not in cleaned
    assert "Hey there" in cleaned


def test_clean_message_text_removes_extra_whitespace(message_processor):
    """Test that extra whitespace is removed."""
    text = "<@U12345678>   multiple    spaces   here  "

    cleaned = message_processor._clean_message_text(text)

    assert cleaned == "multiple spaces here"
    assert "  " not in cleaned


def test_process_message_without_tools(message_processor, mock_llm_client):
    """Test message processing without tool handlers."""
    response = message_processor.process_message(
        text="<@U12345> Test message",
        user="U67890",
        channel="C11111",
        thread_ts="1234.5678"
    )

    assert response == "Test response"
    mock_llm_client.generate_response.assert_called_once_with("Test message")


def test_process_message_with_tools(message_processor_with_tools, mock_llm_client):
    """Test message processing with tool handlers."""
    response = message_processor_with_tools.process_message(
        text="<@U12345> Use a tool",
        user="U67890",
        channel="C11111",
        thread_ts="1234.5678"
    )

    assert response == "Test response with tools"
    mock_llm_client.generate_response_with_tools.assert_called_once()


def test_process_message_handles_exceptions(message_processor, mock_llm_client):
    """Test that exceptions during processing are handled."""
    mock_llm_client.generate_response.side_effect = Exception("Test error")

    response = message_processor.process_message(
        text="Test",
        user="U123",
        channel="C111",
        thread_ts="1234.5678"
    )

    assert "오류가 발생했습니다" in response
    assert "Test error" in response


def test_process_message_empty_text(message_processor):
    """Test processing empty message."""
    response = message_processor.process_message(
        text="",
        user="U123",
        channel="C111",
        thread_ts="1234.5678"
    )

    assert response is not None


def test_message_processor_uses_adk_agent():
    """Test that MessageProcessor can use ADKAgent without tools."""
    # Mock ADKAgent's generate_response method
    with patch.object(ADKAgent, 'generate_response', return_value="ADK response"):
        # Create real ADKAgent instance (mocked generate_response)
        with patch.object(ADKAgent, '__init__', return_value=None):
            adk_agent = ADKAgent(api_key="test_key")
            adk_agent.generate_response = Mock(return_value="ADK response")

            # Create MessageProcessor with ADKAgent (no tools)
            processor = MessageProcessor(adk_agent)

            # Process message
            response = processor.process_message(
                text="<@U12345> Test message",
                user="U67890",
                channel="C11111",
                thread_ts="1234.5678"
            )

            # Verify ADKAgent was called with cleaned text and session info
            adk_agent.generate_response.assert_called_once_with(
                text="Test message",
                channel="C11111",
                thread_ts="1234.5678",
                user="U67890"
            )
            assert response == "ADK response"


def test_message_processor_with_adk_agent_ignores_tools():
    """Test that MessageProcessor uses only generate_response even when tools are provided."""
    # Mock ADKAgent's generate_response method
    with patch.object(ADKAgent, '__init__', return_value=None):
        adk_agent = ADKAgent(api_key="test_key")
        adk_agent.generate_response = Mock(return_value="ADK response")

        # Create MessageProcessor with ADKAgent and tools
        tool_handlers = {"test_tool": Mock(return_value="Tool result")}
        processor = MessageProcessor(adk_agent, tool_handlers=tool_handlers)

        # Process message
        response = processor.process_message(
            text="<@U12345> Test message with tools",
            user="U67890",
            channel="C11111",
            thread_ts="1234.5678"
        )

        # ADKAgent should use generate_response, not generate_response_with_tools
        adk_agent.generate_response.assert_called_once_with(
            text="Test message with tools",
            channel="C11111",
            thread_ts="1234.5678",
            user="U67890"
        )
        assert response == "ADK response"
