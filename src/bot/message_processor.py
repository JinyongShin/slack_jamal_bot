"""Message processing logic."""

import re
from typing import Optional, Dict
from src.utils.logger import setup_logger
from src.config import Config

logger = setup_logger(__name__, Config.LOG_LEVEL)


class MessageProcessor:
    """Process incoming Slack messages."""

    def __init__(self, llm_client, tool_handlers: Optional[Dict] = None):
        """
        Initialize message processor.

        Args:
            llm_client: LLM client for generating responses
            tool_handlers: Dictionary mapping function names to handler functions
                          (deprecated for ADKAgent, kept for backward compatibility)
        """
        self.llm_client = llm_client
        self.tool_handlers = tool_handlers or {}

        # ADKAgent manages tools internally, no need for external tool_handlers
        if tool_handlers and self._is_adk_agent():
            logger.warning("tool_handlers are ignored when using ADKAgent - tools are managed internally")

        logger.info(f"MessageProcessor initialized with {len(self.tool_handlers)} tool handlers")

    def _is_adk_agent(self) -> bool:
        """
        Check if the LLM client is an ADKAgent instance.

        Returns:
            True if the client is ADKAgent, False otherwise
        """
        return self.llm_client.__class__.__name__ == 'ADKAgent'

    def _generate_response(self, text: str) -> str:
        """
        Generate response using the appropriate method based on client type.

        Args:
            text: Cleaned message text

        Returns:
            Generated response text
        """
        # ADKAgent handles tools internally, always use generate_response
        if self._is_adk_agent():
            return self.llm_client.generate_response(text)

        # Legacy clients may have separate tool handling
        if self.tool_handlers and hasattr(self.llm_client, 'generate_response_with_tools'):
            return self.llm_client.generate_response_with_tools(
                text,
                tool_handlers=self.tool_handlers
            )

        # Default: simple generate_response
        return self.llm_client.generate_response(text)

    def process_message(self, text: str, user: str, channel: str, thread_ts: str) -> str:
        """
        Process a message and generate a response.

        Args:
            text: Message text
            user: User ID
            channel: Channel ID
            thread_ts: Thread timestamp

        Returns:
            Response text
        """
        try:
            # Clean up message text (remove bot mention)
            cleaned_text = self._clean_message_text(text)

            logger.info(f"Processing message from user {user}: {cleaned_text}")

            # Generate response based on client type
            response = self._generate_response(cleaned_text)

            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return f"죄송합니다. 메시지 처리 중 오류가 발생했습니다: {str(e)}"

    def _clean_message_text(self, text: str) -> str:
        """
        Clean message text by removing bot mentions.

        Args:
            text: Raw message text

        Returns:
            Cleaned message text
        """
        # Remove bot mention (e.g., <@U12345678>)
        cleaned = re.sub(r"<@[A-Z0-9]+>", "", text)
        # Remove extra whitespace
        cleaned = " ".join(cleaned.split())
        return cleaned.strip()
