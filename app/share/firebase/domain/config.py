from firebase_admin import credentials
from dotenv import load_dotenv
import os

from app.share.config import FirebaseConfig

load_dotenv()


class FirebaseConfigImpl(FirebaseConfig):
    cread = credentials.Certificate(
        os.getenv('FIREBASE_ADMIN_CREDENTIALS'))

    api_key = os.getenv('FIREBASE_API_KEY')
