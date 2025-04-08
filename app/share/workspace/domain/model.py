from enum import Enum


class WorkspaceRoles(str, Enum):
    VISITOR = "visitor"
    MANAGER = "manager"
    ADMINISTRATOR = "administrator"


class WorkspaceType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
