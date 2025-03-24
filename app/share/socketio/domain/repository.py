from abc import ABC, abstractmethod

from app.share.jwt.domain.payload import MeterPayload, UserPayload


class SessionMeterSocketIORepository(ABC):
    @abstractmethod
    def get(cls, id: str):
        pass

    @abstractmethod
    def add(cls, id: str, payload: MeterPayload):
        pass

    @abstractmethod
    def delete(cls, id: str):
        pass


class SessionUserSocketIORepository(ABC):
    @abstractmethod
    def get(self, id: str):
        pass

    @abstractmethod
    def add(self, user_id: str, payload: UserPayload):
        pass
