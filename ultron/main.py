"""Main entry point for Ultron"""

import logging
import sys
import asyncio
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ultron.config import get_config
from ultron.classifier.intent_classifier import IntentClassifier
from ultron.classifier.entity_extractor import EntityExtractor
from ultron.generator.response import ResponseGenerator
from ultron.session.manager import SessionManager
from ultron.messaging.handler import MessageHandler
from ultron.messaging.base import MessagingPlatform
from ultron.messaging.telegram_bot import TelegramBot
from ultron.tools.registry import register_tool
from ultron.tools.system import ExecTool, ReadFileTool, WriteFileTool, GlobTool, GrepTool
from ultron.tools.web import WebFetchTool, WebSearchTool
from ultron.tools.response import GenerateResponseTool
from ultron.skills.loader import get_skill_loader
from ultron.skills.adapter import skill_to_tool

# Optional platform imports
try:
    from ultron.messaging.discord_bot import DiscordBot
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

try:
    from ultron.messaging.slack_bot import SlackBot
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

try:
    from ultron.messaging.whatsapp_bot import WhatsAppBot
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ultron.log')
        ]
    )


def register_tools(config):
    """Register all available tools"""
    print("\nRegistering tools...")

    # System tools
    if config.get("tools.system.enabled", True):
        sandbox = config.get("tools.system.sandbox", False)
        allowed_commands = config.get("tools.system.allowed_commands", [])

        register_tool(ExecTool(sandbox=sandbox, allowed_commands=allowed_commands))
        register_tool(ReadFileTool())
        register_tool(WriteFileTool())
        register_tool(GlobTool())
        register_tool(GrepTool())

    # Web tools
    if config.get("tools.web.enabled", True):
        timeout = config.get("tools.web.timeout", 10)
        user_agent = config.get("tools.web.user_agent", "Ultron/1.0")

        register_tool(WebFetchTool(timeout=timeout, user_agent=user_agent))
        register_tool(WebSearchTool(timeout=timeout))

    # Response generator tool (for chat intent)
    register_tool(GenerateResponseTool())

    print("Tools registered successfully\n")


def load_skills(config, intent_classifier):
    """Load and register all skills"""
    skills_enabled = config.get("skills.enabled", True)
    if not skills_enabled:
        print("Skills system disabled\n")
        return 0

    print("Loading skills...")

    skills_dir = config.get("skills.directory", "./skills")
    skill_loader = get_skill_loader(skills_dir)

    # Discover and load skills
    count = skill_loader.load_all_skills()

    if count == 0:
        print("No skills found\n")
        return 0

    # Register each skill as a tool and add to intent classifier
    for skill in skill_loader.get_all_skills():
        # Convert skill to tool
        tool = skill_to_tool(skill)
        register_tool(tool)

        # Add skill as an intent
        intent_classifier.add_skill_intent(
            skill_name=skill.name(),
            description=skill.description(),
            tool_name=tool.name(),
            entities=skill.entities()
        )

    print(f"{count} skill(s) loaded and registered\n")
    return count


def initialize_platforms(config, message_handler) -> List[MessagingPlatform]:
    """Initialize enabled messaging platforms"""
    platforms = []

    # Telegram
    if config.get("platforms.telegram.enabled", True):
        bot_token = config.get("platforms.telegram.bot_token")
        if bot_token and not bot_token.startswith("${"):
            print("Initializing Telegram bot...")
            allowed_users = config.get("platforms.telegram.allowed_users", [])
            platforms.append(TelegramBot(
                token=bot_token,
                message_handler=message_handler,
                allowed_users=allowed_users
            ))
        else:
            print("⚠ Telegram enabled but token not set (skipping)")

    # Discord
    if config.get("platforms.discord.enabled", False):
        if not DISCORD_AVAILABLE:
            print("⚠ Discord enabled but discord.py not installed (skipping)")
            print("  Install with: pip install discord.py")
        else:
            bot_token = config.get("platforms.discord.bot_token")
            if bot_token and not bot_token.startswith("${"):
                print("Initializing Discord bot...")
                allowed_users = config.get("platforms.discord.allowed_users", [])
                platforms.append(DiscordBot(
                    token=bot_token,
                    message_handler=message_handler,
                    allowed_users=allowed_users
                ))
            else:
                print("⚠ Discord enabled but token not set (skipping)")

    # Slack
    if config.get("platforms.slack.enabled", False):
        if not SLACK_AVAILABLE:
            print("⚠ Slack enabled but slack-bolt not installed (skipping)")
            print("  Install with: pip install slack-bolt")
        else:
            bot_token = config.get("platforms.slack.bot_token")
            app_token = config.get("platforms.slack.app_token")
            if bot_token and app_token and not bot_token.startswith("${"):
                print("Initializing Slack bot...")
                allowed_users = config.get("platforms.slack.allowed_users", [])
                platforms.append(SlackBot(
                    bot_token=bot_token,
                    app_token=app_token,
                    message_handler=message_handler,
                    allowed_users=allowed_users
                ))
            else:
                print("⚠ Slack enabled but tokens not set (skipping)")

    # WhatsApp
    if config.get("platforms.whatsapp.enabled", False):
        if not WHATSAPP_AVAILABLE:
            print("⚠ WhatsApp enabled but webwhatsapi not installed (skipping)")
            print("  Install with: pip install webwhatsapi selenium")
        else:
            print("Initializing WhatsApp bot...")
            profile_path = config.get("platforms.whatsapp.profile_path", "./data/whatsapp_session")
            allowed_users = config.get("platforms.whatsapp.allowed_users", [])
            platforms.append(WhatsAppBot(
                profile_path=profile_path,
                message_handler=message_handler,
                allowed_users=allowed_users
            ))

    return platforms


async def run_platforms(platforms: List[MessagingPlatform]):
    """Run multiple platforms concurrently"""
    tasks = []

    for platform in platforms:
        print(f"Starting {platform.platform_name()} bot...")
        task = asyncio.create_task(platform.start())
        tasks.append(task)

    print("\n" + "=" * 60)
    print(f"Ultron is running with {len(platforms)} platform(s)")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    # Wait for all platforms
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        for platform in platforms:
            await platform.stop()


def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)

    print("=" * 60)
    print("ULTRON - Intent-Based Task Automation System")
    print("=" * 60)
    print()

    try:
        # Load configuration
        print("Loading configuration...")
        config = get_config("config.yaml")
        print("Configuration loaded\n")

        # Register tools
        register_tools(config)

        # Initialize components
        print("Initializing components...")

        # Intent classifier
        classifier_model = config.get("models.intent_classifier.model_name", "facebook/bart-large-mnli")
        classifier_device = config.get("models.intent_classifier.device", "cpu")
        intent_classifier = IntentClassifier(
            intents_path="data/intents.json",
            device=classifier_device
        )

        # Entity extractor
        entity_extractor = EntityExtractor()

        # Load skills (must be after intent classifier is initialized)
        load_skills(config, intent_classifier)

        # Response generator
        generator_model = config.get("models.response_generator.model_name", "google/flan-t5-small")
        generator_device = config.get("models.response_generator.device", "cpu")
        generator_max_length = config.get("models.response_generator.max_length", 256)
        response_generator = ResponseGenerator(
            model_name=generator_model,
            device=generator_device,
            max_length=generator_max_length
        )

        # Session manager
        sessions_path = config.get("sessions.storage_path", "./data/sessions")
        max_history = config.get("sessions.max_history", 50)
        session_manager = SessionManager(
            storage_path=sessions_path,
            max_history=max_history
        )

        # Message handler
        message_handler = MessageHandler(
            intent_classifier=intent_classifier,
            entity_extractor=entity_extractor,
            response_generator=response_generator,
            session_manager=session_manager
        )

        print("Components initialized successfully\n")

        # Initialize platforms
        print("Initializing messaging platforms...\n")
        platforms = initialize_platforms(config, message_handler)

        if not platforms:
            print("⚠ No messaging platforms enabled!")
            print("Please enable at least one platform in config.yaml")
            sys.exit(1)

        print(f"\n{len(platforms)} platform(s) initialized\n")

        # Check if we should run async or sync
        if len(platforms) == 1 and platforms[0].platform_name() == "telegram":
            # Single Telegram bot - use legacy sync mode
            platforms[0].run()
        else:
            # Multiple platforms or non-Telegram - use async mode
            asyncio.run(run_platforms(platforms))

    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        logger.info("Received keyboard interrupt, shutting down")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
