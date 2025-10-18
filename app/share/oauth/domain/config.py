from app.share.config import Config


class GithubOAuthConfigImpl(Config):
    @property
    def client_id(self) -> str:
        return self.get_env("GITHUB_CLIENT_ID")

    @property
    def client_secret(self) -> str:
        return self.get_env("GITHUB_CLIENT_SECRET")

    @property
    def callback_url(self) -> str:
        return self.get_env("GITHUB_CALLBACK_URL")

    @property
    def frontend_origin(self) -> str:
        return self.get_env("FRONTEND_ORIGIN")
