from fastapi import HTTPException
from firebase_admin import auth, db
import requests

from app.features.auth.domain.model import UserLogin, UserData, UserRegister
from app.share.firebase.domain.config import FirebaseConfigImpl


class AuthService:

    def register(self, user: UserRegister) -> auth.UserRecord:
        try:

            return auth.create_user(
                email=user.email,
                password=user.password,
                display_name=user.username,
                phone_number=user.phone,
            )

        except auth.EmailAlreadyExistsError:
            raise HTTPException(status_code=400, detail="Email already exists")
        except auth.PhoneNumberAlreadyExistsError:
            raise HTTPException(
                status_code=400, detail="Phone number already exists")
        except Exception as e:
            print(e.__class__.__name__)
            print(e)
            raise HTTPException(status_code=500, detail="Server error")

    def save_userData(self, user: auth.UserRecord, rol: str):
        auth.set_custom_user_claims(uid=user.uid, custom_claims={
            "rol": rol,
        })

        return user

    def login(self, user: UserLogin) -> UserData:

        try:
            config = FirebaseConfigImpl()
            api_key = config.api_key
            url_sign_in = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}'
            print(url_sign_in)

            auth_user: auth.UserRecord = auth.get_user_by_email(user.email)

            body = {
                "email": user.email,
                "password": user.password,
            }

            response = requests.post(url_sign_in, json=body)
            print(response.json())

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Invalid credentials")

            return UserData(
                email=auth_user.email,
                password="********",
                username=auth_user.display_name,
                phone=auth_user.phone_number,
                rol=auth_user.custom_claims.get("rol"),
            )

        except auth.UserNotFoundError:
            raise HTTPException(status_code=401, detail="Unregistered user")
        except Exception as e:
            print(e.__class__.__name__)
            print(e)
            raise HTTPException(status_code=500, detail="Server error")
