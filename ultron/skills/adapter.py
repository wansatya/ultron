"""Adapter to convert Skills to Tools"""

import logging
from typing import Dict, Any
from .base import Skill
from ..tools.base import Tool, ToolContext, ToolResult

logger = logging.getLogger(__name__)


class SkillToolAdapter(Tool):
    """
    Adapter that wraps a Skill to make it compatible with the Tool interface

    This allows skills to be registered in the tool registry and executed
    through the standard tool execution pipeline.
    """

    def __init__(self, skill: Skill):
        self.skill = skill

    def name(self) -> str:
        """Return skill name as tool name"""
        return f"skill.{self.skill.name()}"

    def description(self) -> str:
        """Return skill description"""
        return self.skill.description()

    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """
        Execute the skill

        Args:
            params: Extracted entities
            context: Tool execution context

        Returns:
            ToolResult from skill execution
        """
        try:
            # Execute skill
            result = await self.skill.execute(
                entities=params,
                user_id=context.user_id,
                message=context.message
            )

            # Convert SkillResult to ToolResult
            return ToolResult(
                success=result.success,
                output=result.output,
                error=result.error,
                metadata=result.metadata
            )

        except Exception as e:
            logger.error(f"Error executing skill {self.skill.name()}: {e}", exc_info=True)
            return ToolResult(
                success=False,
                output="",
                error=f"Skill execution failed: {str(e)}"
            )


def skill_to_tool(skill: Skill) -> SkillToolAdapter:
    """
    Convert a Skill to a Tool

    Args:
        skill: Skill instance

    Returns:
        SkillToolAdapter wrapping the skill
    """
    return SkillToolAdapter(skill)
