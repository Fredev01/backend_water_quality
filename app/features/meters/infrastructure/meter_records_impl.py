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
        meter_data = meter_ref.get()
        sensor_data = meter_data.get("sensors")
        sensor_records_by_type = {
            "color": [],
            "conductivity": [],
            "ph": [],
            "temperature": [],
            "tds": [],
            "turbidity": [],
        }
        if sensor_data is None:
            return SensorRecordsResponse(**sensor_records_by_type)

        base_ref = meter_ref.child("sensors")
        for sensor_type in sensor_records_by_type.keys():
            sensor_ref = base_ref.child(sensor_type)
            records = (
                sensor_ref.order_by_child("datetime").limit_to_last(params.limit).get()
                or {}
            )
            if not records:
                continue

            for key, record in records.items():
                if sensor_type == "color":
                    sensor_records_by_type["color"].append(
                        Record[SRColorValue](id=key, **record)
                    )
                else:
                    sensor_records_by_type[sensor_type].append(
                        Record[float](id=key, **record)
                    )

        return SensorRecordsResponse(**sensor_records_by_type)

    def get_sensor_records(
        self, identifier: SensorIdentifier, params: SensorQueryParams
    ) -> list[Record]:
        meter_ref = self._get_meter(identifier)
        if meter_ref.get() is None:
            raise HTTPException(
                status_code=404,
                detail=f"No existe el medidor con ID: {identifier.meter_id}",
            )

        sensor_ref = meter_ref.child("sensors").child(identifier.sensor_name)
        if sensor_ref.get() is None:
            raise HTTPException(
                status_code=404, detail=f"No existe el sensor: {identifier.sensor_name}"
            )

        records = None
        if params.index is None:
            records = self._get_records(sensor_ref, params)
        else:
            records = self._get_records_by_index(sensor_ref, params)
        if not records:
            raise ValueError(
                f"No existen registros para el sensor: {identifier.sensor_name}"
            )

        if identifier.sensor_name == "color":
            return [
                Record[SRColorValue](id=key, **record)
                for key, record in records.items()
            ]
        else:
            return [Record[float](id=key, **record) for key, record in records.items()]

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
        self, sensor_ref: db.Reference, params: SensorQueryParams
    ) -> dict[str, Any] | list[Any]:
        data = (
            sensor_ref.order_by_child("datetime").limit_to_last(params.limit).get()
            or {}
        )
        if not data:
            return data
        items = list(data.items())
        result = items[::-1]
        return dict(result)

    def _get_records_by_index(
        self, sensor_ref: db.Reference, params: SensorQueryParams
    ) -> dict[str, Any] | list[Any]:
        snapshot = (
            sensor_ref.order_by_key()
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
