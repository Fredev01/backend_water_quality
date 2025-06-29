from app.share.jwt.domain.payload import MeterPayload
from app.share.socketio.domain.model import Record, RecordBody, RecordResponse, SRColorValue
from app.share.socketio.domain.repository import RecordRepository
from firebase_admin import db
from datetime import datetime


class RecordRepositoryImpl(RecordRepository):

    def _add_in_sensor(self, sensor_ref: db.Reference, sensor_name: str, value: Record):
        sensor_ref.child(sensor_name).push(value.model_dump())

    def add(self, meter_connection: MeterPayload, body: RecordBody) -> RecordResponse:
        workspace_ref = db.reference("workspaces").child(
            meter_connection.id_workspace)

        workspace = workspace_ref.get()

        if workspace is None or workspace.get('owner') != meter_connection.owner:
            raise Exception(
                f"No existe workspace con ID: {meter_connection.id_workspace}")

        meter_ref = workspace_ref.child(
            "meters").child(meter_connection.id_meter)

        meter = meter_ref.get()
        if meter is None:
            raise Exception(f"No existe el sensor")

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sensors_ref = meter_ref.child("sensors")

        color_record = Record[SRColorValue](
            value=body.color, datetime=current_datetime)
        conductivity_record = Record[float](
            value=body.conductivity, datetime=current_datetime)
        ph_record = Record[float](value=body.ph, datetime=current_datetime)
        temperature_record = Record[float](
            value=body.temperature, datetime=current_datetime)
        tds_record = Record[float](value=body.tds, datetime=current_datetime)
        turbidity_record = Record[float](
            value=body.turbidity, datetime=current_datetime)

        self._add_in_sensor(sensors_ref, "color", color_record)
        self._add_in_sensor(sensors_ref, "conductivity", conductivity_record)
        self._add_in_sensor(sensors_ref, "ph", ph_record)
        self._add_in_sensor(sensors_ref, "temperature", temperature_record)
        self._add_in_sensor(sensors_ref, "tds", tds_record)
        self._add_in_sensor(sensors_ref, "turbidity", turbidity_record)

        return RecordResponse(
            color=color_record,
            conductivity=conductivity_record,
            ph=ph_record,
            temperature=temperature_record,
            tds=tds_record,
            turbidity=turbidity_record
        )
