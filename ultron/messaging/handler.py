"""Message handler - main processing pipeline"""

import logging
from typing import Dict, Any
from ..classifier.intent_classifier import IntentClassifier
from ..classifier.entity_extractor import EntityExtractor
from ..generator.response import ResponseGenerator
from ..session.manager import SessionManager
from ..tools.registry import get_tool
from ..tools.base import ToolContext

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles message processing pipeline"""

    def __init__(
        self,
        intent_classifier: IntentClassifier,
        entity_extractor: EntityExtractor,
        response_generator: ResponseGenerator,
        session_manager: SessionManager
    ):
        self.intent_classifier = intent_classifier
        self.entity_extractor = entity_extractor
        self.response_generator = response_generator
        self.session_manager = session_manager

    async def handle_message(self, user_id: str, message: str) -> str:
        """
        Process a user message through the full pipeline

        Pipeline:
        1. Load user session
        2. Classify intent
        3. Extract entities
        4. Execute tool
        5. Generate response
        6. Update session
        7. Return response

        Args:
            user_id: User identifier
            message: User message text

        Returns:
            Response text to send back to user
        """
        try:
            # 1. Load session
            session = self.session_manager.load_session(user_id)
            session.add_message("user", message)

            # 2. Classify intent
            intent = self.intent_classifier.classify(message)
            logger.info(f"Classified intent: {intent.name} (confidence: {intent.confidence:.2f})")

            # 3. Extract entities
            entities = self.entity_extractor.extract(message, intent.entities)
            logger.info(f"Extracted entities: {entities}")

            # 4. Execute tool
            tool = get_tool(intent.tool)
            if tool is None:
                response = f"Tool not found: {intent.tool}"
                session.add_message("assistant", response, {"error": "tool_not_found"})
                self.session_manager.save_session(session)
                return response

            # Create tool context
            tool_context = ToolContext(
                user_id=user_id,
                session_key=user_id,
                message=message,
                metadata={"intent": intent.name, "confidence": intent.confidence}
            )

            # Execute tool
            result = await tool.execute(entities, tool_context)
            logger.info(f"Tool execution: success={result.success}")

            # 5. Generate response
            response_context = {
                "message": message,
                "output": result.output,
                "error": result.error,
                **entities,
                **(result.metadata or {})
            }

            response = self.response_generator.generate(
                intent.name,
                response_context,
                success=result.success
            )

            # 6. Update session
            session.add_message(
                "assistant",
                response,
                {
                    "intent": intent.name,
                    "tool": intent.tool,
                    "success": result.success
                }
            )
            session.update_context("last_intent", intent.name)
            session.update_context("last_tool", intent.tool)

            self.session_manager.save_session(session)

            # 7. Return response
            return response

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            error_response = f"Sorry, I encountered an error: {str(e)}"

            # Try to save error to session
            try:
                session.add_message("assistant", error_response, {"error": str(e)})
                self.session_manager.save_session(session)
            except:
                pass

            return error_response
