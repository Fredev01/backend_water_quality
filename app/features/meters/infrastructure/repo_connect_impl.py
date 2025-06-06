from app.features.meters.domain.model import MeterConnection, SensorStatus
from app.features.meters.domain.repository import WaterQMConnection, WaterQualityMeterRepository
from firebase_admin import db
import random


class WaterQMConnectionImpl(WaterQMConnection):

    def __init__(self, meter_repo: WaterQualityMeterRepository):
        self.meter_repo = meter_repo

    def _query_by(self, type: str, value: str | int):
        connection_ref = db.reference().child('connections')

        connection_query = connection_ref.order_by_child(
            type).equal_to(value)

        return connection_query.get() or {}

    def get_by_password(self, password: int) -> MeterConnection | None:
        connection_query = self._query_by(type='password', value=password)

        connections = []
        for connection_id, data in connection_query.items():
            connection = MeterConnection(
                id=connection_id,
                id_workspace=data['id_workspace'],
                owner=data['owner'],
                id_meter=data['id_meter']
            )
            connections.append(connection)

        if len(connections) == 0:
            return None

        return connections[0]

    def get_by_id_meter(self,  id_meter: str) -> MeterConnection | None:
        connection_query = self._query_by(type='id_meter', value=id_meter)

        connections = []
        for connection_id, data in connection_query.items():
            connection = MeterConnection(
                id=connection_id,
                id_workspace=data['id_workspace'],
                owner=data['owner'],
                id_meter=data['id_meter']
            )
            connections.append(connection)

        if len(connections) == 0:
            return None

        return connections[0]

    def create(self, id_workspace: str, owner: str, id_meter: str) -> int:

        if self.get_by_id_meter(id_meter) is not None:
            raise ValueError("La conexión ya existe")

        if self.meter_repo.is_active(id_workspace, owner, id_meter) is True:
            raise ValueError("El sensor ya esta activo")

        password = random.randint(100000, 999999)

        db.reference().child('connections').push({
            'id_workspace': id_workspace,
            'owner': owner,
            'id_meter': id_meter,
            'password': password
        })

        return password

    def receive(self, password: int) -> MeterConnection | None:
        meter = self.get_by_password(password)

        if meter is None:
            return None

        return meter

    def delete(self, id) -> bool:
        ref = db.reference().child('connections').child(id)
        return ref.delete()
