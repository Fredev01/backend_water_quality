from abc import ABC, abstractmethod

from app.share.users.domain.model import UserDetail


class UserRepository(ABC):
    @abstractmethod
    def get_by_uid(self, uid: str) -> UserDetail:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> UserDetail:
        pass
