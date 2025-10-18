from typing import Generator
from fastapi import Depends

from app.share.ai.domain.config import OpenRouterConfig
from app.share.ai.domain.services import AIChatService
from app.share.ai.infra.firebase_repository import FirebaseChatRepository
from app.share.ai.services.openai_service import OpenAIChatService


def get_chat_repository() -> FirebaseChatRepository:
    """Get chat repository instance"""
    return FirebaseChatRepository()


def get_ai_service(
    repository: FirebaseChatRepository = Depends(get_chat_repository),
) -> AIChatService:
    """Get AI chat service instance"""
    return OpenAIChatService(config=OpenRouterConfig(), repository=repository)
