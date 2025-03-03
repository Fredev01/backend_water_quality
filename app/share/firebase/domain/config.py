from firebase_admin import credentials
from dotenv import load_dotenv
import os

from app.share.config import FirebaseConfig

load_dotenv()


class FirebaseConfigImpl(FirebaseConfig):
    cread = credentials.Certificate(
        os.getenv('FIREBASE_ADMIN_CREDENTIALS'))
