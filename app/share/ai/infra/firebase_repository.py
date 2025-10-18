from datetime import datetime, UTC
from typing import Any
import uuid
from firebase_admin import db
from firebase_admin.db import Reference

from ..domain.models import ChatSession, ChatMessage, MessageRole
from ..domain.repositories import ChatRepository


class FirebaseChatRepository(ChatRepository):
    """Firebase Realtime Database implementation of ChatRepository"""

    def __init__(self, path: str = "ai_chat_sessions"):
        self.ref: Reference = db.reference(f"/{path}")

    async def get_session(self, session_id: str) -> ChatSession | None:
        """Retrieve a chat session by ID"""
        session_data = self.ref.child(session_id).get()
        if not session_data:
            return None
        return self._deserialize_session(session_data)

    async def create_session(self, session: ChatSession) -> ChatSession:
        """Create a new chat session"""
        session_data = self._serialize_session(session)
        self.ref.child(session.id).set(session_data)
        return session

    async def update_session(self, session: ChatSession) -> ChatSession:
        """Update an existing chat session"""
        session_data = self._serialize_session(session)
        self.ref.child(session.id).update(session_data)
        return session

    async def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Add a message to a chat session"""
        message_data = self._serialize_message(message)
        session_ref = self.ref.child(session_id)
        session_ref.update(
            {"messages": {message.id: message_data}, "updated_at": {".sv": "timestamp"}}
        )

    async def get_messages(self, session_id: str) -> list[ChatMessage]:
        """Get all messages for a session"""
        session = await self.get_session(session_id)
        if not session:
            return []
        return session.messages

    def _serialize_session(self, session: ChatSession) -> dict[str, Any]:
        """Convert ChatSession to Firebase-compatible dict"""
        return {
            "id": session.id,
            "context": session.context,
            "created_at": (
                session.created_at.isoformat()
                if isinstance(session.created_at, datetime)
                else session.created_at
            ),
            "updated_at": {".sv": "timestamp"},
            "messages": {
                msg.id: self._serialize_message(msg) for msg in session.messages
            },
            "metadata": session.metadata or {},
        }

    def _deserialize_session(self, data: dict[str, Any]) -> ChatSession | None:
        """Convert Firebase data to ChatSession"""
        if not data:
            return None

        # Convert messages from dict to list
        messages_data = data.get("messages", {}) or {}
        messages = [
            self._deserialize_message(msg_data)
            for msg_id, msg_data in messages_data.items()
        ]

        # Sort messages by timestamp
        messages.sort(
            key=lambda x: (
                x.timestamp
                if isinstance(x.timestamp, datetime)
                else datetime.fromisoformat(x.timestamp)
            )
        )

        return ChatSession(
            id=data["id"],
            context=data["context"],
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
            messages=messages,
            metadata=data.get("metadata", {}),
        )

    def _serialize_message(self, message: ChatMessage) -> dict[str, Any]:
        """Convert ChatMessage to Firebase-compatible dict"""
        return {
            "id": message.id,
            "role": message.role.value,
            "content": message.content,
            "timestamp": (
                message.timestamp.isoformat()
                if isinstance(message.timestamp, datetime)
                else message.timestamp
            ),
        }

    def _deserialize_message(self, data: dict[str, Any]) -> ChatMessage:
        """Convert Firebase data to ChatMessage"""
        return ChatMessage(
            id=data.get("id", str(uuid.uuid4())),
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=self._parse_datetime(data.get("timestamp")),
        )

    def _parse_datetime(self, value: Any) -> datetime:
        """Parse datetime from various formats"""
        if value is None:
            return datetime.now(UTC)
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value / 1000, tz=UTC)  # Assume milliseconds
        return datetime.now(UTC)
