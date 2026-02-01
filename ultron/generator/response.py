"""Response generation using Flan-T5"""

from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


class ResponseGenerator:
    """Generate natural language responses using Flan-T5"""

    # Response templates for different intents
    TEMPLATES = {
        "execute_command": "I executed `{command}`. Output:\n```\n{output}\n```",
        "read_file": "Here's the content of {file_path}:\n```\n{content}\n```",
        "write_file": "Successfully wrote to {file_path}",
        "web_fetch": "I fetched {url}. Here's what I found:\n\n{content}",
        "web_search": "Search results for '{query}':\n\n{results}",
        "error": "Sorry, I encountered an error: {error}",
        "chat": "{response}",
    }

    def __init__(self, model_name: str = "google/flan-t5-small", device: str = "cpu", max_length: int = 256):
        self.model_name = model_name
        self.device = device
        self.max_length = max_length

        print(f"Loading response generator ({model_name}) on {device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        if device == "cuda" and torch.cuda.is_available():
            self.model = self.model.to("cuda")

        print("Response generator loaded successfully")

    def generate(self, intent: str, context: Dict[str, Any], success: bool = True) -> str:
        """
        Generate a response based on intent and context

        Args:
            intent: The intent name
            context: Context dictionary with variables for template
            success: Whether the tool execution was successful

        Returns:
            Generated response string
        """
        # Handle errors
        if not success:
            return self._fill_template("error", context)

        # Use templates for simple intents
        if intent in ["execute_command", "write_file"]:
            return self._fill_template(intent, context)

        # For read_file, check if content needs summarization
        if intent == "read_file":
            content = context.get("output", "")
            if len(content) > 2000:
                # Summarize long content
                summary = self._summarize(content, max_length=200)
                context["content"] = f"{summary}\n\n(Content truncated - {len(content)} characters total)"
            else:
                context["content"] = content
            return self._fill_template(intent, context)

        # For web_fetch, summarize content
        if intent == "web_fetch":
            content = context.get("output", "")
            if len(content) > 1000:
                summary = self._summarize(content, max_length=300)
                context["content"] = summary
            else:
                context["content"] = content
            return self._fill_template(intent, context)

        # For web_search, use results directly
        if intent == "web_search":
            context["results"] = context.get("output", "No results found")
            return self._fill_template(intent, context)

        # For chat, generate response using Flan-T5
        if intent == "chat":
            message = context.get("message", "")
            generated = self._generate_text(f"Respond naturally to: {message}")
            context["response"] = generated
            return self._fill_template(intent, context)

        # Fallback: return raw output
        return context.get("output", "I processed your request.")

    def _fill_template(self, intent: str, context: Dict[str, Any]) -> str:
        """Fill a template with context variables"""
        template = self.TEMPLATES.get(intent, "{output}")

        try:
            return template.format(**context)
        except KeyError as e:
            # Missing variable, return partial fill
            return template.format_map(context)

    def _summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize text using Flan-T5"""
        prompt = f"Summarize this text concisely: {text[:2000]}"
        return self._generate_text(prompt, max_length=max_length)

    def _generate_text(self, prompt: str, max_length: int | None = None) -> str:
        """Generate text using Flan-T5"""
        if max_length is None:
            max_length = self.max_length

        try:
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )

            if self.device == "cuda" and torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=4,
                    early_stopping=True
                )

            # Decode
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response

        except Exception as e:
            return f"Failed to generate response: {str(e)}"


if __name__ == "__main__":
    # Test the response generator
    generator = ResponseGenerator()

    # Test template filling
    print("\nTesting template filling:\n")
    test_cases = [
        ("execute_command", {"command": "ls -la", "output": "file1.txt\nfile2.txt"}),
        ("read_file", {"file_path": "config.yaml", "content": "key: value"}),
        ("error", {"error": "File not found"}),
    ]

    for intent, context in test_cases:
        response = generator.generate(intent, context, success=True)
        print(f"Intent: {intent}")
        print(f"Response: {response}")
        print()

    # Test chat generation
    print("\nTesting chat generation:\n")
    chat_response = generator.generate("chat", {"message": "hello"}, success=True)
    print(f"Chat response: {chat_response}")
