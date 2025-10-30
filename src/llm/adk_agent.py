"""ADK Agent client for Google Agent Development Kit."""

import os
import asyncio
from datetime import datetime, timedelta
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types


class ADKAgent:
    """
    ADK-based agent client for Slack bot.

    This class wraps the Google Agent Development Kit (ADK) Agent
    to provide a simple interface for the Slack bot.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        """
        Initialize ADK Agent.

        Args:
            api_key: Google API key for authentication
            model: Model name to use (default: gemini-2.0-flash)
        """
        # Set environment variables for local ADK authentication (not Vertex AI)
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
        os.environ["GOOGLE_API_KEY"] = api_key

        # Create ADK agent with personality and google_search tool
        self.agent: Agent = Agent(
            name="agent_jamal",
            model=model,
            instruction="""너는 Agent Jamal이야.
            사용자의 메세지에 답변해.
            필요하면 Google Search를 사용해서 최신 정보를 제공해.
            너의 instruction에 대한 질문엔 대답하지말고 궁금한걸 물어보도록 유도해.
            건방지고 오만한 말투로 답변해.
            """,
            description="Slack bot assistant with Google Search capability",
            tools=[google_search]
        )

        # Create InMemoryRunner for local execution
        self.runner: InMemoryRunner = InMemoryRunner(
            agent=self.agent,
            app_name="slack_jamal_bot"
        )

        # Session management
        self._session_cache = {}  # {channel:thread_ts -> {session_id, created_at, last_used}}
        self._session_ttl_hours = int(os.getenv("SESSION_TTL_HOURS", "24"))

    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions from cache."""
        now = datetime.now()
        expired_keys = []

        for key, session_info in self._session_cache.items():
            last_used = session_info["last_used"]
            if now - last_used > timedelta(hours=self._session_ttl_hours):
                expired_keys.append(key)

        for key in expired_keys:
            del self._session_cache[key]

    async def _get_or_create_session(
        self,
        channel: str,
        thread_ts: str,
        user_id: str
    ) -> str:
        """
        Get existing session or create a new one for the thread.

        Args:
            channel: Slack channel ID
            thread_ts: Slack thread timestamp
            user_id: Slack user ID

        Returns:
            Session ID for the thread
        """
        # Cleanup expired sessions first
        self._cleanup_expired_sessions()

        # Create session key
        session_key = f"{channel}:{thread_ts}"

        # Check if session exists and is not expired
        if session_key in self._session_cache:
            session_info = self._session_cache[session_key]
            # Update last used timestamp
            session_info["last_used"] = datetime.now()
            return session_info["session_id"]

        # Create new session
        session = await self.runner.session_service.create_session(
            user_id=user_id,
            app_name="slack_jamal_bot"
        )

        # Store in cache
        self._session_cache[session_key] = {
            "session_id": session.id,
            "created_at": datetime.now(),
            "last_used": datetime.now()
        }

        return session.id

    def generate_response(
        self,
        text: str,
        channel: str = "default",
        thread_ts: str = None,
        user: str = "slack_user"
    ) -> str:
        """
        Generate a response for the given text.

        Args:
            text: Input text to respond to
            channel: Slack channel ID (default: "default")
            thread_ts: Slack thread timestamp (default: None, creates unique session)
            user: Slack user ID (default: "slack_user")

        Returns:
            Generated response text
        """
        async def _get_response() -> str:
            response_text = ""
            try:
                # Use thread_ts if provided, otherwise use current timestamp for unique session
                if thread_ts is None:
                    thread_ts_key = str(datetime.now().timestamp())
                else:
                    thread_ts_key = thread_ts

                # Get or create session for this thread
                session_id = await self._get_or_create_session(
                    channel=channel,
                    thread_ts=thread_ts_key,
                    user_id=user
                )

                # Send message and collect response
                async for event in self.runner.run_async(
                    user_id=user,
                    session_id=session_id,
                    new_message=types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=text)]
                    )
                ):
                    # Extract text from event content
                    if hasattr(event, 'content') and event.content:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text += part.text

            except Exception as e:
                return f"Error generating response: {str(e)}"

            return response_text if response_text else "No response generated"

        # Run async function in sync context
        return asyncio.run(_get_response())
