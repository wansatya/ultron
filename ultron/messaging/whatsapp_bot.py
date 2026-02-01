"""WhatsApp bot integration using webwhatsapp"""

import logging
import asyncio
from typing import Optional
from .handler import MessageHandler as UltronMessageHandler
from .base import MessagingPlatform, IncomingMessage, OutgoingMessage

logger = logging.getLogger(__name__)

# Try to import whatsapp library
try:
    from webwhatsapi import WhatsAPIDriver
    from webwhatsapi.objects.message import Message
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    logger.warning("webwhatsapi not installed. WhatsApp support disabled.")
    logger.warning("Install with: pip install webwhatsapi")


class WhatsAppBot(MessagingPlatform):
    """WhatsApp bot interface for Ultron using WhatsApp Web API"""

    def __init__(
        self,
        profile_path: str = "./data/whatsapp_session",
        message_handler: Optional[UltronMessageHandler] = None,
        allowed_users: list = None
    ):
        if not WHATSAPP_AVAILABLE:
            raise ImportError(
                "webwhatsapi is not installed. "
                "Install with: pip install webwhatsapi selenium"
            )

        self.profile_path = profile_path
        self.message_handler = message_handler
        self.allowed_users = set(allowed_users) if allowed_users else None
        self._running = False
        self.driver: Optional[WhatsAPIDriver] = None
        self.last_message_id = None

    def platform_name(self) -> str:
        return "whatsapp"

    def is_running(self) -> bool:
        return self._running

    async def start(self):
        """Start the WhatsApp bot"""
        logger.info("Starting WhatsApp bot...")
        print("\n" + "=" * 60)
        print("WhatsApp Bot Starting")
        print("=" * 60)
        print("\nScan the QR code with your WhatsApp mobile app")
        print("(WhatsApp > Settings > Linked Devices > Link a Device)")
        print("")

        try:
            # Initialize driver
            self.driver = WhatsAPIDriver(
                profile=self.profile_path,
                client='chrome'
            )

            self._running = True

            # Wait for WhatsApp Web to load
            print("Waiting for WhatsApp Web to load...")
            self.driver.wait_for_login()
            print("Logged in successfully!\n")

            # Start message polling loop
            await self._poll_messages()

        except Exception as e:
            logger.error(f"Error starting WhatsApp bot: {e}", exc_info=True)
            self._running = False
            raise

    async def stop(self):
        """Stop the WhatsApp bot"""
        logger.info("Stopping WhatsApp bot...")
        self._running = False
        if self.driver:
            self.driver.quit()

    async def send_message(self, message: OutgoingMessage):
        """Send a message via WhatsApp"""
        if not self.driver:
            logger.error("WhatsApp driver not initialized")
            return

        try:
            # WhatsApp uses phone numbers or chat IDs
            self.driver.send_message_to_id(message.chat_id, message.text)
            logger.info(f"Sent message to {message.chat_id}")

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}", exc_info=True)

    async def _poll_messages(self):
        """Poll for new messages"""
        logger.info("Starting message polling...")

        while self._running:
            try:
                # Get unread messages
                unread = self.driver.get_unread()

                for chat in unread:
                    # Process each unread message
                    for message in chat.messages:
                        if isinstance(message, Message):
                            await self._handle_message(chat, message)

                # Mark messages as seen
                if unread:
                    # Optional: mark as read
                    pass

                # Wait before next poll
                await asyncio.sleep(2)

            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error polling messages: {e}", exc_info=True)
                await asyncio.sleep(5)

    async def _handle_message(self, chat, message):
        """Handle an individual WhatsApp message"""
        # Extract message details
        user_id = message.sender.id if hasattr(message, 'sender') else chat.id
        user_name = message.sender.get_safe_name() if hasattr(message, 'sender') else "Unknown"
        text = message.content if hasattr(message, 'content') else str(message)

        # Skip if already processed
        message_id = message.id if hasattr(message, 'id') else None
        if message_id == self.last_message_id:
            return
        self.last_message_id = message_id

        # Check authorization
        if self.allowed_users and user_id not in self.allowed_users:
            await self.send_message(OutgoingMessage(
                chat_id=chat.id,
                text="Sorry, you are not authorized to use this bot."
            ))
            return

        logger.info(f"WhatsApp message from {user_name} ({user_id}): {text}")

        # Handle commands
        if text.startswith('/'):
            await self._handle_command(chat.id, text, user_id)
            return

        # Process through Ultron pipeline
        try:
            response = await self.message_handler.handle_message(str(user_id), text)
            await self.send_message(OutgoingMessage(
                chat_id=chat.id,
                text=response
            ))
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await self.send_message(OutgoingMessage(
                chat_id=chat.id,
                text=f"Sorry, I encountered an error: {str(e)}"
            ))

    async def _handle_command(self, chat_id: str, command: str, user_id: str):
        """Handle WhatsApp commands"""
        if command == "/start":
            message = (
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
        elif command == "/help":
            message = (
                "Ultron - Intent-Based Task Automation\n\n"
                "Examples:\n"
                "- 'run ls -la' - Execute a command\n"
                "- 'read config.yaml' - Read a file\n"
                "- 'write hello to test.txt' - Write to a file\n"
                "- 'fetch https://example.com' - Fetch web content\n"
                "- 'search for python tutorials' - Search the web\n"
                "- 'hello' - Chat with me"
            )
        elif command == "/reset":
            self.message_handler.session_manager.reset_session(str(user_id))
            message = "Your session has been reset."
        else:
            message = f"Unknown command: {command}\nSend /help for available commands."

        await self.send_message(OutgoingMessage(chat_id=chat_id, text=message))

    def run(self):
        """Synchronous run method"""
        asyncio.run(self.start())
