from firebase_admin import credentials
from dotenv import load_dotenv
import os

from app.share.config import FirebaseConfig

# load_dotenv()


class FirebaseConfigImpl(FirebaseConfig):
    @property
    def cread(self):
        private_key_raw = self.get_env('FIREBASE_PRIVATE_KEY')
        private_key_fixed = private_key_raw.replace('\\n', '\n')
        cred_dict = {
            'type': self.get_env('FIREBASE_TYPE'),
            'project_id': self.get_env('FIREBASE_PROJECT_ID'),
            'private_key_id': self.get_env('FIREBASE_PRIVATE_KEY_ID'),
            'private_key': private_key_fixed,
            'client_email': self.get_env('FIREBASE_CLIENT_EMAIL'),
            'client_id': self.get_env('FIREBASE_CLIENT_ID'),
            'auth_uri': self.get_env('FIREBASE_AUTH_URI'),
            'token_uri': self.get_env('FIREBASE_TOKEN_URI'),
            'auth_provider_x509_cert_url': self.get_env(
                'FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
            'client_x509_cert_url': self.get_env(
                'FIREBASE_CLIENT_X509_CERT_URL'),
            'universe_domain': self.get_env('FIREBASE_UNIVERSE_DOMAIN'),
        }
        return credentials.Certificate(cred_dict)

    @property
    def api_key(self):
        return self.get_env('FIREBASE_API_KEY')

    @property
    def database_url(self):
        return self.get_env('FIREBASE_REALTIME_URL')
