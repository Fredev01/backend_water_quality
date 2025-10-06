from abc import ABC, abstractmethod

from app.share.ai.domain.model import ChatConfig


class AIChatService(ABC):
    @abstractmethod
    def chat(self, chat_config: ChatConfig, message: str):
        pass


class AIChatRepo(ABC):
    @abstractmethod
    async def chat(self, message: str, id_chat: str | None = None):
        pass

    @abstractmethod
    def get_chat(self, uuid: str | None = None) -> dict:
        pass

    @abstractmethod
    def add_message(self, message: str, role: str, uuid: str | None = None) -> dict:
        pass
