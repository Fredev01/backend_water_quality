from abc import ABC, abstractmethod
from .model import WaterQualityMeter, WaterQualityMeterSensor


class WaterQualityMeterRepository(ABC):
    @abstractmethod
    def add(self, water_quality_meter: WaterQualityMeter) -> WaterQualityMeter:
        pass

    @abstractmethod
    def add_sensor(self, water_quality_meter: WaterQualityMeter, sensor: WaterQualityMeterSensor) -> WaterQualityMeter:
        pass

    @abstractmethod
    def get_details(self, id_workspace: str, id_meter: str) -> WaterQualityMeter:
        pass

    @abstractmethod
    def get_list(self, id_workspace: str) -> list[WaterQualityMeter]:
        pass

    @abstractmethod
    def delete(self, id_workspace: str, id_meter: str) -> bool:
        pass

    @abstractmethod
    def update(self, id_workspace: str, id_meter: str, water_quality_meter: WaterQualityMeter) -> WaterQualityMeter:
        pass


class WaterQMConnection(ABC):
    @abstractmethod
    def create_connection(self, id_workspace: str, id_meter: str) -> str:
        pass

    @abstractmethod
    def receive(self) -> bool:
        pass
