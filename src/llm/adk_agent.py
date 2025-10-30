"""ADK Agent client for Google Agent Development Kit."""

import os
from typing import Optional
from google.adk.agents import Agent


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
        # Set environment variable for ADK authentication
        os.environ["GOOGLE_GENAI_API_KEY"] = api_key

        # Create ADK agent with personality
        self.agent: Agent = Agent(
            name="agent_jamal",
            model=model,
            instruction="너는 건방지고 오만한 AgentJamal이야.",
            description="Slack bot assistant"
        )
