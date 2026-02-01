"""
Example Skill: Weather Information

This skill fetches weather information for a given location.
"""

import aiohttp
from typing import List, Dict, Any
from ultron.skills.base import Skill, SkillResult


class WeatherSkill(Skill):
    """Get current weather for a location"""

    def name(self) -> str:
        return "weather"

    def description(self) -> str:
        return "Get current weather information for a location"

    def examples(self) -> List[str]:
        return [
            "what's the weather in London",
            "weather in New York",
            "how's the weather in Tokyo",
            "check weather for Paris",
            "is it raining in Seattle"
        ]

    def entities(self) -> List[str]:
        return ["location"]

    async def execute(self, entities: Dict[str, Any], user_id: str, message: str) -> SkillResult:
        """Fetch weather information"""
        # Validate entities
        valid, error = self.validate_entities(entities)
        if not valid:
            return SkillResult(success=False, output="", error=error)

        location = entities.get("location", "London")

        try:
            # Use wttr.in API for weather
            url = f"https://wttr.in/{location}?format=3"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        weather = await response.text()
                        return SkillResult(
                            success=True,
                            output=weather.strip(),
                            metadata={"location": location, "source": "wttr.in"}
                        )
                    else:
                        return SkillResult(
                            success=False,
                            output="",
                            error=f"Weather API returned status {response.status}"
                        )

        except Exception as e:
            return SkillResult(
                success=False,
                output="",
                error=f"Failed to fetch weather: {str(e)}"
            )

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name(),
            "description": self.description(),
            "version": "1.0.0",
            "author": "Ultron Team",
            "requires": ["aiohttp"]
        }
