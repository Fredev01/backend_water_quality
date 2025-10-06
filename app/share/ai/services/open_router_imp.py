from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from app.share.ai.domain.config import OpenRouterConfig
from app.share.ai.domain.model import ChatConfig
from app.share.ai.domain.repo import AIChatService


class OpenRouterService(AIChatService):
    config = OpenRouterConfig()

    def _get_agent(self, chat_config: ChatConfig) -> Agent:
        model = OpenAIChatModel(
            model_name=self.config.model,
            provider=OpenRouterProvider(api_key=self.config.api_key),
        )
        return Agent(
            models=[model],
            name=chat_config.name,
            system_prompt=chat_config.system_prompt,
            tools=chat_config.tools,
        )

    async def chat(self, chat_config: ChatConfig, message: str):
        agent: Agent = self._get_agent(chat_config)
        response = await agent.run(user_prompt=message)
        return response.all_messages_json()
