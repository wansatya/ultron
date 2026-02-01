"""Slack bot integration"""

import logging
import asyncio
from typing import Optional
from .handler import MessageHandler as UltronMessageHandler
from .base import MessagingPlatform, IncomingMessage, OutgoingMessage

logger = logging.getLogger(__name__)

# Try to import slack library
try:
    from slack_bolt.async_app import AsyncApp
    from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    logger.warning("slack-bolt not installed. Slack support disabled.")
    logger.warning("Install with: pip install slack-bolt")


class SlackBot(MessagingPlatform):
    """Slack bot interface for Ultron"""

    def __init__(
        self,
        bot_token: str,
        app_token: str,
        message_handler: Optional[UltronMessageHandler] = None,
        allowed_users: list = None
    ):
        if not SLACK_AVAILABLE:
            raise ImportError(
                "slack-bolt is not installed. "
                "Install with: pip install slack-bolt"
            )

        self.bot_token = bot_token
        self.app_token = app_token
        self.message_handler = message_handler
        self.allowed_users = set(allowed_users) if allowed_users else None
        self._running = False

        # Create Slack app
        self.app = AsyncApp(token=bot_token)
        self.handler: Optional[AsyncSocketModeHandler] = None

        # Register event handlers
        self.app.message("")(self.handle_message)
        self.app.command("/start")(self.start_command)
        self.app.command("/help")(self.help_command)
        self.app.command("/reset")(self.reset_command)

    def platform_name(self) -> str:
        return "slack"

    def is_running(self) -> bool:
        return self._running

    async def handle_message(self, message, say):
        """Handle incoming Slack messages"""
        # Extract message details
        user_id = message["user"]
        text = message["text"]
        channel = message["channel"]

        # Skip bot messages
        if message.get("bot_id"):
            return

        # Check authorization
        if self.allowed_users and user_id not in self.allowed_users:
            await say("Sorry, you are not authorized to use this bot.")
            return

        logger.info(f"Slack message from {user_id}: {text}")

        try:
            # Process through Ultron pipeline
            response = await self.message_handler.handle_message(user_id, text)

            # Send response
            await say(response)

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await say(f"Sorry, I encountered an error: {str(e)}")

    async def start_command(self, ack, command, say):
        """Handle /start command"""
        await ack()

        user_id = command["user_id"]

        if self.allowed_users and user_id not in self.allowed_users:
            await say("Sorry, you are not authorized to use this bot.")
            return

        welcome_message = (
            "*Welcome to Ultron!*\n\n"
            "I'm an intent-based task automation assistant. I can help you:\n"
            "• Execute shell commands\n"
            "• Read and write files\n"
            "• Fetch web content\n"
            "• Search the web\n"
            "• Have general conversations\n\n"
            "Just send me a message and I'll figure out what you need!\n\n"
            "*Commands:*\n"
            "`/help` - Show this help message\n"
            "`/reset` - Reset your session"
        )

        await say(welcome_message)

    async def help_command(self, ack, command, say):
        """Handle /help command"""
        await ack()

        help_message = (
            "*Ultron - Intent-Based Task Automation*\n\n"
            "*Examples:*\n"
            "• 'run ls -la' - Execute a command\n"
            "• 'read config.yaml' - Read a file\n"
            "• 'write hello to test.txt' - Write to a file\n"
            "• 'fetch https://example.com' - Fetch web content\n"
            "• 'search for python tutorials' - Search the web\n"
            "• 'hello' - Chat with me\n\n"
            "*Commands:*\n"
            "`/start` - Welcome message\n"
            "`/help` - This help message\n"
            "`/reset` - Reset your conversation session"
        )

        await say(help_message)

    async def reset_command(self, ack, command, say):
        """Handle /reset command"""
        await ack()

        user_id = command["user_id"]

        if self.allowed_users and user_id not in self.allowed_users:
            await say("Sorry, you are not authorized to use this bot.")
            return

        self.message_handler.session_manager.reset_session(user_id)
        await say("Your session has been reset.")

    async def start(self):
        """Start the Slack bot"""
        logger.info("Starting Slack bot...")
        self._running = True

        # Create socket mode handler
        self.handler = AsyncSocketModeHandler(self.app, self.app_token)
        await self.handler.start_async()

    async def stop(self):
        """Stop the Slack bot"""
        logger.info("Stopping Slack bot...")
        self._running = False
        if self.handler:
            await self.handler.close_async()

    async def send_message(self, message: OutgoingMessage):
        """Send a message via Slack"""
        try:
            await self.app.client.chat_postMessage(
                channel=message.chat_id,
                text=message.text,
                mrkdwn=message.parse_mode == "markdown"
            )
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}", exc_info=True)

    def run(self):
        """Synchronous run method"""
        logger.info("Starting Slack bot...")
        print("Slack bot is running. Press Ctrl+C to stop.")
        asyncio.run(self.start())
