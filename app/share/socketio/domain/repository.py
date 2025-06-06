from abc import ABC, abstractmethod

from app.share.jwt.domain.payload import MeterPayload, UserPayload
from app.share.socketio.domain.enum.meter_connection_state import MeterConnectionState
from app.share.socketio.domain.model import RecordBody, RecordResponse


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


class RecordRepository(ABC):
    @abstractmethod
    def add(self, meter_connection: MeterPayload, body: RecordBody) -> RecordResponse:
        pass


class MeterStateRepository(ABC):
    @abstractmethod
    def set_state(self, id_workspace: str,  id_meter: str, status: MeterConnectionState) -> MeterConnectionState:
        pass
