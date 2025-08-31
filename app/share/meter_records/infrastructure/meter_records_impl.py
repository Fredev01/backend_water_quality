from datetime import datetime
from fastapi import HTTPException
from firebase_admin import db
from typing import Any

from app.share.meter_records.domain.model import SensorIdentifier, SensorQueryParams
from app.share.meter_records.domain.repository import MeterRecordsRepository
from app.share.meter_records.domain.response import SensorRecordsResponse
from app.share.socketio.domain.model import Record, SRColorValue
from app.share.workspace.domain.model import WorkspaceRoles
from app.share.workspace.workspace_access import WorkspaceAccess


class MeterRecordsRepositoryImpl(MeterRecordsRepository):

    def __init__(self, workspace_access: WorkspaceAccess):
        self.workspace_access = workspace_access

    def get_sensor_records(
        self, identifier: SensorIdentifier, params: SensorQueryParams
    ) -> list[Record]:
        meter_ref = self._get_meter(identifier)

        records: dict[str, dict] = None
        if params.index is None:
            records = self._get_records(meter_ref, params)
        else:
            records = self._get_records_by_index(meter_ref, params)

        if not records:
            raise ValueError(
                f"No existen registros para el sensor: {identifier.sensor_name}"
            )

        result = []
        for timestamp, record in records.items():
            sensor_data = record.get(identifier.sensor_name)
            print(timestamp)
            if sensor_data:
                if identifier.sensor_name == "color":
                    result.append(
                        Record[SRColorValue](
                            id=timestamp,
                            datetime=datetime.fromisoformat(sensor_data["datetime"]),
                            value=SRColorValue(**sensor_data["value"]),
                        )
                    )
                else:
                    result.append(
                        Record[float](
                            id=timestamp,
                            datetime=datetime.fromisoformat(sensor_data["datetime"]),
                            value=sensor_data["value"],
                        )
                    )
        return result

    def _get_meter(self, identifier: SensorIdentifier) -> db.Reference:
        workspace = self.workspace_access.get_ref(
            identifier.workspace_id,
            identifier.user_id,
            roles=[
                WorkspaceRoles.ADMINISTRATOR,
                WorkspaceRoles.MANAGER,
                WorkspaceRoles.VISITOR,
            ],
            is_public=True,
        )

        meter_ref = workspace.ref.child("meters").child(identifier.meter_id)
        if meter_ref.get() is None:
            raise HTTPException(
                status_code=404,
                detail=f"No existe el medidor con ID: {identifier.meter_id}",
            )
        return meter_ref

    def _get_records(
        self, meter_ref: db.Reference, params: SensorQueryParams
    ) -> dict[str, Any]:
        data = (
            meter_ref.child("sensors").order_by_key().limit_to_last(params.limit).get()
            or {}
        )

        if not data:
            return data
        items = list(data.items())
        result = items[::-1]
        return dict(result)

    def _get_records_by_index(
        self, meter_ref: db.Reference, params: SensorQueryParams
    ) -> dict[str, Any]:
        snapshot = (
            meter_ref.child("sensors")
            .order_by_key()
            .end_at(params.index)
            .limit_to_last(params.limit + 1)
            .get()
            or {}
        )
        if not snapshot:
            return snapshot
        items = list(snapshot.items())
        filtered = [item for item in items if item[0] != params.index]
        result = filtered[::-1]
        return dict(result)

    def _convert_to_timestamp(self, date_str: str) -> int:
        """Convert date string in format 'YYYY-MM-DD HH:MM:SS' to timestamp in milliseconds."""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except (ValueError, TypeError):
            return None

    def _process_records(
        self, records_data: dict, index: str = None, sensor_type_filter: str = None
    ) -> SensorRecordsResponse:
        """Process raw records data into SensorRecordsResponse with optional type filtering."""
        sensor_records_by_type = {
            "color": [],
            "conductivity": [],
            "ph": [],
            "temperature": [],
            "tds": [],
            "turbidity": [],
        }

        if not records_data:
            return SensorRecordsResponse(**sensor_records_by_type)

        # Convert to dict and reverse to get most recent first
        records: dict[str, dict] = dict(reversed(list(records_data.items())))

        for key, data in records.items():
            try:
                timestamp = int(key)
            except ValueError:
                continue

            if index is not None and timestamp == int(index):
                continue

            for sensor_type, record in data.items():
                # Skip if we're filtering by sensor type and this isn't it
                if sensor_type_filter and sensor_type != sensor_type_filter:
                    continue

                if sensor_type in sensor_records_by_type:
                    if sensor_type == "color":
                        sensor_records_by_type[sensor_type].append(
                            Record[SRColorValue](
                                id=key,
                                datetime=datetime.fromisoformat(record["datetime"]),
                                value=SRColorValue(**record["value"]),
                            )
                        )
                    else:
                        sensor_records_by_type[sensor_type].append(
                            Record[float](
                                id=key,
                                datetime=datetime.fromisoformat(record["datetime"]),
                                value=record["value"],
                            )
                        )

        return SensorRecordsResponse(**sensor_records_by_type)

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
        meter_ref = self._get_meter(identifier)
        sensors_ref = meter_ref.child("sensors").order_by_key()

        if params.index is not None:
            sensors_ref = sensors_ref.limit_to_last(params.limit)

        # Convert date strings to timestamps
        start_timestamp = (
            self._convert_to_timestamp(params.start_date) if params.start_date else None
        )
        end_timestamp = (
            self._convert_to_timestamp(params.end_date) if params.end_date else None
        )

        print("start_timestamp", start_timestamp)
        print("end_timestamp", end_timestamp)

        # Build the query
        if start_timestamp is not None:
            sensors_ref = sensors_ref.start_at(str(start_timestamp))
        if end_timestamp is not None:
            sensors_ref = sensors_ref.end_at(str(end_timestamp))

        if params.index is not None:
            sensors_ref = sensors_ref.end_at(params.index)

        limit = params.limit if params.index is None else params.limit + 1
        # Get the records and apply limit
        records_data = sensors_ref.limit_to_last(limit).get() or {}

        # Process and filter the records
        return self._process_records(records_data, params.index, params.sensor_type)
