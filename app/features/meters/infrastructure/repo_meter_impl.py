from fastapi import HTTPException
from firebase_admin import db
from app.features.meters.domain.model import SensorStatus, WQMeter, WQMeterUpdate, WaterQualityMeter, WQMeterCreate, WaterQualityMeterSensor
from app.features.meters.domain.repository import WaterQualityMeterRepository


class WaterQualityMeterRepositoryImpl(WaterQualityMeterRepository):
    def add(self,  id_workspace: str, owner: str, water_quality_meter: WQMeterCreate) -> WaterQualityMeter:

        workspaces_ref = db.reference().child('workspaces')

        workspace = workspaces_ref.child(id_workspace)

        if workspace.get() is None or workspace.get().get('owner') != owner:
            raise ValueError(f"No existe workspace con ID: {id_workspace}")

        new_meter = WQMeter(
            name=water_quality_meter.name,
            location=water_quality_meter.location,
        )

        new_meter_ref = workspace.child('meters').push(new_meter.model_dump())

        return WaterQualityMeter(
            id=new_meter_ref.key,
            name=new_meter.name,
            status=new_meter.status,
            location=new_meter.location
        )

    def get_list(self, id_workspace: str, owner: str) -> list[WaterQualityMeter]:

        workspaces_ref = db.reference().child('workspaces')

        workspace = workspaces_ref.child(id_workspace)

        if workspace.get() is None or workspace.get().get('owner') != owner:
            raise ValueError(f"No existe workspace con ID: {id_workspace}")

        meters = []

        workspace_meters = workspace.child('meters')

        if workspace_meters.get() is None:
            return []

        for meter_id, data in workspace_meters.get().items():
            meter = WaterQualityMeter(
                id=meter_id,
                name=data['name'],
                status=data['status'],
                location=data['location']
            )
            meters.append(meter)

        return meters

    def _get_meter_ref(self, id_workspace: str, owner: str, id_meter: str) -> db.Reference:
        workspaces_ref = db.reference().child('workspaces')

        workspace = workspaces_ref.child(id_workspace)

        if workspace.get() is None or workspace.get().get('owner') != owner:
            raise HTTPException(
                status_code=404, detail=f"No existe workspace con ID: {id_workspace}")

        meter_ref = workspace.child('meters').child(id_meter)

        if meter_ref.get() is None:
            raise HTTPException(status_code=404, detail="No existe el sensor")

        return meter_ref

    def get_details(self, id_workspace: str, owner: str, id_meter: str) -> WaterQualityMeterSensor:
        pass

    def is_active(self, id_workspace: str, owner: str, id_meter: str) -> bool:

        meter_ref = self._get_meter_ref(id_workspace, owner, id_meter)

        if meter_ref.get() is None:
            return False

        return meter_ref.get().get('status') == SensorStatus.ACTIVE

    def delete(self, id_workspace: str, owner: str, id_meter: str) -> WaterQualityMeter:
        meter_ref = self._get_meter_ref(id_workspace, owner, id_meter)

        meter = meter_ref.get()

        if meter is None:
            raise HTTPException(status_code=404, detail="No existe el sensor")

        if meter.get('status') == SensorStatus.ACTIVE:
            raise HTTPException(
                status_code=400, detail="El sensor está activo")

        meter_ref.delete()
        return WaterQualityMeter(
            id=meter_ref.key,
            name=meter.get('name'),
            status=meter.get('status'),
            location=meter.get('location')
        )

    def update(self, id_workspace: str, owner: str, id_meter: str, meter: WQMeterUpdate) -> WaterQualityMeter:

        meter_ref = self._get_meter_ref(id_workspace, owner, id_meter)

        if meter_ref.get() is None:
            raise HTTPException(status_code=404, detail="No existe el sensor")

        meter_ref.update(meter.model_dump())

        meter_update = meter_ref.get()

        return WaterQualityMeter(
            id=meter_ref.key,
            name=meter_update["name"],
            location=meter_update["location"],
            status=meter_update["status"],

        )
