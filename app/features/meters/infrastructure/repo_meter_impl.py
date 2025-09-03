from fastapi import HTTPException
from firebase_admin import db
from app.features.meters.domain.model import (
    SensorStatus,
    WQMeter,
    WQMeterUpdate,
    WaterQualityMeter,
    WQMeterCreate,
)
from app.features.meters.domain.repository import WaterQualityMeterRepository
from app.share.socketio.domain.enum.meter_connection_state import MeterConnectionState
from app.share.workspace.domain.model import WorkspaceRoles, WorkspaceRolesAll
from app.share.workspace.workspace_access import WorkspaceAccess


class WaterQualityMeterRepositoryImpl(WaterQualityMeterRepository):
    def __init__(self, access: WorkspaceAccess):
        self.access = access

    def add(
        self, id_workspace: str, owner: str, water_quality_meter: WQMeterCreate
    ) -> WaterQualityMeter:

        workspace_ref = self.access.get_ref(
            id_workspace,
            owner,
            roles=[WorkspaceRoles.MANAGER, WorkspaceRoles.ADMINISTRATOR],
        )

        new_meter = WQMeter(
            name=water_quality_meter.name,
            location=water_quality_meter.location,
        )

        new_meter_ref = workspace_ref.ref.child("meters").push(new_meter.model_dump())

        return WaterQualityMeter(
            id=new_meter_ref.key,
            name=new_meter.name,
            location=new_meter.location,
            rol=workspace_ref.rol,
        )

    def get_list(self, id_workspace: str, owner: str) -> list[WaterQualityMeter]:

        workspace_ref = self.access.get_ref(
            id_workspace,
            owner,
            roles=[
                WorkspaceRoles.ADMINISTRATOR,
                WorkspaceRoles.MANAGER,
                WorkspaceRoles.VISITOR,
            ],
            is_public=True,
        )

        meters = []

        workspace_meters = workspace_ref.ref.child("meters")

        if workspace_meters.get() is None:
            return []

        for meter_id, data in workspace_meters.get().items():
            meter = WaterQualityMeter(
                id=meter_id,
                name=data["name"],
                location=data["location"],
                state=(
                    data["state"]
                    if "state" in data
                    else MeterConnectionState.DISCONNECTED
                ),
                rol=workspace_ref.rol,
            )
            meters.append(meter)

        return meters

    def _get_meter_ref(
        self,
        id_workspace: str,
        owner: str,
        id_meter: str,
        roles: list[WorkspaceRoles],
        is_public: bool = False,
    ) -> tuple[db.Reference, WorkspaceRoles | WorkspaceRolesAll]:
        workspace_ref = self.access.get_ref(
            id_workspace, owner, roles=roles, is_public=is_public
        )

        meter_ref = workspace_ref.ref.child("meters").child(id_meter)

        if meter_ref.get() is None:
            raise HTTPException(status_code=404, detail="No existe el medidor")

        return meter_ref, workspace_ref.rol

    def get(self, id_workspace: str, owner: str, id_meter: str) -> WaterQualityMeter:
        meter_ref, rol = self._get_meter_ref(
            id_workspace,
            owner,
            id_meter,
            roles=[
                WorkspaceRoles.ADMINISTRATOR,
                WorkspaceRoles.MANAGER,
                WorkspaceRoles.VISITOR,
            ],
            is_public=True,
        )

        meter: dict = meter_ref.get()

        return WaterQualityMeter(
            id=meter_ref.key,
            name=meter.get("name"),
            location=meter.get("location"),
            state=meter.get("state", MeterConnectionState.DISCONNECTED),
            rol=rol,
        )

    def delete(self, id_workspace: str, owner: str, id_meter: str) -> WaterQualityMeter:
        meter_ref, rol = self._get_meter_ref(
            id_workspace, owner, id_meter, roles=[WorkspaceRoles.ADMINISTRATOR]
        )

        meter: dict = meter_ref.get()

        if meter is None:
            raise HTTPException(status_code=404, detail="No existe el sensor")

        state = meter.get("state", MeterConnectionState.DISCONNECTED)
        if (
            state == MeterConnectionState.SENDING_DATA
            or state == MeterConnectionState.CONNECTED
        ):
            raise HTTPException(status_code=400, detail="El sensor está enviando datos")

        meter_ref.delete()
        return WaterQualityMeter(
            id=meter_ref.key,
            name=meter.get("name"),
            location=meter.get("location"),
            state=meter.get("state", MeterConnectionState.DISCONNECTED),
            rol=rol,
        )

    def update(
        self, id_workspace: str, owner: str, id_meter: str, meter: WQMeterUpdate
    ) -> WaterQualityMeter:

        meter_ref, rol = self._get_meter_ref(
            id_workspace,
            owner,
            id_meter,
            roles=[WorkspaceRoles.ADMINISTRATOR, WorkspaceRoles.MANAGER],
        )

        meter_data: dict = meter_ref.get()

        if meter_data is None:
            raise HTTPException(status_code=404, detail="No existe el sensor")

        state = meter_data.get("state", MeterConnectionState.DISCONNECTED)
        if (
            state == MeterConnectionState.SENDING_DATA
            or state == MeterConnectionState.CONNECTED
        ):
            raise HTTPException(status_code=400, detail="El sensor está enviando datos")

        meter_ref.update(meter.model_dump())

        meter_update: dict = meter_ref.get()

        return WaterQualityMeter(
            id=meter_ref.key,
            name=meter_update.get("name"),
            location=meter_update.get("location"),
            state=meter_update.get("state", MeterConnectionState.DISCONNECTED),
            rol=rol,
        )

    def is_active(self, id_workspace: str, owner: str, id_meter: str) -> bool:
        workspace_ref = self.get(id_workspace, owner, id_meter)

        return (
            workspace_ref.state == MeterConnectionState.CONNECTED
            or workspace_ref.state == MeterConnectionState.SENDING_DATA
        )
