from app.share.jwt.domain.payload import MeterPayload, UserPayload
from app.share.socketio.domain.repository import SessionMeterSocketIORepository


class SessionUserSocketIORepositoryImpl(SessionMeterSocketIORepository):
    sessions: dict[str, UserPayload] = {}

    @classmethod
    def get(cls, id: str):
        return cls.sessions.get(id)

    @classmethod
    def add(cls, id: str, payload: UserPayload):
        cls.sessions[id] = payload

    @classmethod
    def delete(cls, id: str):
        cls.sessions.pop(id)


class SessionMeterSocketIORepositoryImpl(SessionMeterSocketIORepository):
    sessions: dict[str, MeterPayload] = {}

    @classmethod
    def get(cls, id: str):
        return cls.sessions.get(id)

    @classmethod
    def add(cls, id: str, payload: MeterPayload):
        cls.sessions[id] = payload

    @classmethod
    def delete(cls, id: str):
        cls.sessions.pop(id)
