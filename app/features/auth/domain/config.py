
from app.share.config import AuthConfig


class AuthConfigImpl(AuthConfig):
    @property
    def secret_key(self):
        return self.get_env('SECRET_KEY')
