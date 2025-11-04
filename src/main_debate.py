"""Main entry point for Multi-Agent Debate Orchestrator."""

import sys
from slack_sdk import WebClient
from src.config import Config
from src.utils.logger import setup_logger
from src.llm.adk_agent import ADKAgent
from src.bot.message_processor import MessageProcessor
from src.bot.slack_handler import SlackBot
from src.orchestrator import DebateOrchestrator

logger = setup_logger(__name__, Config.LOG_LEVEL)


def main():
    """Main function to start the multi-agent debate orchestrator."""
    try:
        logger.info("Starting Multi-Agent Debate Orchestrator...")

        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")

        # Initialize all three agents
        logger.info("Initializing AgentJamal (Proposer)...")
        jamal_agent = ADKAgent(
            api_key=Config.GOOGLE_GENAI_API_KEY,
            role="proposer",
            model="gemini-2.0-flash"
        )

        logger.info("Initializing AgentRyan (Opposer)...")
        ryan_agent = ADKAgent(
            api_key=Config.GOOGLE_GENAI_API_KEY,
            role="opposer",
            model="gemini-2.0-flash"
        )

        logger.info("Initializing AgentJames (Mediator)...")
        james_agent = ADKAgent(
            api_key=Config.GOOGLE_GENAI_API_KEY,
            role="mediator",
            model="gemini-2.0-flash"
        )

        logger.info("All agents initialized successfully")

        # Initialize Slack client for orchestrator
        slack_client = WebClient(token=Config.SLACK_BOT_TOKEN)

        # Initialize DebateOrchestrator
        orchestrator = DebateOrchestrator(
            slack_client=slack_client,
            jamal_agent=jamal_agent,
            ryan_agent=ryan_agent,
            james_agent=james_agent,
            max_rounds=10
        )
        logger.info("DebateOrchestrator initialized")

        # Initialize MessageProcessor (for backward compatibility, uses Jamal as default)
        message_processor = MessageProcessor(jamal_agent)

        # Initialize SlackBot with orchestrator
        slack_bot = SlackBot(
            message_processor=message_processor,
            debate_orchestrator=orchestrator
        )

        # Start bot
        logger.info("Multi-Agent Debate Orchestrator initialization complete. Starting Socket Mode handler...")
        slack_bot.start()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Multi-Agent Debate Orchestrator stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
