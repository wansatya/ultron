"""Base tool interface and data structures"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class ToolContext:
    """Context information for tool execution"""
    user_id: str
    session_key: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    output: str
    error: str | None = None
    metadata: Dict[str, Any] | None = None

    def __str__(self) -> str:
        if self.success:
            return self.output
        else:
            return f"Error: {self.error}"


class Tool(ABC):
    """Abstract base class for all tools"""

    @abstractmethod
    def name(self) -> str:
        """Return the tool name (e.g., 'system.exec')"""
        pass

    @abstractmethod
    def description(self) -> str:
        """Return a brief description of what the tool does"""
        pass

    @abstractmethod
    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """
        Execute the tool with given parameters

        Args:
            params: Parameters extracted from user message
            context: Execution context (user, session, etc.)

        Returns:
            ToolResult with success status and output
        """
        pass

    def validate_params(self, params: Dict[str, Any], required: List[str]) -> Tuple[bool, str | None]:
        """
        Validate that required parameters are present

        Args:
            params: Parameters to validate
            required: List of required parameter names

        Returns:
            Tuple of (is_valid, error_message)
        """
        for param in required:
            if param not in params or not params[param]:
                return False, f"Missing required parameter: {param}"
        return True, None
