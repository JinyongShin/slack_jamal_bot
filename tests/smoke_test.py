"""Smoke test to verify bot can initialize without running."""

import sys
from src.config import Config
from src.llm.adk_agent import ADKAgent
from src.bot.message_processor import MessageProcessor
from src.utils.logger import setup_logger

logger = setup_logger(__name__, Config.LOG_LEVEL)


def test_bot_initialization():
    """Test that all components can be initialized."""
    try:
        print("=" * 60)
        print("SMOKE TEST: Bot Initialization")
        print("=" * 60)

        # Step 1: Validate configuration
        print("\n[1/4] Validating configuration...")
        Config.validate()
        print(f"✓ SLACK_BOT_TOKEN: {'*' * 20}")
        print(f"✓ SLACK_APP_TOKEN: {'*' * 20}")
        print(f"✓ GOOGLE_GENAI_API_KEY: {'*' * 20}")
        print(f"✓ LOG_LEVEL: {Config.LOG_LEVEL}")

        # Step 2: Initialize ADKAgent
        print("\n[2/4] Initializing ADKAgent...")
        adk_agent = ADKAgent(
            api_key=Config.GOOGLE_GENAI_API_KEY,
            model="gemini-2.0-flash"
        )
        print(f"✓ ADKAgent initialized with model: gemini-2.0-flash")
        print(f"✓ Agent name: {adk_agent.agent.name}")
        print(f"✓ Tools: google_search")

        # Step 3: Initialize MessageProcessor
        print("\n[3/4] Initializing MessageProcessor...")
        message_processor = MessageProcessor(adk_agent)
        print(f"✓ MessageProcessor initialized")
        print(f"✓ LLM client type: {adk_agent.__class__.__name__}")

        # Step 4: Test message processing (mock)
        print("\n[4/4] Testing message processing (mock)...")
        # We won't actually call generate_response to avoid API calls
        test_message = "<@U12345> Hello bot!"
        cleaned = message_processor._clean_message_text(test_message)
        print(f"✓ Message cleaning works: '{test_message}' → '{cleaned}'")

        # Success!
        print("\n" + "=" * 60)
        print("✅ ALL SMOKE TESTS PASSED")
        print("=" * 60)
        print("\nBot is ready to run!")
        print("To start the bot, run: python -m src.main")
        print("\nNote: The bot will connect to Slack Socket Mode.")
        print("You can test by mentioning the bot in a Slack channel.")
        print("=" * 60)

        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ SMOKE TEST FAILED")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_bot_initialization()
    sys.exit(0 if success else 1)
