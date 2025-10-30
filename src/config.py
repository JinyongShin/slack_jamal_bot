"""Configuration management for AgentJamal bot."""

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

    # Bot Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

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

        return True
