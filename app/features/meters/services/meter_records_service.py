from app.features.meters.domain.model import SensorIdentifier, SensorQueryParams
from app.features.meters.domain.repository import MeterRecordsRepository
from app.features.workspaces.domain.services import WorkspaceAuthorizationService
from app.share.socketio.domain.model import Record


class MeterRecordsService:
    def __init__(self, repository: MeterRecordsRepository, auth_service: WorkspaceAuthorizationService):
        self.repository = repository
        self.auth_service = auth_service
    
    def get_10_last_sensor_records(self, identifier: SensorIdentifier):
        has_access = self.auth_service.check_user_access(
            identifier.workspace_id, 
            identifier.user_id
        )
        
        if not has_access:
            raise ValueError("meter not found")
        
        # Obtener datos
        return self.repository.get_10_last_sensor_records(identifier.workspace_id, identifier.meter_id)
    
    def get_sensor_records(self, identifier: SensorIdentifier, params: SensorQueryParams | None = None)->list[Record]:
        has_access = self.auth_service.check_user_access(
            identifier.workspace_id, 
            identifier.user_id
        )
        
        if not has_access:
            raise ValueError("meter not found")
        return self.repository.get_sensor_records(identifier, params)