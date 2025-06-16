from abc import ABC, abstractmethod

from app.features.meters.domain.model import Sensor, SensorRecord, WQMeterCreate, WaterQualityMeterSensor
from app.share.socketio.domain.model import Record
from .model import SensorIdentifier, SensorQueryParams, SensorRecordsResponse, SensorStatus, WQMeterUpdate, WaterQualityMeter


class WaterQualityMeterRepository(ABC):
    @abstractmethod
    def add(self,  id_workspace: str, owner: str, water_quality_meter: WQMeterCreate) -> WaterQualityMeter:
        pass

    @abstractmethod
    def get_list(self, id_workspace: str, owner: str) -> list[WaterQualityMeter]:
        pass

    @abstractmethod
    def get(self, id_workspace: str, owner: str, id_meter: str) -> WaterQualityMeter:
        pass

    @abstractmethod
    def delete(self, id_workspace: str, owner: str, id_meter: str) -> WaterQualityMeter:
        pass

    @abstractmethod
    def update(self, id_workspace: str, owner: str, id_meter: str, meter: WQMeterUpdate) -> WaterQualityMeter:
        pass

    @abstractmethod
    def is_active(self, id_workspace: str, owner: str, id_meter: str) -> bool:
        pass


class WaterQMSensor(ABC):
    @abstractmethod
    def add_sensor(self, id_workspace: str, owner: str, id_meter: str, sensors: list[Sensor]) -> WaterQualityMeter:
        pass

    @abstractmethod
    def add_record(self, id_workspace: str, owner: str, id_meter: str, sensors_record: list[SensorRecord]) -> list[SensorRecord]:
        pass


class WaterQMConnection(ABC):
    @abstractmethod
    def create(self, id_workspace: str, owner: str, id_meter: str) -> int:
        pass

    @abstractmethod
    def receive(self, password: int) -> bool:
        pass


class MeterRecordsRepository(ABC):
    @abstractmethod
    def get_latest_sensor_records(
        self,
        identifier: SensorIdentifier,
        params: SensorQueryParams
    ) -> SensorRecordsResponse:
        pass

    @abstractmethod
    def get_sensor_records(
        self,
        identifier: SensorIdentifier,
        params: SensorQueryParams
    ) -> list[Record]:
        pass
