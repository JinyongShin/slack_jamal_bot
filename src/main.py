"""Main entry point for Multi-Agent Debate Slack bot."""

import sys
from src.config import Config
from src.utils.logger import setup_logger
from src.llm.adk_agent import ADKAgent
from src.bot.message_processor import MessageProcessor
from src.bot.slack_handler import SlackBot

logger = setup_logger(__name__, Config.LOG_LEVEL)


def main():
    """Main function to start the bot."""
    try:
        logger.info(f"Starting {Config.AGENT_NAME} ({Config.AGENT_ROLE})...")

        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")

        # Initialize ADKAgent with role
        adk_agent = ADKAgent(
            api_key=Config.GOOGLE_GENAI_API_KEY,
            role=Config.AGENT_ROLE,
            model="gemini-2.0-flash"
        )
        logger.info(f"{Config.AGENT_NAME} initialized with role: {Config.AGENT_ROLE}")

        # Initialize MessageProcessor with ADKAgent
        # Note: ADKAgent manages tools internally, no need for tool_handlers
        message_processor = MessageProcessor(adk_agent)

        # Initialize SlackBot
        slack_bot = SlackBot(message_processor)

        # Start bot
        logger.info(f"{Config.AGENT_NAME} initialization complete. Starting Socket Mode handler...")
        slack_bot.start()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info(f"{Config.AGENT_NAME} stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
