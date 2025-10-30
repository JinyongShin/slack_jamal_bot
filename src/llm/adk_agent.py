"""ADK Agent client for Google Agent Development Kit."""

import os
import asyncio
from google.adk import Agent
from google.adk.runners import InMemoryRunner
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

        # Create ADK agent with personality
        self.agent: Agent = Agent(
            name="agent_jamal",
            model=model,
            instruction="너는 건방지고 오만한 AgentJamal이야.",
            description="Slack bot assistant"
        )

        # Create InMemoryRunner for local execution
        self.runner: InMemoryRunner = InMemoryRunner(
            agent=self.agent,
            app_name="slack_jamal_bot"
        )

    def generate_response(self, text: str) -> str:
        """
        Generate a response for the given text.

        Args:
            text: Input text to respond to

        Returns:
            Generated response text
        """
        async def _get_response() -> str:
            response_text = ""
            try:
                # Create a new session for this conversation
                session = await self.runner.session_service.create_session(
                    user_id="slack_user",
                    app_name="slack_jamal_bot"
                )

                # Send message and collect response
                async for event in self.runner.run_async(
                    user_id="slack_user",
                    session_id=session.id,
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
