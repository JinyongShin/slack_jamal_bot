"""ADK Agent client for Google Agent Development Kit."""

import os
import asyncio
from datetime import datetime
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

from src.utils.session_registry import FileSessionRegistry
from src.llm.agent_roles import AGENT_INSTRUCTIONS, AGENT_NAMES
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ADKAgent:
    """
    ADK-based agent client for multi-agent Slack bot debate.

    Supports three roles: proposer, opposer, mediator
    Uses shared session registry for conversation history sharing.
    """

    def __init__(
        self,
        api_key: str,
        role: str = "proposer",
        model: str = "gemini-2.0-flash"
    ) -> None:
        """
        Initialize ADK Agent with specific role.

        Args:
            api_key: Google API key for authentication
            role: Agent role (proposer, opposer, mediator)
            model: Model name to use (default: gemini-2.0-flash)
        """
        if role not in AGENT_INSTRUCTIONS:
            raise ValueError(
                f"Invalid role: {role}. Must be one of {list(AGENT_INSTRUCTIONS.keys())}"
            )

        self.role = role
        self.agent_name = AGENT_NAMES[role]

        # Initialize shared session registry
        self.session_registry = FileSessionRegistry()

        # Set environment variables for local ADK authentication (not Vertex AI)
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
        os.environ["GOOGLE_API_KEY"] = api_key

        # Create ADK agent with role-specific instruction
        self.agent: Agent = Agent(
            name=self.agent_name,
            model=model,
            instruction=AGENT_INSTRUCTIONS[role],
            description=f"{self.agent_name} - {role.capitalize()} agent for multi-agent debate",
            tools=[google_search]
        )

        # Create InMemoryRunner for local execution
        self.runner: InMemoryRunner = InMemoryRunner(
            agent=self.agent,
            app_name=f"debate_{self.agent_name}"
        )

        logger.info(f"{self.agent_name} initialized with role: {role}")

    async def _get_or_create_shared_session(self, thread_ts: str) -> str:
        """
        Get existing session or create a new one for the thread.
        Uses shared session registry so all agents can access the same conversation.

        Args:
            thread_ts: Slack thread timestamp

        Returns:
            Session ID for the thread
        """
        # Check registry first
        session_id = self.session_registry.get_session_id(thread_ts)

        if session_id:
            logger.info(f"[{self.agent_name}] Using existing shared session: {session_id}")
            return session_id

        # Create new session
        session = await self.runner.session_service.create_session(
            user_id=f"debate_thread_{thread_ts}",
            app_name="multi_agent_debate"
        )

        # Store in registry for other agents
        self.session_registry.set_session_id(thread_ts, session.id)
        logger.info(f"[{self.agent_name}] Created new shared session: {session.id}")

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
            thread_ts: Slack thread timestamp (default: None)
            user: Slack user ID (default: "slack_user")

        Returns:
            Generated response text
        """
        async def _get_response() -> str:
            response_text = ""
            try:
                # Use thread_ts if provided, otherwise use current timestamp
                if thread_ts is None:
                    thread_ts_key = str(datetime.now().timestamp())
                else:
                    thread_ts_key = thread_ts

                # Get or create shared session for this thread
                session_id = await self._get_or_create_shared_session(thread_ts_key)

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
                logger.error(f"[{self.agent_name}] Error generating response: {e}", exc_info=True)
                return f"Error generating response: {str(e)}"

            return response_text if response_text else "No response generated"

        # Run async function in sync context
        return asyncio.run(_get_response())
