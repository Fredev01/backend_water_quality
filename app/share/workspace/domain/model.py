from enum import Enum
from firebase_admin.db import Reference

from app.share.users.domain.model.user import UserData


class WorkspaceRoles(str, Enum):
    VISITOR = "visitor"
    MANAGER = "manager"
    ADMINISTRATOR = "administrator"


class WorkspaceRolesAll(str, Enum):
    OWNER = "owner"
    UNKNOWN = "unknown"


class WorkspaceType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class WorkspaceRef:
    ref: Reference
    user: UserData | None
    rol: WorkspaceRoles | WorkspaceRolesAll

    def __init__(
        self,
        ref: Reference,
        user: UserData | None = None,
        rol: WorkspaceRoles = WorkspaceRolesAll.UNKNOWN,
    ):
        self.ref = ref
        self.user = user
        self.rol = rol


class WorkspaceGuest:
    is_guest: bool
    rol: WorkspaceRoles | WorkspaceRolesAll = WorkspaceRolesAll.UNKNOWN

    def __init__(self, is_guest: bool, rol: WorkspaceRoles = WorkspaceRolesAll.UNKNOWN):
        self.is_guest = is_guest
        self.rol = rol
