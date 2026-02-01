"""Base messaging platform interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class IncomingMessage:
    """Represents an incoming message from any platform"""
    user_id: str
    user_name: str
    text: str
    platform: str  # "telegram", "whatsapp", "discord", "slack"
    chat_id: str  # Platform-specific chat/channel ID
    metadata: dict = None  # Platform-specific metadata

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OutgoingMessage:
    """Represents an outgoing message to any platform"""
    chat_id: str
    text: str
    parse_mode: Optional[str] = None  # "markdown", "html", None
    metadata: dict = None  # Platform-specific options

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MessagingPlatform(ABC):
    """Abstract base class for all messaging platforms"""

    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name (e.g., 'telegram', 'whatsapp')"""
        pass

    @abstractmethod
    async def start(self):
        """Start the messaging platform bot"""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the messaging platform bot"""
        pass

    @abstractmethod
    async def send_message(self, message: OutgoingMessage):
        """Send a message to the platform"""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """Check if the platform is currently running"""
        pass
