"""Test script to verify Ultron components"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_intent_classifier():
    """Test intent classification"""
    print("=" * 60)
    print("Testing Intent Classifier")
    print("=" * 60)

    from ultron.classifier.intent_classifier import IntentClassifier

    classifier = IntentClassifier(intents_path="data/intents.json")

    test_messages = [
        "run ls -la",
        "read config.yaml",
        "write 'hello world' to test.txt",
        "fetch https://example.com",
        "search for python tutorials",
        "hello there",
    ]

    for msg in test_messages:
        intent = classifier.classify(msg)
        print(f"\nMessage: {msg}")
        print(f"  Intent: {intent.name} (confidence: {intent.confidence:.2f})")
        print(f"  Tool: {intent.tool}")


async def test_entity_extractor():
    """Test entity extraction"""
    print("\n" + "=" * 60)
    print("Testing Entity Extractor")
    print("=" * 60)

    from ultron.classifier.entity_extractor import EntityExtractor

    extractor = EntityExtractor()

    tests = [
        ("run ls -la", ["command"]),
        ("read /etc/hosts", ["file_path"]),
        ("write 'hello world' to test.txt", ["content", "file_path"]),
        ("fetch https://example.com", ["url"]),
        ("search for python tutorials", ["query"]),
    ]

    for message, entity_types in tests:
        entities = extractor.extract(message, entity_types)
        print(f"\nMessage: {message}")
        print(f"  Entities: {entities}")


async def test_tools():
    """Test tool execution"""
    print("\n" + "=" * 60)
    print("Testing Tools")
    print("=" * 60)

    from ultron.tools.system import ReadFileTool
    from ultron.tools.base import ToolContext

    tool = ReadFileTool()
    context = ToolContext(
        user_id="test_user",
        session_key="test_session",
        message="read config.yaml"
    )

    result = await tool.execute({"file_path": "config.yaml"}, context)
    print(f"\nTool: {tool.name()}")
    print(f"Success: {result.success}")
    if result.success:
        print(f"Output (first 200 chars): {result.output[:200]}...")
    else:
        print(f"Error: {result.error}")


async def test_response_generator():
    """Test response generation"""
    print("\n" + "=" * 60)
    print("Testing Response Generator")
    print("=" * 60)

    from ultron.generator.response import ResponseGenerator

    generator = ResponseGenerator()

    # Test template filling
    test_cases = [
        ("execute_command", {"command": "ls -la", "output": "file1.txt\nfile2.txt"}, True),
        ("read_file", {"file_path": "config.yaml", "content": "key: value"}, True),
        ("error", {"error": "File not found"}, False),
    ]

    for intent, context, success in test_cases:
        response = generator.generate(intent, context, success=success)
        print(f"\nIntent: {intent}")
        print(f"Response: {response[:200]}...")


async def main():
    """Run all tests"""
    print("\nUltron Component Tests")
    print("=" * 60)
    print()

    try:
        await test_intent_classifier()
        await test_entity_extractor()
        await test_tools()
        await test_response_generator()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
