from firebase_admin import db
from app.features.meters.domain.model import SensorStatus, WQMeter, WaterQualityMeter, WQMeterCreate, WaterQualityMeterSensor
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

    def get_details(self, id_workspace: str, owner: str, id_meter: str) -> WaterQualityMeterSensor:
        pass

    def is_active(self, id_workspace: str, owner: str, id_meter: str) -> bool:
        workspaces_ref = db.reference().child('workspaces')

        workspace = workspaces_ref.child(id_workspace)

        if workspace.get() is None or workspace.get().get('owner') != owner:
            raise ValueError(f"No existe workspace con ID: {id_workspace}")

        meter_ref = workspace.child('meters').child(id_meter)

        if meter_ref.get() is None:
            return False

        return meter_ref.get().get('status') == SensorStatus.ACTIVE

    def delete(self, id_workspace: str, owner: str, id_meter: str) -> bool:
        pass

    def update(self, id_workspace: str, owner: str, str, id_meter: str, water_quality_meter: WaterQualityMeter) -> WaterQualityMeter:
        pass
