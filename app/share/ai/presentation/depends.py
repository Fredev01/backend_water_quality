from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from app.share.ai.domain.repo import AIChatService
from app.share.ai.services.open_router_imp import OpenRouterService
from app.share.ai.infra.ai_chat_impl import AIChatImpl


@lru_cache
def get_ai_service() -> AIChatService:
    return OpenRouterService()


@lru_cache
def get_ai_chat_repo(
    ai_chat_service: Annotated[AIChatService, Depends(get_ai_service)],
) -> AIChatService:
    return AIChatImpl(ai_chat_service=ai_chat_service)
