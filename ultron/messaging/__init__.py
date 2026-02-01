"""Messaging package"""

from .base import MessagingPlatform, IncomingMessage, OutgoingMessage
from .handler import MessageHandler
from .telegram_bot import TelegramBot

# Optional imports
try:
    from .discord_bot import DiscordBot
except ImportError:
    DiscordBot = None

try:
    from .slack_bot import SlackBot
except ImportError:
    SlackBot = None

try:
    from .whatsapp_bot import WhatsAppBot
except ImportError:
    WhatsAppBot = None

__all__ = [
    "MessagingPlatform",
    "IncomingMessage",
    "OutgoingMessage",
    "MessageHandler",
    "TelegramBot",
    "DiscordBot",
    "SlackBot",
    "WhatsAppBot",
]
