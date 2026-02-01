"""
Example Skill: Calculator

This skill performs mathematical calculations.
"""

import re
from typing import List, Dict, Any
from ultron.skills.base import Skill, SkillResult


class CalculatorSkill(Skill):
    """Perform mathematical calculations"""

    def name(self) -> str:
        return "calculator"

    def description(self) -> str:
        return "Perform mathematical calculations and evaluate expressions"

    def examples(self) -> List[str]:
        return [
            "calculate 2 + 2",
            "what is 15 * 37",
            "compute 100 / 5",
            "evaluate 2^8",
            "what's the square root of 144"
        ]

    def entities(self) -> List[str]:
        return ["expression"]

    async def execute(self, entities: Dict[str, Any], user_id: str, message: str) -> SkillResult:
        """Evaluate mathematical expression"""
        # Extract expression from message if not in entities
        expression = entities.get("expression", "")

        if not expression:
            # Try to extract from message
            expression = self._extract_expression(message)

        if not expression:
            return SkillResult(
                success=False,
                output="",
                error="No mathematical expression found"
            )

        try:
            # Clean and prepare expression
            expression = expression.replace("^", "**")  # Handle power notation
            expression = expression.replace("x", "*")   # Handle multiplication

            # Evaluate safely (only allow math operations)
            allowed_names = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
            }

            # Eval with restricted namespace
            result = eval(expression, {"__builtins__": {}}, allowed_names)

            output = f"Result: {expression} = {result}"

            return SkillResult(
                success=True,
                output=output,
                metadata={"expression": expression, "result": result}
            )

        except Exception as e:
            return SkillResult(
                success=False,
                output="",
                error=f"Failed to evaluate expression: {str(e)}"
            )

    def _extract_expression(self, message: str) -> str:
        """Extract mathematical expression from message"""
        # Remove common trigger words
        cleaned = re.sub(
            r"^(calculate|compute|evaluate|what is|what's|whats)\s+",
            "",
            message,
            flags=re.IGNORECASE
        )

        # Extract numbers and operators
        # Match: numbers, operators, parentheses, spaces
        match = re.search(r'[\d\s+\-*/()^.]+', cleaned)
        if match:
            return match.group(0).strip()

        return ""

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name(),
            "description": self.description(),
            "version": "1.0.0",
            "author": "Ultron Team",
            "requires": []
        }
