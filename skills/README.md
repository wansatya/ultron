# Ultron Skills

This directory contains custom skills for Ultron. Skills are plugin-like modules that add new capabilities without modifying core code.

## What is a Skill?

A skill is a self-contained module that defines:
- **Intent**: What user messages trigger it
- **Entities**: What parameters it needs
- **Execution**: What it does
- **Response**: How it responds

## Creating a Skill

### Method 1: Single File Skill

Create a Python file in this directory (e.g., `weather.py`):

```python
from ultron.skills.base import Skill, SkillResult
from typing import List, Dict, Any

class WeatherSkill(Skill):
    def name(self) -> str:
        return "weather"

    def description(self) -> str:
        return "Get current weather for a location"

    def examples(self) -> List[str]:
        return [
            "what's the weather in London",
            "weather in Paris",
            "is it raining in Tokyo"
        ]

    def entities(self) -> List[str]:
        return ["location"]

    async def execute(self, entities: Dict[str, Any], user_id: str, message: str) -> SkillResult:
        location = entities.get("location", "London")

        # Your implementation here
        weather_data = await fetch_weather(location)

        return SkillResult(
            success=True,
            output=f"Weather in {location}: {weather_data}"
        )
```

### Method 2: Directory-Based Skill

Create a directory with `skill.py`:

```
skills/
└── myskill/
    ├── skill.py       # Main skill class
    ├── utils.py       # Helper functions
    └── config.json    # Skill configuration
```

In `skill.py`:
```python
from ultron.skills.base import Skill, SkillResult
# ... implement as above
```

## Skill Requirements

### Required Methods

1. **name()** - Unique identifier
2. **description()** - For intent classification
3. **examples()** - Example trigger messages
4. **entities()** - Required parameters
5. **execute()** - Main logic

### Optional Methods

- **validate_entities()** - Custom validation (default provided)
- **format_response()** - Custom response formatting
- **metadata()** - Skill information

## Entity Types

Your skill can request these entity types:

- `command` - Shell command
- `file_path` - File path
- `content` - Text content
- `url` - Web URL
- `query` - Search query
- `location` - Place name
- `expression` - Math expression

Custom entity types will return empty string (implement custom extraction if needed).

## Example Skills

Check the `examples/` directory for:
- `weather_skill.py` - Fetch weather data
- `time_skill.py` - Get current time
- `calculator_skill.py` - Math calculations

## Testing Your Skill

### 1. Create the skill file

```bash
nano skills/myskill.py
```

### 2. Restart Ultron

```bash
python -m ultron.main
```

You should see:
```
Loading skills...
Loaded skill: myskill from ./skills/myskill.py
Registered tool: skill.myskill
1 skill(s) loaded and registered
```

### 3. Test via messaging platform

Send a message that matches your skill's description:
```
User: [message matching your skill]
Bot: [your skill's response]
```

### 4. Check logs

```bash
tail -f ultron.log | grep myskill
```

## Skill Lifecycle

1. **Discovery**: Ultron scans `skills/` directory
2. **Loading**: Python file is imported
3. **Registration**: Skill is registered as both:
   - A tool (for execution)
   - An intent (for classification)
4. **Execution**: When matched, skill.execute() is called
5. **Response**: Result is sent back to user

## Advanced Features

### Access Skill Loader

```python
from ultron.skills.loader import get_skill_loader

loader = get_skill_loader()
loader.reload_skill("weather")  # Hot-reload a skill
```

### Skill Dependencies

Specify in metadata():
```python
def metadata(self) -> Dict[str, Any]:
    return {
        "name": self.name(),
        "requires": ["aiohttp", "beautifulsoup4"]
    }
```

### Custom Entity Extraction

Override extraction in your skill:
```python
async def execute(self, entities: Dict[str, Any], user_id: str, message: str) -> SkillResult:
    # Extract custom entity from raw message
    custom_param = self._extract_custom(message)

    # Your logic here
    ...
```

## Best Practices

1. **Single Responsibility**: One skill = one capability
2. **Clear Description**: Used for intent matching
3. **Good Examples**: Helps with classification
4. **Error Handling**: Always return SkillResult
5. **Async**: Use `async def execute()` for I/O operations
6. **Validation**: Validate entities before use
7. **Logging**: Use logger for debugging

## Troubleshooting

### Skill not loading

Check logs:
```bash
grep "Loading skill" ultron.log
```

Ensure:
- File has a class that inherits from `Skill`
- Class is not named exactly `Skill`
- File is in `skills/` directory
- Python syntax is valid

### Skill not triggering

- Check description is clear and specific
- Add more examples
- Test with exact example messages first
- Check logs for classification results

### Skill errors

Check execution errors:
```bash
grep "skill.*error" ultron.log -i
```

Add debug logging:
```python
async def execute(self, entities, user_id, message):
    logger = logging.getLogger(__name__)
    logger.info(f"Executing {self.name()} with {entities}")
    # ...
```

## Sharing Skills

To share a skill:

1. Package it as a single file or directory
2. Include requirements in metadata()
3. Add documentation as docstring
4. Share the file

Others can use it by:
```bash
# Copy to their skills directory
cp myskill.py ~/ultron/skills/

# Restart Ultron
python -m ultron.main
```

## Disabling Skills

In `config.yaml`:
```yaml
skills:
  enabled: false
```

## Examples of Skill Ideas

- **GitHub**: Check repo status, create issues
- **Jira**: Query tickets, update status
- **AWS**: Check EC2 instances, S3 buckets
- **Docker**: List containers, check logs
- **Database**: Run queries, check connections
- **Monitoring**: Check service health
- **Notifications**: Send alerts
- **Reminders**: Set and manage reminders
- **Translation**: Translate text
- **Image**: Generate or edit images

The possibilities are endless!

## Skill Template

```python
"""
Skill: [Name]
Description: [What it does]
"""

from ultron.skills.base import Skill, SkillResult
from typing import List, Dict, Any

class MySkill(Skill):
    def name(self) -> str:
        return "myskill"

    def description(self) -> str:
        return "Clear description for intent matching"

    def examples(self) -> List[str]:
        return [
            "example message 1",
            "example message 2",
        ]

    def entities(self) -> List[str]:
        return ["entity1", "entity2"]

    async def execute(self, entities: Dict[str, Any], user_id: str, message: str) -> SkillResult:
        # Validate
        valid, error = self.validate_entities(entities)
        if not valid:
            return SkillResult(success=False, output="", error=error)

        # Extract parameters
        param1 = entities["entity1"]

        try:
            # Your logic here
            result = do_something(param1)

            return SkillResult(
                success=True,
                output=f"Done: {result}"
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output="",
                error=str(e)
            )
```

Save, restart Ultron, and your skill is live!
