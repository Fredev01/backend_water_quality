from pydantic import BaseModel


class ChatConfig(BaseModel):
    """Configuración del agente de chat."""

    name: str
    system_prompt: str | (str)
    tools: dict[str, callable] = {}
    initial_context: dict[str, str | int | float] = {}
    history: list[dict[str, str]] = []


class ChatBuilder:
    """Builder fluido para crear configuraciones de chat y mantener historial."""

    def __init__(self):
        self._name: str | None = None
        self._system_prompt: str | None = None
        self._tools: dict[str, callable] = {}
        self._initial_context: dict[str, str | int | float] = {}
        self._history: list[dict[str, str]] = []

    def with_name(self, name: str) -> "ChatBuilder":
        self._name = name
        return self

    def with_system_prompt(self, prompt: str | (str)) -> "ChatBuilder":
        self._system_prompt = prompt
        self._history.append({"role": "system", "content": prompt})
        return self

    def add_tool(self, name: str, fn: callable) -> "ChatBuilder":
        self._tools[name] = fn
        return self

    def with_initial_context(self, ctx: dict[str, str | int | float]) -> "ChatBuilder":
        self._initial_context = ctx
        return self

    def with_history(self, history: list[dict[str, str]]) -> "ChatBuilder":
        self._history = history.copy()
        return self

    def send_user(self, message: str) -> "ChatBuilder":
        self._history.append({"role": "user", "content": message})
        return self

    def build(self) -> ChatConfig:
        if not self._name:
            raise ValueError("Debe definir un nombre para el agente.")
        if not self._system_prompt:
            raise ValueError("Debe definir un system prompt.")

        cfg = ChatConfig(
            name=self._name,
            system_prompt=self._system_prompt,
            tools=self._tools,
            initial_context=self._initial_context,
            history=self._history,
        )

        return cfg
