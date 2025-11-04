"""ADK Agent client for Google Agent Development Kit."""

import os
import asyncio
from datetime import datetime
from importlib import import_module
from google.adk.runners import InMemoryRunner
from google.genai import types

from src.llm.agent_roles import AGENT_NAMES
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ADKAgent:
    """
    ADK-based agent client for multi-agent Slack bot debate.

    Supports three roles: proposer, opposer, mediator
    Each agent maintains independent session per thread.
    """

    def __init__(
        self,
        api_key: str,
        role: str = "proposer",
        model: str = "gemini-2.0-flash"
    ) -> None:
        """
        Initialize ADK Agent with specific role.

        Loads agent from file-based structure with independent app_name.

        Args:
            api_key: Google API key for authentication
            role: Agent role (proposer, opposer, mediator)
            model: Model name to use (default: gemini-2.0-flash)
        """
        valid_roles = ["proposer", "opposer", "mediator"]
        if role not in valid_roles:
            raise ValueError(
                f"Invalid role: {role}. Must be one of {valid_roles}"
            )

        self.role = role
        self.agent_name = AGENT_NAMES[role]

        # Set environment variables for local ADK authentication (not Vertex AI)
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
        os.environ["GOOGLE_API_KEY"] = api_key

        # Load agent from file system (file-based agents for proper app_name inference)
        # Map role to agent module path
        agent_module_map = {
            "proposer": "src.agents.jamal.agent",
            "opposer": "src.agents.ryan.agent",
            "mediator": "src.agents.james.agent"
        }

        module_path = agent_module_map[role]
        agent_module = import_module(module_path)
        self.agent = agent_module.root_agent

        # Create InMemoryRunner with INDEPENDENT app_name per agent
        # Each agent maintains its own session pool
        self.runner: InMemoryRunner = InMemoryRunner(
            agent=self.agent,
            app_name=f"debate_{self.agent_name.lower()}"
        )

        logger.info(f"{self.agent_name} initialized with role: {role}")

    async def _get_or_create_session(self, thread_ts: str, user_id: str) -> str:
        """
        Get existing session or create new one for this thread.
        Each agent maintains independent session per thread.

        Args:
            thread_ts: Thread timestamp (used for logging)
            user_id: User ID (thread-based: "thread_{timestamp}")

        Returns:
            Session ID for this agent's conversation with this thread
        """
        app_name = f"debate_{self.agent_name.lower()}"

        # Try to find existing session for this user
        try:
            sessions = await self.runner.session_service.list_sessions(
                app_name=app_name,
                user_id=user_id
            )

            if sessions:
                session_id = sessions[0].id
                logger.info(f"[{self.agent_name}] Reusing session: {session_id}")
                return session_id

        except Exception as e:
            logger.warning(f"[{self.agent_name}] Error listing sessions: {e}")

        # Create new session
        try:
            session = await self.runner.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                state={}  # Initial empty state
            )
            logger.info(f"[{self.agent_name}] Created new session: {session.id}")
            return session.id

        except Exception as e:
            logger.error(f"[{self.agent_name}] Error creating session: {e}", exc_info=True)
            raise

    def generate_response(
        self,
        text: str,
        channel: str = "default",
        thread_ts: str = None,
        user: str = "slack_user"
    ) -> str:
        """
        Generate a response for the given text.

        Each agent maintains independent session per thread.
        ADK automatically manages session creation and retrieval.

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
                # Use thread_ts as user_id for thread-based context
                # Each agent maintains its own session per thread
                if thread_ts is None:
                    thread_ts_key = str(datetime.now().timestamp())
                else:
                    thread_ts_key = thread_ts

                user_id = f"thread_{thread_ts_key}"

                # Get or create session for this agent + thread
                session_id = await self._get_or_create_session(thread_ts_key, user_id)

                logger.info(
                    f"[{self.agent_name}] Generating response | "
                    f"user: {user_id} | session: {session_id}"
                )

                # Send message and collect response
                # session_id is required parameter
                async for event in self.runner.run_async(
                    user_id=user_id,
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
