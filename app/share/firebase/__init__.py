from firebase_admin import initialize_app

from app.share.firebase.domain.config import FirebaseConfig


def initialize(config: FirebaseConfig):
    firebase_admin = initialize_app(config.cread)
    return firebase_admin
