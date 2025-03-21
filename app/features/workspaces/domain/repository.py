from abc import ABC, abstractmethod
from .model import WorkspaceCreate, WorkspaceResponse

class WorkspaceRepository(ABC):
    
    @abstractmethod
    def get_per_user(self, owner: str)-> list[WorkspaceResponse]:
        pass
    
    @abstractmethod
    def get_by_id(self, id: str)-> WorkspaceResponse:
        pass
    @abstractmethod
    def create(self, workspace: WorkspaceCreate)-> WorkspaceResponse:
        pass
    
    @abstractmethod
    def update(self, id: str, workspace: WorkspaceCreate)-> WorkspaceResponse:
        pass
    @abstractmethod
    def delete(self, id: str)-> bool:
        pass
    