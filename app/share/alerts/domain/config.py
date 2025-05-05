from app.share.config import Config


class ConfigOneSignal(Config):
    @property
    def api_key(self):
        return self.get_env("ONESIGNAL_API_KEY")

    @property
    def app_id(self):
        return self.get_env("ONESIGNAL_APP_ID")
