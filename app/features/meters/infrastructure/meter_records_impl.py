from datetime import datetime
from typing import Any
from fastapi import HTTPException
from firebase_admin import db
from app.features.meters.domain.model import (
    SensorIdentifier,
    SensorQueryParams,
    SensorRecordsResponse,
)
from app.features.meters.domain.repository import MeterRecordsRepository
from app.share.socketio.domain.model import Record, SRColorValue
from app.share.workspace.domain.model import WorkspaceRoles
from app.share.workspace.workspace_access import WorkspaceAccess


class MeterRecordsRepositoryImpl(MeterRecordsRepository):

    def __init__(self, workspace_access: WorkspaceAccess):
        self.workspace_access = workspace_access

    def get_latest_sensor_records(
        self, identifier: SensorIdentifier, params: SensorQueryParams
    ) -> SensorRecordsResponse:
        meter_ref = self._get_meter(identifier)
        sensor_records_by_type = {
            "color": [],
            "conductivity": [],
            "ph": [],
            "temperature": [],
            "tds": [],
            "turbidity": [],
        }

        # Get the latest records in a single query
        records_data = meter_ref.child("sensors")\
            .order_by_key()\
            .limit_to_last(params.limit)\
            .get()

        if not records_data:
            return SensorRecordsResponse(**sensor_records_by_type)

        # Convert to dict and reverse to get most recent first
        records: dict[str, dict] = dict(reversed(list(records_data.items())))

        for key, data in records.items():
            # convert key to int, pero si da error continuar
            try:
                timestamp = int(key)
            except ValueError:
                continue

            for sensor_type, record in data.items():
                if sensor_type == "color":
                    sensor_records_by_type[sensor_type].append(
                        Record[SRColorValue](
                            id=timestamp,
                            datetime=datetime.fromisoformat(
                                record["datetime"]),
                            value=SRColorValue(**record["value"]),
                        )
                    )
                else:
                    sensor_records_by_type[sensor_type].append(
                        Record[float](
                            id=timestamp,
                            datetime=datetime.fromisoformat(
                                record["datetime"]),
                            value=record["value"],
                        )
                    )

        return SensorRecordsResponse(**sensor_records_by_type)

    def get_sensor_records(
        self, identifier: SensorIdentifier, params: SensorQueryParams
    ) -> list[Record]:
        meter_ref = self._get_meter(identifier)

        records: dict[str, dict] = None
        if params.index is None:
            records = self._get_records(
                meter_ref, identifier.sensor_name, params)
        else:
            records = self._get_records_by_index(
                meter_ref, identifier.sensor_name, params
            )

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
                            datetime=datetime.fromisoformat(
                                sensor_data["datetime"]),
                            value=SRColorValue(**sensor_data["value"]),
                        )
                    )
                else:
                    result.append(
                        Record[float](
                            id=timestamp,
                            datetime=datetime.fromisoformat(
                                sensor_data["datetime"]),
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
        self, meter_ref: db.Reference, sensor_name: str, params: SensorQueryParams
    ) -> dict[str, Any]:
        data = (
            meter_ref.child("sensors").order_by_key(
            ).limit_to_last(params.limit).get()
            or {}
        )
        if not data:
            return data
        items = list(data.items())
        result = items[::-1]
        return dict(result)

    def _get_records_by_index(
        self, meter_ref: db.Reference, sensor_name: str, params: SensorQueryParams
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
