"""Entity extraction from user messages"""

import re
from typing import Dict, Any, List
from urllib.parse import urlparse


class EntityExtractor:
    """Extract entities (parameters) from user messages"""

    def extract(self, message: str, entity_types: List[str]) -> Dict[str, Any]:
        """
        Extract entities from message based on expected entity types

        Args:
            message: User message
            entity_types: List of entity types to extract (e.g., ['command', 'file_path'])

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        for entity_type in entity_types:
            if entity_type == "command":
                entities["command"] = self._extract_command(message)
            elif entity_type == "file_path":
                entities["file_path"] = self._extract_file_path(message)
            elif entity_type == "content":
                entities["content"] = self._extract_content(message)
            elif entity_type == "url":
                entities["url"] = self._extract_url(message)
            elif entity_type == "query":
                entities["query"] = self._extract_query(message)
            elif entity_type == "location":
                entities["location"] = self._extract_location(message)
            elif entity_type == "expression":
                entities["expression"] = self._extract_expression(message)

        return entities

    def _extract_command(self, message: str) -> str:
        """Extract shell command from message"""
        # Patterns: "run X", "execute X", "X" (just the command)
        patterns = [
            r"(?:run|execute)\s+(.+)",
            r"^(.+)$"  # Fallback: entire message
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                cmd = match.group(1).strip()
                # Remove quotes if present
                cmd = cmd.strip("'\"")
                return cmd

        return message

    def _extract_file_path(self, message: str) -> str:
        """Extract file path from message"""
        # Patterns: absolute paths, relative paths, filenames
        patterns = [
            r"(/[^\s]+)",  # Absolute path
            r"(\./[^\s]+)",  # Relative path
            r"([~]/[^\s]+)",  # Home relative
            r"(\w+\.\w+)",  # Filename with extension
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip("'\"")

        # Fallback: look for common file indicators
        words = message.split()
        for i, word in enumerate(words):
            if word.lower() in ["file", "to", "called"]:
                if i + 1 < len(words):
                    return words[i + 1].strip("'\"")

        # Last resort: return last word
        if words:
            return words[-1].strip("'\"")

        return ""

    def _extract_content(self, message: str) -> str:
        """Extract content to write from message"""
        # Patterns: "write 'content' to file", "content" in quotes
        patterns = [
            r"write\s+['\"](.+?)['\"]\s+to",
            r"['\"](.+?)['\"]",
            r"write\s+(.+?)\s+to",
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)

        # Fallback: extract content between first and last word
        words = message.split()
        if len(words) > 3:
            # Remove command words
            content_words = [w for w in words if w.lower() not in ["write", "save", "create", "to", "file", "called"]]
            return " ".join(content_words)

        return ""

    def _extract_url(self, message: str) -> str:
        """Extract URL from message"""
        # Pattern: URL format
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, message)
        if match:
            return match.group(0).strip("'\"")

        # Check for domain names without protocol
        domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
        match = re.search(domain_pattern, message)
        if match:
            domain = match.group(0)
            # Add https:// prefix
            return f"https://{domain}"

        return ""

    def _extract_query(self, message: str) -> str:
        """Extract search query from message"""
        # Remove common search trigger words
        query = re.sub(
            r"^(search|google|find|look up|lookup)\s+(for\s+)?",
            "",
            message,
            flags=re.IGNORECASE
        )

        # Remove quotes
        query = query.strip("'\"")

        return query if query else message

    def _extract_location(self, message: str) -> str:
        """Extract location from message"""
        # Remove common weather/location trigger words
        location = re.sub(
            r"^(weather|what's the weather|whats the weather|how's the weather)\s+(in|for|at)?\s*",
            "",
            message,
            flags=re.IGNORECASE
        )

        # Remove quotes
        location = location.strip("'\"")

        # Common patterns: "in London", "for Paris"
        in_pattern = r'\b(?:in|for|at)\s+([A-Z][a-zA-Z\s]+?)(?:\s|$|\?|!|,)'
        match = re.search(in_pattern, message)
        if match:
            return match.group(1).strip()

        # Fallback: capitalize words (likely location)
        words = location.split()
        if words and words[0][0].isupper():
            # Take capitalized words as location
            location_words = []
            for word in words:
                if word[0].isupper() or word.lower() in ['the', 'of', 'and']:
                    location_words.append(word)
                else:
                    break
            if location_words:
                return " ".join(location_words)

        return location if location else "London"  # Default

    def _extract_expression(self, message: str) -> str:
        """Extract mathematical expression from message"""
        # Remove common calculation trigger words
        cleaned = re.sub(
            r"^(calculate|compute|evaluate|what is|what's|whats)\s+",
            "",
            message,
            flags=re.IGNORECASE
        )

        # Extract numbers and operators
        match = re.search(r'[\d\s+\-*/()^.]+', cleaned)
        if match:
            return match.group(0).strip()

        return ""


if __name__ == "__main__":
    # Test the entity extractor
    extractor = EntityExtractor()

    tests = [
        ("run ls -la", ["command"]),
        ("read /etc/hosts", ["file_path"]),
        ("write 'hello world' to test.txt", ["content", "file_path"]),
        ("fetch https://example.com", ["url"]),
        ("search for python tutorials", ["query"]),
    ]

    print("\nTesting entity extraction:\n")
    for message, entity_types in tests:
        entities = extractor.extract(message, entity_types)
        print(f"Message: {message}")
        print(f"  Entities: {entities}")
        print()
