from pyparsing import ABC, abstractmethod

from app.share.meter_records.domain.model import (
    RecordsDict,
    SensorIdentifier,
    SensorQueryParams,
)
from app.share.socketio.domain.model import Record
from app.share.meter_records.domain.response import SensorRecordsResponse


class MeterRecordsRepository(ABC):

    @abstractmethod
    def get_sensor_records(
        self, identifier: SensorIdentifier, params: SensorQueryParams
    ) -> list[Record]:
        pass

    @abstractmethod
    def query_sensor_records(
        self, identifier: SensorIdentifier, params: SensorQueryParams
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

    @abstractmethod
    def query_records(
        self, identifier: SensorIdentifier, params: SensorQueryParams
    ) -> RecordsDict:
        pass
