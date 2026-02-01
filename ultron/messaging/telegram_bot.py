"""Telegram bot integration"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from .handler import MessageHandler as UltronMessageHandler
from .base import MessagingPlatform, IncomingMessage, OutgoingMessage

logger = logging.getLogger(__name__)


class TelegramBot(MessagingPlatform):
    """Telegram bot interface for Ultron"""

    def __init__(self, token: str, message_handler: UltronMessageHandler, allowed_users: list = None):
        self.token = token
        self.message_handler = message_handler
        self.allowed_users = set(allowed_users) if allowed_users else None
        self._running = False

        # Create application
        self.app = Application.builder().token(token).build()

        # Register handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("reset", self.reset_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))

    def platform_name(self) -> str:
        return "telegram"

    def is_running(self) -> bool:
        return self._running

    def _is_user_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to use the bot"""
        if self.allowed_users is None:
            return True
        return user_id in self.allowed_users

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id

        if not self._is_user_allowed(user_id):
            await update.message.reply_text("Sorry, you are not authorized to use this bot.")
            return

        welcome_message = (
            "Welcome to Ultron!\n\n"
            "I'm an intent-based task automation assistant. I can help you:\n"
            "- Execute shell commands\n"
            "- Read and write files\n"
            "- Fetch web content\n"
            "- Search the web\n"
            "- Have general conversations\n\n"
            "Just send me a message and I'll figure out what you need!\n\n"
            "Commands:\n"
            "/help - Show this help message\n"
            "/reset - Reset your session"
        )

        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "Ultron - Intent-Based Task Automation\n\n"
            "Examples:\n"
            "- 'run ls -la' - Execute a command\n"
            "- 'read config.yaml' - Read a file\n"
            "- 'write hello to test.txt' - Write to a file\n"
            "- 'fetch https://example.com' - Fetch web content\n"
            "- 'search for python tutorials' - Search the web\n"
            "- 'hello' - Chat with me\n\n"
            "Commands:\n"
            "/start - Welcome message\n"
            "/help - This help message\n"
            "/reset - Reset your conversation session"
        )

        await update.message.reply_text(help_message)

    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reset command"""
        user_id = str(update.effective_user.id)

        if not self._is_user_allowed(update.effective_user.id):
            await update.message.reply_text("Sorry, you are not authorized to use this bot.")
            return

        self.message_handler.session_manager.reset_session(user_id)
        await update.message.reply_text("Your session has been reset.")

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        user_id = str(update.effective_user.id)
        user_name = update.effective_user.username or update.effective_user.first_name
        message = update.message.text

        if not self._is_user_allowed(int(user_id)):
            await update.message.reply_text("Sorry, you are not authorized to use this bot.")
            return

        logger.info(f"Message from {user_name} ({user_id}): {message}")

        try:
            # Process message through pipeline
            response = await self.message_handler.handle_message(user_id, message)

            # Send response
            await update.message.reply_text(response, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await update.message.reply_text(f"Sorry, I encountered an error: {str(e)}")

    async def start(self):
        """Start the bot"""
        logger.info("Starting Telegram bot...")
        self._running = True
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping Telegram bot...")
        self._running = False
        if self.app.updater.running:
            await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

    async def send_message(self, message: OutgoingMessage):
        """Send a message via Telegram"""
        try:
            await self.app.bot.send_message(
                chat_id=message.chat_id,
                text=message.text,
                parse_mode=message.parse_mode
            )
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}", exc_info=True)

    def run(self):
        """Synchronous run method for backward compatibility"""
        logger.info("Starting Telegram bot...")
        print("Telegram bot is running. Press Ctrl+C to stop.")
        self._running = True
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
