"""Discord bot integration"""

import logging
import asyncio
from typing import Optional
from .handler import MessageHandler as UltronMessageHandler
from .base import MessagingPlatform, IncomingMessage, OutgoingMessage

logger = logging.getLogger(__name__)

# Try to import discord library
try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    logger.warning("discord.py not installed. Discord support disabled.")
    logger.warning("Install with: pip install discord.py")


class DiscordBot(MessagingPlatform):
    """Discord bot interface for Ultron"""

    def __init__(
        self,
        token: str,
        message_handler: Optional[UltronMessageHandler] = None,
        allowed_users: list = None,
        command_prefix: str = "!"
    ):
        if not DISCORD_AVAILABLE:
            raise ImportError(
                "discord.py is not installed. "
                "Install with: pip install discord.py"
            )

        self.token = token
        self.message_handler = message_handler
        self.allowed_users = set(allowed_users) if allowed_users else None
        self._running = False

        # Create bot with intents
        intents = discord.Intents.default()
        intents.message_content = True  # Required for reading messages

        self.bot = commands.Bot(command_prefix=command_prefix, intents=intents)

        # Register event handlers
        self.bot.event(self.on_ready)
        self.bot.event(self.on_message)

        # Register commands
        @self.bot.command(name='start')
        async def start_cmd(ctx):
            await self._start_command(ctx)

        @self.bot.command(name='help')
        async def help_cmd(ctx):
            await self._help_command(ctx)

        @self.bot.command(name='reset')
        async def reset_cmd(ctx):
            await self._reset_command(ctx)

    def platform_name(self) -> str:
        return "discord"

    def is_running(self) -> bool:
        return self._running

    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Discord bot logged in as {self.bot.user}")
        print(f"Discord bot connected as {self.bot.user.name}")
        self._running = True

    async def on_message(self, message: discord.Message):
        """Handle incoming Discord messages"""
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Check if it's a command (starts with prefix)
        if message.content.startswith(self.bot.command_prefix):
            await self.bot.process_commands(message)
            return

        # Extract user info
        user_id = str(message.author.id)
        user_name = message.author.name
        text = message.content
        chat_id = str(message.channel.id)

        # Check authorization
        if self.allowed_users and int(user_id) not in self.allowed_users:
            await message.channel.send("Sorry, you are not authorized to use this bot.")
            return

        logger.info(f"Discord message from {user_name} ({user_id}): {text}")

        try:
            # Process through Ultron pipeline
            response = await self.message_handler.handle_message(user_id, text)

            # Send response
            await message.channel.send(response)

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await message.channel.send(f"Sorry, I encountered an error: {str(e)}")

    async def _start_command(self, ctx):
        """Handle !start command"""
        user_id = ctx.author.id

        if self.allowed_users and user_id not in self.allowed_users:
            await ctx.send("Sorry, you are not authorized to use this bot.")
            return

        welcome_message = (
            "**Welcome to Ultron!**\n\n"
            "I'm an intent-based task automation assistant. I can help you:\n"
            "- Execute shell commands\n"
            "- Read and write files\n"
            "- Fetch web content\n"
            "- Search the web\n"
            "- Have general conversations\n\n"
            "Just send me a message and I'll figure out what you need!\n\n"
            "**Commands:**\n"
            "`!help` - Show this help message\n"
            "`!reset` - Reset your session"
        )

        await ctx.send(welcome_message)

    async def _help_command(self, ctx):
        """Handle !help command"""
        help_message = (
            "**Ultron - Intent-Based Task Automation**\n\n"
            "**Examples:**\n"
            "- 'run ls -la' - Execute a command\n"
            "- 'read config.yaml' - Read a file\n"
            "- 'write hello to test.txt' - Write to a file\n"
            "- 'fetch https://example.com' - Fetch web content\n"
            "- 'search for python tutorials' - Search the web\n"
            "- 'hello' - Chat with me\n\n"
            "**Commands:**\n"
            "`!start` - Welcome message\n"
            "`!help` - This help message\n"
            "`!reset` - Reset your conversation session"
        )

        await ctx.send(help_message)

    async def _reset_command(self, ctx):
        """Handle !reset command"""
        user_id = str(ctx.author.id)

        if self.allowed_users and ctx.author.id not in self.allowed_users:
            await ctx.send("Sorry, you are not authorized to use this bot.")
            return

        self.message_handler.session_manager.reset_session(user_id)
        await ctx.send("Your session has been reset.")

    async def start(self):
        """Start the Discord bot"""
        logger.info("Starting Discord bot...")
        self._running = True
        await self.bot.start(self.token)

    async def stop(self):
        """Stop the Discord bot"""
        logger.info("Stopping Discord bot...")
        self._running = False
        await self.bot.close()

    async def send_message(self, message: OutgoingMessage):
        """Send a message via Discord"""
        try:
            channel = await self.bot.fetch_channel(int(message.chat_id))
            await channel.send(message.text)
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}", exc_info=True)

    def run(self):
        """Synchronous run method"""
        logger.info("Starting Discord bot...")
        print("Discord bot is running. Press Ctrl+C to stop.")
        self.bot.run(self.token)
