
from app.share.config import JWTConfig


class JWTConfigImpl(JWTConfig):
    @property
    def secret_key(self):
        return self.get_env('SECRET_KEY')
