from abc import ABC, abstractmethod

from app.features.meters.domain.model import Sensor, SensorRecord, WQMeterCreate, WaterQualityMeterSensor
from .model import WaterQualityMeter


class WaterQualityMeterRepository(ABC):
    @abstractmethod
    def add(self,  id_workspace: str, owner: str, water_quality_meter: WQMeterCreate) -> WaterQualityMeter:
        pass

    @abstractmethod
    def get_list(self, id_workspace: str, owner: str) -> list[WaterQualityMeter]:
        pass

    @abstractmethod
    def get_details(self, id_workspace: str, owner: str, id_meter: str) -> WaterQualityMeterSensor:
        pass

    @abstractmethod
    def delete(self, id_workspace: str, owner: str, id_meter: str) -> bool:
        pass

    @abstractmethod
    def update(self, id_workspace: str, owner: str, str, id_meter: str, water_quality_meter: WaterQualityMeter) -> WaterQualityMeter:
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
    def create_connection(self, id_workspace: str, owner: str, id_meter: str) -> str:
        pass

    @abstractmethod
    def receive(self) -> bool:
        pass
