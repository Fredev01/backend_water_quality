from abc import ABC, abstractmethod
from .models import ChatMessage, ChatSession

class AIChatService(ABC):
    """Abstract base class for AI chat services"""
    
    @abstractmethod
    async def create_session(self, session_id: str, context: str, metadata: dict | None = None) -> ChatSession:
        """
        Create a new chat session with the given context
        
        Args:
            session_id: The ID for the chat session
            context: The initial context for the chat session
            metadata: Optional metadata for the session
            
        Returns:
            The created chat session
        """
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> ChatSession | None:
        """Retrieve a chat session by ID"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        session_id: str,
        message: str,
        context: str | None = None
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
