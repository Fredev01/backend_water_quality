import uuid
from typing import List, Optional
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from app.share.ai.domain.config import OpenRouterConfig

from ..domain.models import ChatSession, ChatMessage, MessageRole
from ..domain.services import AIChatService
from ..domain.repositories import ChatRepository


class OpenAIChatService(AIChatService):
    """OpenAI chat service implementation using OpenRouter"""

    def __init__(self, config: OpenRouterConfig, repository: ChatRepository):
        self.config = config
        self.repository = repository
        
        # Create the model
        model = OpenAIChatModel(
            model_name=self.config.model,
            provider=OpenRouterProvider(api_key=self.config.api_key),
        )
        
        # Create the agent with the model
        self.agent = Agent(
            model=model,
            deps_type=str,  # Context will be passed as dependency
            output_type=str,  # Response will be a string
            system_prompt=(
                "Eres un experto en calidad del agua. "
                "Responde preguntas basándote únicamente en el contexto proporcionado. "
                "Si la pregunta está fuera del contexto, indica que solo puedes responder "
                "preguntas relacionadas con la calidad del agua y el contexto proporcionado."
            ),
        )
        
        # Add dynamic system prompt for context
        @self.agent.system_prompt
        def add_context(ctx: RunContext[str]) -> str:
            """Add the context to the system prompt"""
            return f"\n\nContexto: {ctx.deps}"

    async def create_session(
        self, context: str, metadata: Optional[dict] = None
    ) -> ChatSession:
        """Create a new chat session with initial context"""
        session_id = str(uuid.uuid4())
        session = ChatSession(id=session_id, context=context, metadata=metadata or {})

        # Add system message with context
        system_message = ChatMessage(
            role=MessageRole.SYSTEM,
            content=(
                "Eres un experto en calidad del agua. "
                "Responde preguntas basándote en el contexto proporcionado. "
                "Si la pregunta está fuera del contexto, indica que solo puedes responder "
                "preguntas relacionadas con la calidad del agua y el contexto proporcionado.\n\n"
                f"Contexto: {context}"
            ),
        )

        session.messages.append(system_message)
        return await self.repository.create_session(session)

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a chat session by ID"""
        return await self.repository.get_session(session_id)

    async def chat(
        self, session_id: str, message: str, context: Optional[str] = None
    ) -> str:
        """Process a user message and return the AI's response"""
        # Get session
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Add user message to history
        user_message = ChatMessage(role=MessageRole.USER, content=message)
        await self.repository.add_message(session_id, user_message)

        # Prepare message history for the agent
        message_history = self._prepare_message_history(session)

        # Run the agent with the context and message history
        result = await self.agent.run(
            message,
            deps=session.context,  # Pass context as dependency
            message_history=message_history,
        )

        # Add assistant response to history
        assistant_message = ChatMessage(
            role=MessageRole.ASSISTANT, content=result.output
        )
        await self.repository.add_message(session_id, assistant_message)

        return result.output

    def _prepare_message_history(self, session: ChatSession) -> List[dict]:
        """Prepare message history for the agent"""
        messages = []
        
        # Add conversation history (skip system message as it's handled by agent)
        for msg in session.messages:
            if msg.role != MessageRole.SYSTEM:
                messages.append({"role": msg.role.value, "content": msg.content})
        
        return messages
