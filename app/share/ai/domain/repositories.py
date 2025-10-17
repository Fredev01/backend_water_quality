from abc import ABC, abstractmethod
from typing import Optional, List
from .models import ChatSession, ChatMessage

class ChatRepository(ABC):
    """Abstract base class for chat session storage"""
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a chat session by ID"""
        pass
    
    @abstractmethod
    async def create_session(self, session: ChatSession) -> ChatSession:
        """Create a new chat session"""
        pass
    
    @abstractmethod
    async def update_session(self, session: ChatSession) -> ChatSession:
        """Update an existing chat session"""
        pass
    
    @abstractmethod
    async def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Add a message to a chat session"""
        pass
    
    @abstractmethod
    async def get_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a session"""
        pass
