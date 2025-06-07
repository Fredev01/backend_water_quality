from firebase_admin import db
from app.share.socketio.domain.enum.meter_connection_state import MeterConnectionState
from app.share.socketio.domain.repository import MeterStateRepository


class MeterStateRepositoryImpl(MeterStateRepository):
    def set_state(self, id_workspace: str,  id_meter: str, state: MeterConnectionState) -> MeterConnectionState:
        meter_status = db.reference(
            f'workspaces/{id_workspace}/meters/{id_meter}/state')

        meter_status.set(state.value)
        return state
