"""Response generation tool for chat intent"""

from typing import Dict, Any
from .base import Tool, ToolContext, ToolResult


class GenerateResponseTool(Tool):
    """Generate a response for chat/conversation intent"""

    def __init__(self, response_generator=None):
        self._response_generator = response_generator

    def name(self) -> str:
        return "response.generate"

    def description(self) -> str:
        return "Generate a conversational response"

    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Generate a conversational response"""
        # For chat intent, just return success with the message
        # The response generator will handle creating the actual response
        return ToolResult(
            success=True,
            output=context.message,
            metadata={"intent": "chat"}
        )
