from firebase_admin import auth
from app.share.users.domain.model.user import UserDetail, UserUpdate
from app.share.users.domain.repository import UserRepository


class UserRepositoryImpl(UserRepository):
    def get_by_uid(self, uid: str) -> UserDetail:
        auth_user: auth.UserRecord = auth.get_user(uid)
        return UserDetail(
            uid=auth_user.uid,
            username=auth_user.display_name,
            email=auth_user.email,
            phone=auth_user.phone_number
        )

    def get_by_email(self, email: str) -> UserDetail:
        auth_user: auth.UserRecord = auth.get_user_by_email(email)
        return UserDetail(
            uid=auth_user.uid,
            username=auth_user.display_name,
            email=auth_user.email,
            phone=auth_user.phone_number
        )

    def get_all(self) -> list[UserDetail]:
        users = auth.list_users()
        print(users)
        return []

    def update_user(self, uid: str, user: UserUpdate) -> UserDetail:
        user_record: auth.UserRecord = auth.update_user(
            uid=uid,
            email=user.email,
            password=user.password,
            display_name=user.username,
            phone_number=user.phone
        )

        return UserDetail(
            uid=user_record.uid,
            username=user_record.display_name,
            email=user_record.email,
            phone=user_record.phone_number
        )
