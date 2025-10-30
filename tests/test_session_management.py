"""Tests for session management functionality."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.llm.adk_agent import ADKAgent


class TestSessionManagement:
    """Test session management in ADKAgent."""

    @pytest.fixture
    def mock_session_service(self):
        """Create a mock session service."""
        service = MagicMock()
        # Mock create_session to return a session with an id
        mock_session = MagicMock()
        mock_session.id = "test_session_123"
        service.create_session = AsyncMock(return_value=mock_session)
        return service

    @pytest.fixture
    def agent_with_mock(self, mock_session_service):
        """Create ADKAgent with mocked session service."""
        with patch.dict('os.environ', {
            'GOOGLE_GENAI_USE_VERTEXAI': 'FALSE',
            'GOOGLE_API_KEY': 'test_key'
        }):
            agent = ADKAgent(api_key="test_key")
            agent.runner.session_service = mock_session_service
            return agent

    @pytest.mark.asyncio
    async def test_session_created_for_new_thread(self, agent_with_mock, mock_session_service):
        """Test that a new session is created for a new thread."""
        channel = "C123"
        thread_ts = "1234567890.123"
        user_id = "U123"

        session_id = await agent_with_mock._get_or_create_session(
            channel=channel,
            thread_ts=thread_ts,
            user_id=user_id
        )

        # Verify session was created
        mock_session_service.create_session.assert_called_once_with(
            user_id=user_id,
            app_name="slack_jamal_bot"
        )
        assert session_id == "test_session_123"

        # Verify session is cached
        session_key = f"{channel}:{thread_ts}"
        assert session_key in agent_with_mock._session_cache
        assert agent_with_mock._session_cache[session_key]["session_id"] == "test_session_123"

    @pytest.mark.asyncio
    async def test_session_reused_for_existing_thread(self, agent_with_mock, mock_session_service):
        """Test that existing session is reused for the same thread."""
        channel = "C123"
        thread_ts = "1234567890.123"
        user_id = "U123"

        # First call - creates session
        session_id_1 = await agent_with_mock._get_or_create_session(
            channel=channel,
            thread_ts=thread_ts,
            user_id=user_id
        )

        # Second call - should reuse session
        session_id_2 = await agent_with_mock._get_or_create_session(
            channel=channel,
            thread_ts=thread_ts,
            user_id=user_id
        )

        # Session service should only be called once
        assert mock_session_service.create_session.call_count == 1
        # Same session ID should be returned
        assert session_id_1 == session_id_2
        assert session_id_2 == "test_session_123"

    @pytest.mark.asyncio
    async def test_different_threads_have_separate_sessions(self, agent_with_mock, mock_session_service):
        """Test that different threads have separate sessions."""
        channel = "C123"
        thread_ts_1 = "1234567890.123"
        thread_ts_2 = "1234567891.456"
        user_id = "U123"

        # Mock to return different session IDs
        mock_sessions = [
            MagicMock(id="session_1"),
            MagicMock(id="session_2")
        ]
        mock_session_service.create_session.side_effect = mock_sessions

        # Create sessions for two different threads
        session_id_1 = await agent_with_mock._get_or_create_session(
            channel=channel,
            thread_ts=thread_ts_1,
            user_id=user_id
        )
        session_id_2 = await agent_with_mock._get_or_create_session(
            channel=channel,
            thread_ts=thread_ts_2,
            user_id=user_id
        )

        # Should create two separate sessions
        assert mock_session_service.create_session.call_count == 2
        assert session_id_1 != session_id_2
        assert session_id_1 == "session_1"
        assert session_id_2 == "session_2"

    @pytest.mark.asyncio
    async def test_expired_session_is_recreated(self, agent_with_mock, mock_session_service):
        """Test that expired sessions are cleaned up and recreated."""
        channel = "C123"
        thread_ts = "1234567890.123"
        user_id = "U123"

        # Create initial session
        session_id_1 = await agent_with_mock._get_or_create_session(
            channel=channel,
            thread_ts=thread_ts,
            user_id=user_id
        )

        # Manually expire the session
        session_key = f"{channel}:{thread_ts}"
        agent_with_mock._session_cache[session_key]["last_used"] = (
            datetime.now() - timedelta(hours=25)
        )

        # Mock to return a new session
        new_mock_session = MagicMock(id="new_session_456")
        mock_session_service.create_session.return_value = new_mock_session

        # Try to get session again - should create new one
        session_id_2 = await agent_with_mock._get_or_create_session(
            channel=channel,
            thread_ts=thread_ts,
            user_id=user_id
        )

        # Should have created a new session
        assert mock_session_service.create_session.call_count == 2
        assert session_id_2 == "new_session_456"
        assert session_id_1 != session_id_2

    @pytest.mark.asyncio
    async def test_session_last_used_updated_on_access(self, agent_with_mock):
        """Test that last_used timestamp is updated on session access."""
        channel = "C123"
        thread_ts = "1234567890.123"
        user_id = "U123"

        # Create session
        await agent_with_mock._get_or_create_session(
            channel=channel,
            thread_ts=thread_ts,
            user_id=user_id
        )

        session_key = f"{channel}:{thread_ts}"
        first_access_time = agent_with_mock._session_cache[session_key]["last_used"]

        # Wait a bit and access again
        import asyncio
        await asyncio.sleep(0.1)

        await agent_with_mock._get_or_create_session(
            channel=channel,
            thread_ts=thread_ts,
            user_id=user_id
        )

        second_access_time = agent_with_mock._session_cache[session_key]["last_used"]

        # Last used time should be updated
        assert second_access_time > first_access_time

    @pytest.mark.asyncio
    async def test_multiple_expired_sessions_cleaned_up(self, agent_with_mock, mock_session_service):
        """Test that multiple expired sessions are cleaned up."""
        # Create several sessions
        sessions = [
            ("C123", "111.111", "U1"),
            ("C123", "222.222", "U2"),
            ("C456", "333.333", "U3"),
        ]

        for channel, thread_ts, user_id in sessions:
            await agent_with_mock._get_or_create_session(channel, thread_ts, user_id)

        # Should have 3 sessions
        assert len(agent_with_mock._session_cache) == 3

        # Expire first two sessions
        for channel, thread_ts, _ in sessions[:2]:
            session_key = f"{channel}:{thread_ts}"
            agent_with_mock._session_cache[session_key]["last_used"] = (
                datetime.now() - timedelta(hours=25)
            )

        # Access third session - should trigger cleanup
        await agent_with_mock._get_or_create_session(*sessions[2])

        # Should only have 1 active session now
        assert len(agent_with_mock._session_cache) == 1
        assert "C456:333.333" in agent_with_mock._session_cache
