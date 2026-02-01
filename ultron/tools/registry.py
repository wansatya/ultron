"""Tool registry for managing available tools"""

from typing import Dict, Optional
from .base import Tool


class ToolRegistry:
    """Registry for managing and looking up tools"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool"""
        self._tools[tool.name()] = tool
        print(f"Registered tool: {tool.name()}")

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, str]:
        """List all registered tools"""
        return {name: tool.description() for name, tool in self._tools.items()}

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered"""
        return name in self._tools


# Global registry instance
_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """Get or create global registry instance"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def register_tool(tool: Tool):
    """Register a tool in the global registry"""
    get_registry().register(tool)


def get_tool(name: str) -> Optional[Tool]:
    """Get a tool from the global registry"""
    return get_registry().get(name)
