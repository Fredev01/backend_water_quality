from datetime import datetime
from firebase_admin import db
from app.features.meters.domain.model import SensorIdentifier, SensorQueryParams,RecordDatetime, SensorRecordsResponse
from app.features.meters.domain.repository import MeterRecordsRepository
from app.share.socketio.domain.model import Record, SRColorValue


class MeterRecordsRepositoryImpl(MeterRecordsRepository):
    def get_10_last_sensor_records(self, workspace_id: str, meter_id: str) -> SensorRecordsResponse:
        meter_ref = self._get_meter(workspace_id, meter_id)
        meter_data = meter_ref.get()
        sensor_data = meter_data.get('sensors')
        if sensor_data is None:
            raise ValueError(f"No existen sensores para el medidor con ID: {meter_id}")

        sensor_records_by_type = {
            "color": [],
            "conductivity": [],
            "ph": [],
            "temperature": [],
            "tds": [],
            "turbidity": []
        }

        base_ref = meter_ref.child('sensors')
        for sensor_type in sensor_records_by_type.keys():
            sensor_ref = base_ref.child(sensor_type)
            records = sensor_ref.order_by_child("timestamp").limit_to_last(10).get() or {}
            if not records:
                continue

            for record in records.values():
                if sensor_type == "color":
                    sensor_records_by_type["color"].append(Record[SRColorValue](**record))
                else:
                    sensor_records_by_type[sensor_type].append(Record[float](**record))

        return SensorRecordsResponse(**sensor_records_by_type)

    def get_sensor_records(
        self, 
        identifier: SensorIdentifier,
        params: SensorQueryParams | None = None
    ) -> list[Record | RecordDatetime]:
        meter_ref = self._get_meter(identifier.workspace_id, identifier.meter_id)
        if meter_ref.get() is None:
            raise ValueError(f"No existe el medidor: {identifier.meter_id}")

        sensor_ref = meter_ref.child('sensors').child(identifier.sensor_name)
        if sensor_ref.get() is None:
            raise ValueError(f"No existe el sensor: {identifier.sensor_name}")

        records = self._get_records(sensor_ref, params)
        if not records:
            raise ValueError(f"No existen registros para el sensor: {identifier.sensor_name}")

        if params.convert_timestamp:
            if identifier.sensor_name == "color":
                return [
                    RecordDatetime[SRColorValue](
                        value=record['value'],
                        datetime=self._convert_timestamp_to_datetime(record.get('timestamp'))
                    )
                    for record in records.values()
                ]
            else:
                return [
                    RecordDatetime[float](
                        value=record['value'],
                        datetime=self._convert_timestamp_to_datetime(record.get('timestamp'))
                    )
                    for record in records.values()
                ]
        else:
            if identifier.sensor_name == "color":
                return [Record[SRColorValue](**record) for record in records.values()]
            else:
                return [Record[float](**record) for record in records.values()]

    def _get_workspace(self, workspace_id: str):
        workspaces_ref = db.reference().child('workspaces')
        workspace = workspaces_ref.child(workspace_id)
        if workspace.get() is None:
            raise ValueError(f"No existe workspace con ID: {workspace_id}")
        return workspace
    
    def _get_meter(self, workspace_id: str, meter_id: str):
        workspace = self._get_workspace(workspace_id)
        meter_ref = workspace.child('meters').child(meter_id)
        if meter_ref.get() is None:
            raise ValueError(f"No existe el medidor con ID: {meter_id}")
        return meter_ref

    def _get_records(self, sensor_ref, params: SensorQueryParams) -> dict:
        if params.descending:
            return sensor_ref.order_by_child("timestamp").limit_to_last(params.limit).get() or {}
        else:
            return sensor_ref.order_by_child("timestamp").limit_to_first(params.limit).get() or {}

    def _convert_timestamp_to_datetime(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
