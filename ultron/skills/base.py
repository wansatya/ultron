"""Base skill interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class SkillResult:
    """Result from skill execution"""
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        if self.success:
            return self.output
        else:
            return f"Error: {self.error}"


class Skill(ABC):
    """
    Base class for Ultron skills

    A skill is a self-contained capability that combines:
    - Intent definition (what triggers it)
    - Entity extraction (what parameters it needs)
    - Execution logic (what it does)
    - Response generation (how it responds)
    """

    @abstractmethod
    def name(self) -> str:
        """
        Unique skill name (e.g., 'weather', 'github_status')

        Returns:
            Skill identifier
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """
        Human-readable description for intent classification

        This is used by the zero-shot classifier to match user messages.
        Be specific and clear.

        Returns:
            Description string (e.g., "Get current weather information")
        """
        pass

    @abstractmethod
    def examples(self) -> List[str]:
        """
        Example messages that should trigger this skill

        Returns:
            List of example user messages
        """
        pass

    @abstractmethod
    def entities(self) -> List[str]:
        """
        Required entity types this skill needs

        Returns:
            List of entity names (e.g., ['location', 'date'])
        """
        pass

    @abstractmethod
    async def execute(self, entities: Dict[str, Any], user_id: str, message: str) -> SkillResult:
        """
        Execute the skill with extracted entities

        Args:
            entities: Extracted parameters from user message
            user_id: User identifier
            message: Original user message

        Returns:
            SkillResult with success status and output
        """
        pass

    def validate_entities(self, entities: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate that required entities are present

        Args:
            entities: Extracted entities to validate

        Returns:
            (is_valid, error_message)
        """
        for entity in self.entities():
            if entity not in entities or not entities[entity]:
                return False, f"Missing required parameter: {entity}"
        return True, None

    def format_response(self, result: SkillResult) -> str:
        """
        Format skill result into user-friendly response

        Override this to customize response formatting.

        Args:
            result: SkillResult from execution

        Returns:
            Formatted response string
        """
        if result.success:
            return result.output
        else:
            return f"Error: {result.error}"

    def metadata(self) -> Dict[str, Any]:
        """
        Optional metadata about the skill

        Returns:
            Dictionary with skill metadata
        """
        return {
            "name": self.name(),
            "description": self.description(),
            "version": "1.0.0",
            "author": "Unknown",
            "requires": []
        }
