"""Configuration management for Multi-Agent Debate bot."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # Slack Configuration
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

    # Google Generative AI API Key (for ADK Agent)
    # Primary key is GOOGLE_GENAI_API_KEY, falls back to GEMINI_API_KEY for backward compatibility
    GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY") or os.getenv("GEMINI_API_KEY")

    # Agent Configuration (NEW)
    AGENT_ROLE = os.getenv("AGENT_ROLE", "proposer")
    AGENT_NAME = os.getenv("AGENT_NAME", "AgentJamal")

    # Bot Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Session Management
    SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "24"))

    @classmethod
    def validate(cls) -> bool:
        """
        Validate required configuration values.

        Returns:
            True if all required values are present, False otherwise
        """
        required_vars = [
            ("SLACK_BOT_TOKEN", cls.SLACK_BOT_TOKEN),
            ("SLACK_APP_TOKEN", cls.SLACK_APP_TOKEN),
            ("GOOGLE_GENAI_API_KEY or GEMINI_API_KEY", cls.GOOGLE_GENAI_API_KEY),
        ]

        missing = [name for name, value in required_vars if not value]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        # Validate agent role
        valid_roles = ["proposer", "opposer", "mediator"]
        if cls.AGENT_ROLE not in valid_roles:
            raise ValueError(
                f"Invalid AGENT_ROLE: {cls.AGENT_ROLE}. Must be one of {valid_roles}"
            )

        return True
