from abc import ABC, abstractmethod

from app.features.meters.domain.model import (
    Sensor,
    SensorRecord,
    WQMeterCreate,
    WaterQualityMeterSensor,
)
from app.share.socketio.domain.model import Record
from .model import (
    SensorIdentifier,
    SensorQueryParams,
    SensorRecordsResponse,
    SensorStatus,
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


class WaterQMSensor(ABC):
    @abstractmethod
    def add_sensor(
        self, id_workspace: str, owner: str, id_meter: str, sensors: list[Sensor]
    ) -> WaterQualityMeter:
        pass

    @abstractmethod
    def add_record(
        self,
        id_workspace: str,
        owner: str,
        id_meter: str,
        sensors_record: list[SensorRecord],
    ) -> list[SensorRecord]:
        pass


class MeterRecordsRepository(ABC):

    @abstractmethod
    def get_sensor_records(
        self, identifier: SensorIdentifier, params: SensorQueryParams
    ) -> list[Record]:
        pass

    @abstractmethod
    def query_sensor_records(
        self,
        identifier: SensorIdentifier,
        params: SensorQueryParams
    ) -> SensorRecordsResponse:
        """
        Query sensor records with optional date range and sensor type filters.

        Args:
            identifier: Sensor identifier
            params: Query parameters including:
                - start_date: Optional start date in format 'YYYY-MM-DD HH:MM:SS'
                - end_date: Optional end date in format 'YYYY-MM-DD HH:MM:SS' (defaults to now)
                - sensor_type: Optional sensor type to filter by
                - limit: Maximum number of records to return (default: 10)

        Returns:
            SensorRecordsResponse with filtered records in descending order (newest first)
        """
        pass
