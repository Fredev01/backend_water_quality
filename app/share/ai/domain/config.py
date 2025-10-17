from app.share.config import Config


class OpenRouterConfig(Config):
    _instance = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenRouterConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not OpenRouterConfig._initialized:
            self._load_env()
            self._initialized = True

    def _load_env(self):
        self._api_key = self.get_env("OPEN_ROUTER_KEY")
        self._model = self.get_env("OPEN_ROUTER_MODEL")

    @property
    def api_key(self):
        return self._api_key

    @property
    def model(self):
        return self._model

    temperature: float = 0.7
    max_tokens: int = 1000
