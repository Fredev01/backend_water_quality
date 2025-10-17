from abc import ABC, abstractmethod
from typing import Optional, List
from .models import ChatMessage, ChatSession, ChatConfig

class AIChatService(ABC):
    """Abstract base class for AI chat services"""
    
    @abstractmethod
    async def create_session(self, context: str, metadata: Optional[dict] = None) -> ChatSession:
        """Create a new chat session with the given context"""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a chat session by ID"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        session_id: str,
        message: str,
        context: Optional[str] = None
    ) -> str:
        """
        Process a user message and return the AI's response
        
        Args:
            session_id: The chat session ID
            message: The user's message
            context: Optional additional context to prepend to the conversation
            
        Returns:
            The AI's response
        """
        pass
