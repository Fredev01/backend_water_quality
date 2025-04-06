from firebase_admin import db
from app.features.meters.domain.model import SensorIdentifier, SensorQueryParams, SensorRecord, SensorRecordsResponse
from app.features.meters.domain.repository import MeterRecordsRepository
from app.share.socketio.domain.model import Record, SRColorValue


class MeterRecordsRepositoryImpl(MeterRecordsRepository):
    def get_10_last_sensor_records(
    self, 
    workspace_id: str, 
    meter_id: str
    ) -> SensorRecordsResponse:
    # Obtener la referencia a la base de datos
        workspaces_ref = db.reference().child('workspaces')
        workspace = workspaces_ref.child(workspace_id)

        if workspace.get() is None:
            raise ValueError(f"No existe workspace con ID: {workspace_id}")

        meter_ref = workspace.child('meters').child(meter_id).get()
        if meter_ref is None:
            raise ValueError(f"No existe el medidor con ID: {meter_id}")
        sensor_data = meter_ref.get('sensors')
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
        
        base_ref = workspace.child('meters').child(meter_id).child('sensors')
        
        for sensor_type in sensor_records_by_type.keys():
            sensor_ref = base_ref.child(sensor_type)
            records = sensor_ref.order_by_child("timestamp").limit_to_last(10).get() or {}
            print(records)

            if records is None:
                continue

            for record in records.values():
                if sensor_type == "color":
                    sensor_records_by_type["color"].append(Record[SRColorValue](**record))
                else:
                    sensor_records_by_type[sensor_type].append(Record[float](**record))

        # Devolver la respuesta con los registros agrupados por tipo de sensor
        return SensorRecordsResponse(**sensor_records_by_type)

    
    def get_sensor_records(
        self, 
        identifier: SensorIdentifier,
        params: SensorQueryParams | None = None
    ) -> list[SensorRecord]:
        pass
    
    