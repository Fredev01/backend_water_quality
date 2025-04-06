from abc import ABC, abstractmethod

class WorkspaceAuthorizationService(ABC):
    @abstractmethod
    def check_user_access(self, workspace_id: str, user_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_user_role(self, workspace_id: str, user_id: str) -> str:
        pass
    
    @abstractmethod
    def can_access_meter(self, workspace_id: str, meter_id: str, user_id: str) -> bool:
        pass