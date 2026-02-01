"""
Example Skill: Time and Date Information

This skill provides current time and date information.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any
from ultron.skills.base import Skill, SkillResult


class TimeSkill(Skill):
    """Get current time and date"""

    def name(self) -> str:
        return "time"

    def description(self) -> str:
        return "Get current time and date information"

    def examples(self) -> List[str]:
        return [
            "what time is it",
            "what's the current time",
            "tell me the date",
            "what day is it",
            "current date and time"
        ]

    def entities(self) -> List[str]:
        return []  # No entities required

    async def execute(self, entities: Dict[str, Any], user_id: str, message: str) -> SkillResult:
        """Get current time"""
        try:
            now = datetime.now()
            utc_now = datetime.now(timezone.utc)

            # Format output
            output = f"""Current Time Information:

Local Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}
UTC Time: {utc_now.strftime('%Y-%m-%d %H:%M:%S %Z')}

Day: {now.strftime('%A')}
Date: {now.strftime('%B %d, %Y')}
Week: {now.strftime('Week %W of %Y')}
"""

            return SkillResult(
                success=True,
                output=output.strip(),
                metadata={
                    "timestamp": now.isoformat(),
                    "timezone": str(now.astimezone().tzinfo)
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                output="",
                error=f"Failed to get time: {str(e)}"
            )

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name(),
            "description": self.description(),
            "version": "1.0.0",
            "author": "Ultron Team",
            "requires": []  # No external dependencies
        }
