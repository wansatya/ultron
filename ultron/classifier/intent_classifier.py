"""Intent classification using zero-shot BART-MNLI"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from transformers import pipeline


@dataclass
class Intent:
    """Represents a classified intent"""
    name: str
    description: str
    tool: str
    entities: List[str]
    confidence: float


class IntentClassifier:
    """Zero-shot intent classifier using BART-MNLI"""

    def __init__(self, intents_path: str = "data/intents.json", device: str = "cpu"):
        self.device = device
        self.intents_path = Path(intents_path)
        self.intents: List[Dict] = []
        self.candidate_labels: List[str] = []
        self.intent_map: Dict[str, Dict] = {}

        # Load intents
        self._load_intents()

        # Initialize zero-shot classifier
        print(f"Loading intent classifier (BART-MNLI) on {device}...")
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if device == "cuda" else -1
        )
        print("Intent classifier loaded successfully")

    def _load_intents(self):
        """Load intent definitions from JSON file"""
        if not self.intents_path.exists():
            raise FileNotFoundError(f"Intents file not found: {self.intents_path}")

        with open(self.intents_path, 'r') as f:
            data = json.load(f)
            self.intents = data["intents"]

        # Create candidate labels and intent mapping
        for intent in self.intents:
            label = intent["description"]
            self.candidate_labels.append(label)
            self.intent_map[label] = intent

    def add_skill_intent(self, skill_name: str, description: str, tool_name: str, entities: List[str]):
        """
        Dynamically add a skill as an intent

        Args:
            skill_name: Name of the skill
            description: Description for zero-shot classification
            tool_name: Tool name (e.g., 'skill.weather')
            entities: Required entity types
        """
        # Create intent dict
        intent = {
            "name": skill_name,
            "description": description,
            "tool": tool_name,
            "entities": entities,
            "examples": []  # Skills provide examples separately
        }

        # Add to intents list
        self.intents.append(intent)

        # Add to candidate labels and mapping
        self.candidate_labels.append(description)
        self.intent_map[description] = intent

        logger = logging.getLogger(__name__)
        logger.info(f"Added skill intent: {skill_name} -> {tool_name}")

    def classify(self, message: str) -> Intent:
        """
        Classify a message into an intent using zero-shot classification

        Args:
            message: User message to classify

        Returns:
            Intent object with classification results
        """
        # Run zero-shot classification
        result = self.classifier(
            message,
            candidate_labels=self.candidate_labels,
            multi_label=False
        )

        # Get top prediction
        top_label = result["labels"][0]
        confidence = result["scores"][0]

        # Map to intent
        intent_data = self.intent_map[top_label]

        return Intent(
            name=intent_data["name"],
            description=intent_data["description"],
            tool=intent_data["tool"],
            entities=intent_data["entities"],
            confidence=confidence
        )

    def classify_with_alternatives(self, message: str, top_k: int = 3) -> List[Tuple[Intent, float]]:
        """
        Classify message and return top-k alternatives

        Args:
            message: User message to classify
            top_k: Number of top predictions to return

        Returns:
            List of (Intent, confidence) tuples
        """
        result = self.classifier(
            message,
            candidate_labels=self.candidate_labels,
            multi_label=False
        )

        results = []
        for i in range(min(top_k, len(result["labels"]))):
            label = result["labels"][i]
            confidence = result["scores"][i]
            intent_data = self.intent_map[label]

            intent = Intent(
                name=intent_data["name"],
                description=intent_data["description"],
                tool=intent_data["tool"],
                entities=intent_data["entities"],
                confidence=confidence
            )
            results.append((intent, confidence))

        return results


if __name__ == "__main__":
    # Test the classifier
    classifier = IntentClassifier()

    test_messages = [
        "run ls -la",
        "read config.yaml",
        "write 'hello world' to test.txt",
        "fetch https://example.com",
        "search for python tutorials",
        "hello there",
        "check disk space",
    ]

    print("\nTesting intent classification:\n")
    for msg in test_messages:
        intent = classifier.classify(msg)
        print(f"Message: {msg}")
        print(f"  Intent: {intent.name} (confidence: {intent.confidence:.2f})")
        print(f"  Tool: {intent.tool}")
        print()
