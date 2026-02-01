"""Session management for conversation tracking"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class Message:
    """Represents a single message in conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Represents a user session"""
    user_id: str
    created_at: str
    updated_at: str
    history: List[Message] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the session history"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow().isoformat() + "Z",
            metadata=metadata or {}
        )
        self.history.append(message)
        self.updated_at = message.timestamp

    def get_recent_history(self, limit: int = 10) -> List[Message]:
        """Get recent messages from history"""
        return self.history[-limit:]

    def update_context(self, key: str, value: Any):
        """Update session context"""
        self.context[key] = value
        self.updated_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "history": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "metadata": msg.metadata
                }
                for msg in self.history
            ],
            "context": self.context
        }


class SessionManager:
    """Manage user sessions with JSON file storage"""

    def __init__(self, storage_path: str = "./data/sessions", max_history: int = 50):
        self.storage_path = Path(storage_path)
        self.max_history = max_history
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_session_file(self, user_id: str) -> Path:
        """Get the path to a user's session file"""
        return self.storage_path / f"{user_id}.json"

    def load_session(self, user_id: str) -> Session:
        """Load or create a session for a user"""
        session_file = self._get_session_file(user_id)

        if session_file.exists():
            # Load existing session
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)

                # Reconstruct Message objects
                history = [
                    Message(
                        role=msg["role"],
                        content=msg["content"],
                        timestamp=msg["timestamp"],
                        metadata=msg.get("metadata", {})
                    )
                    for msg in data.get("history", [])
                ]

                # Trim history if too long
                if len(history) > self.max_history:
                    history = history[-self.max_history:]

                return Session(
                    user_id=data["user_id"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                    history=history,
                    context=data.get("context", {})
                )

            except Exception as e:
                print(f"Error loading session for {user_id}: {e}")
                # Create new session on error
                return self._create_new_session(user_id)
        else:
            # Create new session
            return self._create_new_session(user_id)

    def _create_new_session(self, user_id: str) -> Session:
        """Create a new session"""
        now = datetime.utcnow().isoformat() + "Z"
        return Session(
            user_id=user_id,
            created_at=now,
            updated_at=now,
            history=[],
            context={}
        )

    def save_session(self, session: Session):
        """Save session to disk"""
        session_file = self._get_session_file(session.user_id)

        try:
            # Trim history before saving
            if len(session.history) > self.max_history:
                session.history = session.history[-self.max_history:]

            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)

        except Exception as e:
            print(f"Error saving session for {session.user_id}: {e}")

    def reset_session(self, user_id: str):
        """Reset a user's session"""
        session_file = self._get_session_file(user_id)
        if session_file.exists():
            session_file.unlink()

    def delete_session(self, user_id: str):
        """Delete a user's session file"""
        self.reset_session(user_id)


if __name__ == "__main__":
    # Test session manager
    manager = SessionManager(storage_path="./test_sessions")

    # Create and save a session
    session = manager.load_session("test_user")
    session.add_message("user", "hello", {"intent": "chat"})
    session.add_message("assistant", "Hi there!", {"tool": "response.generate"})
    session.update_context("last_intent", "chat")

    manager.save_session(session)
    print(f"Session saved: {session.to_dict()}")

    # Load it back
    loaded = manager.load_session("test_user")
    print(f"\nLoaded session: {loaded.to_dict()}")

    # Cleanup
    manager.delete_session("test_user")
    Path("./test_sessions").rmdir()
