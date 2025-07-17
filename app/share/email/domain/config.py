from app.share.config import Config


class EmailConfig(Config):
    @property
    def api_key(self):
        return self.get_env("RESEND_API_KEY")
