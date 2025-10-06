from firebase_admin import db
from app.share.ai.domain.model import ChatBuilder, ChatConfig
from app.share.ai.domain.repo import AIChatRepo, AIChatService


class AIChatImpl(AIChatRepo):

    def __init__(self, ai_chat_service: AIChatService):
        self.ai_chat_service: AIChatService = ai_chat_service

    async def chat(self, message: str, id_chat: str | None = None):

        chat_build: ChatBuilder = (
            ChatBuilder()
            .with_name("Aqua Bot")
            .with_system_prompt(
                "Eres un asistente experto en calidad del agua. Responde con precisión técnica."
            )
        )

        if id_chat is not None:
            history = self.get_chat(id_chat)
            chat_build.with_history(history=history)

        config: ChatConfig = chat_build.build()

        return await self.ai_chat_service.chat(
            config=config,
            message=message,
        )

    def get_chat(self, uuid: str | None = None) -> dict:
        return {}

    def add_message(self, message: str, role: str, uuid: str | None = None) -> dict:
        return {}
