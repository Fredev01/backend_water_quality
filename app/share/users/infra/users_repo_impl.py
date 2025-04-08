from app.share.users.domain.model import UserDetail
from app.share.users.domain.repository import UserRepository
from firebase_admin import auth


class UserRepositoryImpl(UserRepository):
    def get_by_uid(self, uid: str) -> UserDetail:
        auth_user: auth.UserRecord = auth.get_user(uid)
        return UserDetail(
            uid=auth_user.uid,
            username=auth_user.display_name,
            email=auth_user.email,
            phone=auth_user.phone_number
        )
