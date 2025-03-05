from fastapi import HTTPException
from firebase_admin import auth, db
import requests

from app.features.auth.domain.model import UserLogin, UserRegister
from app.share.firebase.domain.config import FirebaseConfigImpl


class AuthService:
    def register(self, user: UserRegister) -> auth.UserRecord:
        return auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.username,
            phone_number=user.phone,
        )

    def save_userData(self, user: auth.UserRecord, rol: str):
        db.reference('/users').child(user.uid).set({
            "rol": rol,
        })

        return user

    def login(self, user: UserLogin) -> auth.UserRecord:

        config = FirebaseConfigImpl()
        api_key = config.api_key
        url_sign_in = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}'
        print(url_sign_in)

        auth_user = auth.get_user_by_email(user.email)

        body = {
            "email": user.email,
            "password": user.password,
        }

        response = requests.post(url_sign_in, json=body)
        print(response.json())

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        return auth_user
