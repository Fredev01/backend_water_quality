from firebase_admin import db
class WorkspaceAuthorizationServiceImpl:
    def check_user_access(self, workspace_id: str, user_id: str) -> bool:
        """Check if the user has access to the workspace."""
        workspace_ref = db.reference("workspaces")
        workspace_data = workspace_ref.child(workspace_id).get()
        if workspace_data is None:
            raise ValueError(f"Workspace with ID {workspace_id} does not exist.")
        return workspace_data.get("owner") == user_id or any(user_id == g.get("email") for g in workspace_data.get("guests", {}).values())
    
    def get_user_role(self, workspace_id: str, user_id: str) -> str:
        pass
    
    def can_access_meter(self, workspace_id: str, meter_id: str, user_id: str) -> bool:
        pass