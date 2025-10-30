"""Slack bot event handler."""

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__, Config.LOG_LEVEL)


class SlackBot:
    """Slack bot handler with Socket Mode."""

    def __init__(self, message_processor):
        """
        Initialize Slack bot.

        Args:
            message_processor: Message processing handler
        """
        self.app = App(token=Config.SLACK_BOT_TOKEN)
        self.message_processor = message_processor

        # Register event listeners
        self._register_listeners()

        logger.info("SlackBot initialized successfully")

    def _register_listeners(self):
        """Register Slack event listeners."""

        @self.app.event("app_mention")
        def handle_mention(event, say, client):
            """
            Handle app mention events.

            Args:
                event: Slack event data
                say: Function to send messages
                client: Slack client
            """
            try:
                logger.info(f"Received mention: {event}")

                # Add loading reaction
                try:
                    client.reactions_add(
                        channel=event["channel"],
                        timestamp=event["ts"],
                        name="hourglass_flowing_sand"
                    )
                except SlackApiError as e:
                    logger.warning(f"Failed to add reaction: {e}")

                # Extract message text (remove bot mention)
                text = event.get("text", "")
                user = event.get("user")
                channel = event.get("channel")
                thread_ts = event.get("thread_ts") or event.get("ts")

                # Process message
                response = self.message_processor.process_message(
                    text=text,
                    user=user,
                    channel=channel,
                    thread_ts=thread_ts
                )

                # Send response in thread
                say(
                    text=response,
                    thread_ts=thread_ts
                )

                # Remove loading reaction and add checkmark
                try:
                    client.reactions_remove(
                        channel=event["channel"],
                        timestamp=event["ts"],
                        name="hourglass_flowing_sand"
                    )
                    client.reactions_add(
                        channel=event["channel"],
                        timestamp=event["ts"],
                        name="white_check_mark"
                    )
                except SlackApiError as e:
                    logger.warning(f"Failed to update reaction: {e}")

                logger.info(f"Successfully processed mention from user {user}")

            except Exception as e:
                logger.error(f"Error handling mention: {e}", exc_info=True)
                # Send error message to user
                try:
                    say(
                        text=f"죄송합니다. 메시지 처리 중 오류가 발생했습니다: {str(e)}",
                        thread_ts=event.get("thread_ts") or event.get("ts")
                    )
                except Exception as inner_e:
                    logger.error(f"Failed to send error message: {inner_e}")

    def start(self):
        """Start the Slack bot with Socket Mode."""
        logger.info("Starting Slack bot in Socket Mode...")
        handler = SocketModeHandler(self.app, Config.SLACK_APP_TOKEN)
        handler.start()
