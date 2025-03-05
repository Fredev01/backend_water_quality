from firebase_admin import credentials
from dotenv import load_dotenv
import os

from app.share.config import FirebaseConfig

# load_dotenv()


class FirebaseConfigImpl(FirebaseConfig):
    @property
    def cread(self):
        return credentials.Certificate(self.get_env('FIREBASE_ADMIN_CREDENTIALS'))

    @property
    def api_key(self):
        return self.get_env('FIREBASE_API_KEY')

    @property
    def database_url(self):
        return self.get_env('FIREBASE_REALTIME_URL')
