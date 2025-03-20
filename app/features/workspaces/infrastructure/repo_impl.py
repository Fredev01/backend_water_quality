from app.features.workspaces.domain.repository import WorkspaceRepository
from firebase_admin import db
from app.features.workspaces.domain.model import Workspace, WorkspaceResponse

from typing import Optional, List


class WorkspaceRepositoryImpl(WorkspaceRepository):
    def __init__(self):
        pass
    
    def get_per_user(self, owner: str) -> List[WorkspaceResponse]:
        """Obtiene todos los workspaces pertenecientes a un usuario."""
        workspaces_ref = db.reference().child('workspaces')
        workspaces_query = workspaces_ref.order_by_child('owner').equal_to(owner).get() or {}
    
        workspaces = []
        for workspace_id, data in workspaces_query.items():
            workspace = WorkspaceResponse(
            id=workspace_id,
            name=data['name'],
            owner=data['owner']
            )
            workspaces.append(workspace)
        return workspaces
    
    def get_by_id(self, id: str) -> WorkspaceResponse:
        """Obtiene un workspace por su ID."""
        workspaces_ref = db.reference().child('workspaces')
        workspace_data = workspaces_ref.child(id).get()
    
        if workspace_data is None:
            raise ValueError(f"No existe workspace con ID: {id}")
    
        return WorkspaceResponse(
        id=id,
        name=workspace_data.get('name'),
        owner=workspace_data.get('owner')
        )
    
    def create(self, workspace: Workspace) -> WorkspaceResponse:
        """Crea un nuevo workspace."""
        workspaces_ref = db.reference().child('workspaces')
        workspace_dict = workspace.model_dump()
        new_workspace_ref = workspaces_ref.push(workspace_dict)
        return WorkspaceResponse(
            id=new_workspace_ref.key,
            **workspace_dict
        )
    
    def delete(self, id: str) -> bool:
        """Elimina un workspace por su ID."""
        workspaces_ref = db.reference().child('workspaces')
        try:
            workspace_ref = workspaces_ref.child(id)
            if workspace_ref.get() is None:
                return False
            
            workspace_ref.delete()
            return True
        except Exception:
            return False
    
    def update(self, id: str, workspace: Workspace)-> WorkspaceResponse:
        """Actualiza un workspace existente."""
        workspaces_ref = db.reference().child('workspaces')
        workspace_ref = workspaces_ref.child(id)
        current_data = workspace_ref.get()
        if current_data is None:
            raise ValueError(f"No existe workspace con ID: {id}")
        update_data = {k: v for k, v in workspace.model_dump().items() if v is not None}
        if not update_data:
            return WorkspaceResponse(id=id, **current_data)
        workspace_ref.update(update_data)
        updated_data = workspace_ref.get()
        return WorkspaceResponse(
            id=id,
            name=updated_data.get('name'),
            owner=updated_data.get('owner')
        )