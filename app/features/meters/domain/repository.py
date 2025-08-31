from abc import ABC, abstractmethod

from app.features.meters.domain.model import (
    WQMeterCreate,
)
from .model import (
    WQMeterUpdate,
    WaterQualityMeter,
)


class WaterQualityMeterRepository(ABC):
    @abstractmethod
    def add(
        self, id_workspace: str, owner: str, water_quality_meter: WQMeterCreate
    ) -> WaterQualityMeter:
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
    def update(
        self, id_workspace: str, owner: str, id_meter: str, meter: WQMeterUpdate
    ) -> WaterQualityMeter:
        pass

    @abstractmethod
    def is_active(self, id_workspace: str, owner: str, id_meter: str) -> bool:
        pass
