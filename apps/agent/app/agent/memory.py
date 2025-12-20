"""
Conversation memory management.

This module provides session-based conversation memory for the agent.
Currently uses in-memory storage - can be swapped for Redis/PostgreSQL later.
"""

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in the conversation."""

    role: str  # "user", "assistant", or "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationSession(BaseModel):
    """A conversation session with message history."""

    session_id: str
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a message to the conversation."""
        self.messages.append(
            Message(role=role, content=content, metadata=metadata or {})
        )
        self.updated_at = datetime.utcnow()

    def get_messages_for_llm(self) -> list[dict[str, str]]:
        """Get messages formatted for LLM context."""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def get_recent_messages(self, limit: int = 20) -> list[Message]:
        """Get the most recent messages."""
        return self.messages[-limit:]

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []
        self.updated_at = datetime.utcnow()


class MemoryStore:
    """
    In-memory conversation store.

    This is a simple implementation for development.
    Replace with Redis/PostgreSQL for production.
    """

    def __init__(self, max_sessions: int = 1000, session_ttl_hours: int = 24) -> None:
        """
        Initialize the memory store.

        Args:
            max_sessions: Maximum number of sessions to keep in memory.
            session_ttl_hours: Hours before a session expires.
        """
        self._sessions: dict[str, ConversationSession] = {}
        self._max_sessions = max_sessions
        self._session_ttl = timedelta(hours=session_ttl_hours)

    def get_session(self, session_id: str) -> ConversationSession:
        """
        Get or create a conversation session.

        Args:
            session_id: The session identifier.

        Returns:
            The conversation session.
        """
        self._cleanup_expired()

        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(session_id=session_id)

        return self._sessions[session_id]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a conversation session.

        Args:
            session_id: The session identifier.

        Returns:
            True if session was deleted, False if not found.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def list_sessions(self) -> list[str]:
        """List all active session IDs."""
        self._cleanup_expired()
        return list(self._sessions.keys())

    def _cleanup_expired(self) -> None:
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired = [
            sid
            for sid, session in self._sessions.items()
            if now - session.updated_at > self._session_ttl
        ]
        for sid in expired:
            del self._sessions[sid]

        # Also enforce max sessions (remove oldest)
        if len(self._sessions) > self._max_sessions:
            sorted_sessions = sorted(
                self._sessions.items(), key=lambda x: x[1].updated_at
            )
            to_remove = len(self._sessions) - self._max_sessions
            for sid, _ in sorted_sessions[:to_remove]:
                del self._sessions[sid]


# Global memory store instance
_memory_store: MemoryStore | None = None


def get_memory_store() -> MemoryStore:
    """Get the global memory store instance."""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store

