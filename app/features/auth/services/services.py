from firebase_admin import auth

from app.features.auth.domain.model import UserLogin, UserRegister


class AuthService:
    def register(self, user: UserRegister) -> auth.UserRecord:
        return auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.username,
        )

    def login(self, user: UserLogin) -> auth.UserRecord:
        return auth.get_user_by_email(user.email)
