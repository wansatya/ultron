# Ultron

**Intent-Based Task Automation System**

A lightweight task automation system that uses CPU-based machine learning models to understand natural language commands and execute tasks via **Telegram, Discord, Slack, or WhatsApp**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/wansatya/ultron/main/install.sh | bash
```

Then:
```bash
export TELEGRAM_BOT_TOKEN="your-token-from-botfather"
cd ~/ultron && ./run_ultron.sh
```

---

## Features

- **Multi-Platform Support**: Works with Telegram, Discord, Slack, and WhatsApp simultaneously
- **Dynamic Skills System**: Add new capabilities without modifying core code
- **Natural Language Understanding**: Uses BART-MNLI for zero-shot intent classification
- **Smart Response Generation**: Uses Flan-T5-small for natural responses
- **8 Built-in Tools**: Execute commands, read/write files, fetch web content, search the web
- **Session Management**: Maintains conversation history per user
- **CPU-Friendly**: All models optimized to run on CPU (no GPU required)
- **Extensible**: Easy to add platforms, intents, tools, and skills
- **Async**: Built with asyncio for responsive performance

---

## Quick Start

### 1. Install

```bash
# One-line install
curl -sSL https://raw.githubusercontent.com/wansatya/ultron/main/install.sh | bash
cd ~/ultron

# Or manual
git clone <repo-url>
cd ultron
pip install -r requirements.txt
```

### 2. Setup Telegram (Easiest)

```bash
# Get token from @BotFather on Telegram
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 3. Run

```bash
python -m ultron.main
```

### 4. Chat

Open Telegram, find your bot, send `/start`, then:
```
run ls -la
read config.yaml
what's the weather in London
hello
```

---

## Supported Platforms

| Platform | Status | Setup Time | Best For |
|----------|--------|------------|----------|
| **Telegram** | ✅ | 30 seconds | Personal use |
| **Discord** | ✅ | 2 minutes | Communities |
| **Slack** | ✅ | 5 minutes | Teams |
| **WhatsApp** | ⚠️ | 1 minute | Mobile users |

### Platform Setup

#### Telegram
1. Message [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Copy token
4. `export TELEGRAM_BOT_TOKEN="..."`

#### Discord
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create application → Add bot
3. Copy token
4. Enable "Message Content Intent"
5. `export DISCORD_BOT_TOKEN="..."`
6. `pip install discord.py`

#### Slack
1. Go to [Slack API](https://api.slack.com/apps)
2. Create app → Enable Socket Mode
3. Get Bot Token and App Token
4. `export SLACK_BOT_TOKEN="xoxb-..." SLACK_APP_TOKEN="xapp-..."`
5. `pip install slack-bolt`

#### WhatsApp
1. `pip install webwhatsapi selenium`
2. Run Ultron
3. Scan QR code with phone
4. Done!

### Running Multiple Platforms

Enable in `config.yaml`:
```yaml
platforms:
  telegram: {enabled: true, bot_token: "${TELEGRAM_BOT_TOKEN}"}
  discord: {enabled: true, bot_token: "${DISCORD_BOT_TOKEN}"}
  slack: {enabled: true, bot_token: "${SLACK_BOT_TOKEN}", app_token: "${SLACK_APP_TOKEN}"}
  whatsapp: {enabled: true}
```

All platforms run concurrently, sharing ML models!

---

## Skills System

### What are Skills?

Skills are drop-in plugins that add new capabilities to Ultron.

**Create a skill in 3 steps**:

1. **Create file** `skills/weather.py`:
```python
from ultron.skills.base import Skill, SkillResult
from typing import List, Dict, Any

class WeatherSkill(Skill):
    def name(self) -> str:
        return "weather"

    def description(self) -> str:
        return "Get current weather for a location"

    def examples(self) -> List[str]:
        return ["what's the weather in London", "weather in Paris"]

    def entities(self) -> List[str]:
        return ["location"]

    async def execute(self, entities: Dict[str, Any], user_id: str, message: str) -> SkillResult:
        location = entities.get("location", "London")
        # Your implementation
        return SkillResult(success=True, output=f"Sunny in {location}!")
```

2. **Restart Ultron**: `python -m ultron.main`

3. **Use it**: Message "what's the weather in London" from any platform!

### Example Skills

Copy built-in examples:
```bash
cp skills/examples/*.py skills/
```

Now you can use:
- `what's the weather in London` → Weather info
- `what time is it` → Current time
- `calculate 15 * 37` → Math result (555)

### Creating Custom Skills

See `skills/README.md` for:
- Skill template
- Entity types available
- Best practices
- Advanced features
- Troubleshooting

**Skill Ideas**: GitHub, Jira, AWS, Docker, Database queries, Translations, Reminders, Notes, News, Stocks

---

## Supported Intents

### Built-in Intents

1. **execute_command** - Run shell commands
   - Examples: `run ls`, `execute docker ps`, `check disk space`

2. **read_file** - Read file contents
   - Examples: `read config.yaml`, `show me README.md`

3. **write_file** - Write to files
   - Examples: `write 'text' to file.txt`, `create notes.md`

4. **web_fetch** - Fetch web content
   - Examples: `fetch https://example.com`, `scrape that URL`

5. **web_search** - Search the web
   - Examples: `search for tutorials`, `find docker info`

6. **chat** - General conversation
   - Examples: `hello`, `thanks`, `what can you do`

### Dynamic Intents (Skills)

Add unlimited intents by creating skills:
- Weather, Time, Calculator (examples included)
- GitHub, Jira, AWS (create your own)
- Any capability you can code!

---

## Architecture

### System Flow

```
┌──────────────────────┐
│  Messaging Platform  │
│  (Telegram/Discord/  │
│   Slack/WhatsApp)    │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Message Handler     │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ Intent Classifier    │
│ (BART-MNLI)          │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ Entity Extractor     │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ Tool/Skill Executor  │
│ - Built-in tools     │
│ - Dynamic skills     │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ Response Generator   │
│ (Flan-T5-small)      │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ Session Manager      │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Platform Response   │
└──────────────────────┘
```

### Tech Stack

**ML Models**:
- facebook/bart-large-mnli (406M) - Intent classification
- google/flan-t5-small (77M) - Response generation

**Messaging**:
- python-telegram-bot 20.0+ - Telegram
- discord.py 2.3+ - Discord
- slack-bolt 1.18+ - Slack
- webwhatsapi 2.0+ - WhatsApp

**Core**:
- Python 3.9+
- asyncio
- aiohttp
- PyTorch 2.0+
- Transformers 4.30+

---

## Installation

### System Requirements

- **Python**: 3.9+
- **RAM**: 4GB minimum
- **Disk**: 2GB free
- **OS**: Linux, macOS, Windows

### Install Methods

**Method 1: Automated**
```bash
curl -sSL https://raw.githubusercontent.com/wansatya/ultron/main/install.sh | bash
```

**Method 2: Manual**
```bash
git clone <repo-url>
cd ultron
pip install -r requirements.txt  # Installs all platforms
```

**Method 3: Selective**
```bash
# Minimal (Telegram only)
pip install torch transformers python-telegram-bot pyyaml aiohttp beautifulsoup4

# + Discord
pip install discord.py

# + Slack
pip install slack-bolt

# + WhatsApp
pip install webwhatsapi selenium
```

---

## Configuration

### Basic Config

```yaml
platforms:
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT_TOKEN}"

skills:
  enabled: true
  directory: "./skills"

models:
  intent_classifier:
    device: "cpu"  # or "cuda"
  response_generator:
    device: "cpu"  # or "cuda"
```

### Advanced Config

```yaml
# Restrict users
platforms:
  telegram:
    allowed_users: [123456789]

# Whitelist commands
tools:
  system:
    allowed_commands: ["ls", "pwd", "cat"]

# Enable all platforms
platforms:
  telegram: {enabled: true, bot_token: "${TELEGRAM_BOT_TOKEN}"}
  discord: {enabled: true, bot_token: "${DISCORD_BOT_TOKEN}"}
  slack: {enabled: true, bot_token: "${SLACK_BOT_TOKEN}", app_token: "${SLACK_APP_TOKEN}"}
  whatsapp: {enabled: true}
```

---

## Usage Examples

### Execute Commands
```
User: run ls -la
Bot:  I executed `ls -la`. Output:
      drwxr-xr-x  8 user  256 Feb  1 12:00 .
      -rw-r--r--  1 user 1024 Feb  1 11:00 config.yaml
```

### File Operations
```
User: read config.yaml
Bot:  Here's the content of config.yaml:
      [contents]

User: write 'Hello World' to test.txt
Bot:  Successfully wrote to test.txt
```

### Web Tools
```
User: fetch https://wttr.in/London
Bot:  Weather for London: Sunny ☀️

User: search for python tutorials
Bot:  Search results for 'python tutorials':
      [results from DuckDuckGo]
```

### Skills (if enabled)
```
User: what's the weather in Paris
Bot:  Paris: Partly cloudy, 18°C

User: what time is it
Bot:  Current Time: 2026-02-01 14:30:00

User: calculate 15 * 37
Bot:  Result: 15 * 37 = 555
```

---

## Development

### Project Structure

```
ultron/
├── ultron/               # Core package
│   ├── classifier/      # Intent classification
│   ├── tools/           # Built-in tools
│   ├── generator/       # Response generation
│   ├── messaging/       # Platform integrations
│   ├── session/         # Session management
│   └── skills/          # Skills system
├── skills/              # User skills
│   ├── examples/       # Example skills
│   └── README.md       # Skills guide
├── data/
│   ├── intents.json    # Intent definitions
│   ├── models/         # ML models
│   └── sessions/       # User sessions
└── config.yaml         # Configuration
```

### Creating Skills

```python
# skills/myskill.py
from ultron.skills.base import Skill, SkillResult
from typing import List, Dict, Any

class MySkill(Skill):
    def name(self) -> str:
        return "myskill"

    def description(self) -> str:
        return "Clear description for intent matching"

    def examples(self) -> List[str]:
        return ["example message 1", "example message 2"]

    def entities(self) -> List[str]:
        return ["param1"]

    async def execute(self, entities: Dict[str, Any], user_id: str, message: str) -> SkillResult:
        # Your logic here
        return SkillResult(success=True, output="Done!")
```

Save, restart Ultron, done!

### Adding New Platforms

```python
# ultron/messaging/myplatform_bot.py
from .base import MessagingPlatform, OutgoingMessage

class MyPlatformBot(MessagingPlatform):
    def platform_name(self) -> str:
        return "myplatform"

    async def start(self):
        # Initialize platform

    async def send_message(self, message: OutgoingMessage):
        # Send message
```

Register in `main.py` and add to config.

---

## Platform Setup Guides

### Telegram (30 seconds)

1. Message [@BotFather](https://t.me/botfather)
2. Send `/newbot`, choose name and username
3. Copy token: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
4. `export TELEGRAM_BOT_TOKEN="your-token"`
5. Run: `python -m ultron.main`

### Discord (2 minutes)

1. [Discord Developer Portal](https://discord.com/developers/applications) → New Application
2. Bot tab → Add Bot → Copy token
3. Enable "Message Content Intent" (required!)
4. OAuth2 → URL Generator → Select bot + permissions
5. Invite bot to your server
6. `export DISCORD_BOT_TOKEN="your-token"`
7. `pip install discord.py`
8. Enable in config.yaml

### Slack (5 minutes)

1. [Slack API](https://api.slack.com/apps) → Create App
2. OAuth & Permissions → Add scopes: `chat:write`, `channels:history`, `im:history`, `app_mentions:read`
3. Install to workspace → Copy Bot Token (`xoxb-...`)
4. Socket Mode → Enable → Generate token (`xapp-...`)
5. Event Subscriptions → Subscribe to `message.channels`, `message.im`
6. `export SLACK_BOT_TOKEN="xoxb-..." SLACK_APP_TOKEN="xapp-..."`
7. `pip install slack-bolt`
8. Enable in config.yaml

### WhatsApp (1 minute + QR scan)

1. `pip install webwhatsapi selenium`
2. Enable in config.yaml
3. Run Ultron
4. Scan QR code with phone (WhatsApp → Settings → Linked Devices)
5. Wait for "Logged in successfully!"

**Note**: Experimental, uses unofficial WhatsApp Web API

### Running All Platforms

```yaml
# config.yaml
platforms:
  telegram: {enabled: true, bot_token: "${TELEGRAM_BOT_TOKEN}"}
  discord: {enabled: true, bot_token: "${DISCORD_BOT_TOKEN}"}
  slack: {enabled: true, bot_token: "${SLACK_BOT_TOKEN}", app_token: "${SLACK_APP_TOKEN}"}
  whatsapp: {enabled: true}
```

```bash
# Set all tokens
export TELEGRAM_BOT_TOKEN="..."
export DISCORD_BOT_TOKEN="..."
export SLACK_BOT_TOKEN="..."
export SLACK_APP_TOKEN="..."

# Run
python -m ultron.main
```

Output:
```
Ultron is running with 4 platform(s)
Press Ctrl+C to stop
```

---

## Configuration Reference

### Full config.yaml

```yaml
# Platforms
platforms:
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    allowed_users: []  # Empty = all

  discord:
    enabled: false
    bot_token: "${DISCORD_BOT_TOKEN}"
    allowed_users: []

  slack:
    enabled: false
    bot_token: "${SLACK_BOT_TOKEN}"
    app_token: "${SLACK_APP_TOKEN}"
    allowed_users: []

  whatsapp:
    enabled: false
    profile_path: "./data/whatsapp_session"
    allowed_users: []

# Models
models:
  intent_classifier:
    model_name: "facebook/bart-large-mnli"
    device: "cpu"  # or "cuda"

  response_generator:
    model_name: "google/flan-t5-small"
    device: "cpu"  # or "cuda"
    max_length: 256

# Tools
tools:
  system:
    enabled: true
    allowed_commands: []  # Empty = all

  web:
    enabled: true
    timeout: 10

# Skills
skills:
  enabled: true
  directory: "./skills"

# Sessions
sessions:
  storage_path: "./data/sessions"
  max_history: 50
```

---

## Built-in Tools

| Tool | Function | Example |
|------|----------|---------|
| system.exec | Execute shell commands | `run ls -la` |
| system.read | Read file contents | `read config.yaml` |
| system.write | Write to files | `write 'hi' to test.txt` |
| system.glob | Find files by pattern | `find *.py files` |
| system.grep | Search in files | `search for TODO` |
| web.fetch | Fetch URL content | `fetch https://example.com` |
| web.search | Web search (DuckDuckGo) | `search for python` |
| response.generate | Chat responses | `hello` |

---

## Example Skills Included

Copy to use:
```bash
cp skills/examples/*.py skills/
```

### 1. Weather Skill
```
User: what's the weather in London
Bot:  London: Partly cloudy ⛅
```

### 2. Time Skill
```
User: what time is it
Bot:  Current Time: 2026-02-01 14:30:00 UTC
      Day: Saturday
      Date: February 01, 2026
```

### 3. Calculator Skill
```
User: calculate 15 * 37
Bot:  Result: 15 * 37 = 555

User: what is 2^8
Bot:  Result: 2**8 = 256
```

---

## Performance

### Latency (CPU)

- **First message**: 5-10s (model loading)
- **Subsequent**: 2-3s per message
- **With GPU**: ~500ms per message

### Resource Usage

- **RAM**: ~2GB (models) + ~50MB per platform
- **Disk**: ~1.5GB (downloaded models)
- **CPU**: Moderate during inference

### Multi-Platform Impact

Running 4 platforms vs 1:
- **Memory**: +200MB total (models shared)
- **CPU**: Negligible (async)
- **Latency**: No impact

---

## Security

### Default Settings

- All commands allowed
- All users allowed
- Full filesystem access
- Sessions stored as plain JSON

### Hardening

```yaml
# Restrict users
platforms:
  telegram:
    allowed_users: [123456789]

# Whitelist commands
tools:
  system:
    allowed_commands: ["ls", "pwd", "cat", "date"]

# Disable risky tools
tools:
  system:
    enabled: false  # No command execution
```

### Best Practices

1. Use `allowed_users` to restrict access
2. Whitelist commands for production
3. Run in Docker container
4. Don't store secrets in sessions
5. Monitor logs for abuse

---

## Troubleshooting

### Installation

**Problem**: `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

**Problem**: Torch install fails
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Configuration

**Problem**: "Token not set"
```bash
echo $TELEGRAM_BOT_TOKEN  # Should show token
export TELEGRAM_BOT_TOKEN="your-token"
```

### Runtime

**Problem**: Bot not responding
- Check bot is running
- Check token is valid
- Check logs: `tail -f ultron.log`
- Send `/start` to initialize

**Problem**: Slow responses
- First message: 5-10s (normal)
- Later: 2-3s (normal on CPU)
- Use GPU for faster: Set `device: "cuda"` in config

### Platform-Specific

**Discord** - Enable "Message Content Intent" in Developer Portal
**Slack** - Use Socket Mode (app token required)
**WhatsApp** - Install Chrome/Chromium browser

### Skills

**Skill not loading**:
- Check syntax: `python3 -m py_compile skills/myskill.py`
- Check class inherits from `Skill`
- Check file is in `skills/` directory
- Check logs: `grep "skill" ultron.log`

**Skill not triggering**:
- Make description clear and specific
- Add more examples
- Test with exact example message
- Check classification confidence in logs

---

## Testing

### Test Components

```bash
# All components
python test_components.py

# Individual modules
python -m ultron.classifier.intent_classifier
python -m ultron.generator.response
python -m ultron.session.manager
```

### Test Platforms

1. Start with Telegram only
2. Verify it works
3. Add Discord, test again
4. Add Slack, test again
5. Add WhatsApp last

### Test Skills

```bash
# Copy examples
cp skills/examples/*.py skills/

# Restart
python -m ultron.main

# Should see:
# "Loading skills..."
# "Loaded skill: weather from ./skills/weather_skill.py"
# "3 skill(s) loaded and registered"

# Test from any platform:
# "what's the weather in London"
# "what time is it"
# "calculate 2 + 2"
```

---

## Deployment

### Systemd Service (Linux)

```ini
[Unit]
Description=Ultron Multi-Platform Bot
After=network.target

[Service]
Type=simple
User=ultron
WorkingDirectory=/opt/ultron
Environment="TELEGRAM_BOT_TOKEN=..."
Environment="DISCORD_BOT_TOKEN=..."
ExecStart=/usr/bin/python3 -m ultron.main
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker (Future)

Coming in v0.3.0

---

## Roadmap

**Completed** ✅:
- Multi-platform support (4 platforms)
- Skills system (dynamic loading)
- Async concurrent execution
- Enhanced entity extraction

**Planned** 📋:
- Fine-tuned classifier
- Multi-turn conversations
- Docker sandboxing
- Voice interface
- Web UI
- Workflow automation
- Scheduled tasks
- API integrations (GitHub, Jira, AWS)

---

## Statistics

- **Python Modules**: 27
- **Lines of Code**: ~2,500
- **Platforms**: 4
- **Built-in Tools**: 8
- **Example Skills**: 3
- **ML Models**: 2
- **Model Size**: ~1.5GB

---

## FAQ

**Q: Can I run multiple platforms?**
A: Yes! Enable all platforms in config.yaml and set tokens.

**Q: Do skills work on all platforms?**
A: Yes! Skills work identically on all platforms.

**Q: Can I create my own skills?**
A: Yes! Drop a Python file in `skills/` directory and restart.

**Q: Do I need GPU?**
A: No. CPU works fine (2-3s latency). GPU is optional for speed.

**Q: Is WhatsApp reliable?**
A: Experimental. Uses unofficial API. May break with WhatsApp updates.

**Q: Can I restrict who uses the bot?**
A: Yes. Set `allowed_users` per platform in config.

**Q: Do sessions persist across platforms?**
A: Sessions are per-user per-platform. Same user on different platforms = different sessions.

---

## Contributing

Contributions welcome!

**Ideas**:
- New skills (GitHub, Jira, AWS, etc.)
- New platforms (Matrix, iMessage, etc.)
- Improved entity extraction
- Documentation
- Bug fixes

**How to contribute**:
1. Fork repo
2. Create feature branch
3. Add your changes
4. Test thoroughly
5. Submit PR

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Credits

Built with:
- [Transformers](https://huggingface.co/transformers) by HuggingFace
- [python-telegram-bot](https://python-telegram-bot.org/)
- [discord.py](https://discordpy.readthedocs.io/)
- [slack-bolt](https://slack.dev/bolt-python/)
- [PyTorch](https://pytorch.org/) by Meta AI

---

## Support

**Documentation**:
- This README - Complete guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
- `skills/README.md` - Skills development

**Help**:
- Logs: `tail -f ultron.log`
- Tests: `python test_components.py`
- Sessions: `cat data/sessions/<user_id>.json`

**Useful Commands**:
```bash
# View logs
tail -f ultron.log

# Test everything
python test_components.py

# Check skills
ls -la skills/

# Reset all sessions
rm -rf data/sessions/*
```

---

## Quick Command Reference

### Bot Commands (All Platforms)

- `/start` or `!start` - Initialize and show welcome
- `/help` or `!help` - Show usage examples
- `/reset` or `!reset` - Clear conversation history

### Skill Management

```bash
# List skills
ls skills/*.py

# Add skill
cp myskill.py skills/

# Remove skill
rm skills/myskill.py

# Reload (restart required currently)
python -m ultron.main
```

### Platform Management

```bash
# Check which platforms are enabled
grep "enabled: true" config.yaml

# View platform status
tail -f ultron.log | grep "bot"

# Disable platform
# Edit config.yaml: enabled: false
```

---

**Ultron v0.2.0** - Multi-platform task automation with unlimited extensibility!

Made with ⚡ by the Ultron team
