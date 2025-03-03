from firebase_admin import initialize_app, App

from app.share.firebase.domain.config import FirebaseConfig


class FirebaseInitializer:

    firebase_admin: App = None

    @classmethod
    def initialize(cls, config: FirebaseConfig):
        if cls.firebase_admin is None:
            cls.firebase_admin = initialize_app(config.cread)

        return cls.firebase_admin

    @classmethod
    def get(cls):
        return cls.firebase_admin
