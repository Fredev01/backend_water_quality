from app.features.workspaces.domain.model import (
    GuestResponse,
    WorkspacePublicResponse,
    WorkspaceShareResponse,
    WorkspaceResponse,
)
from app.share.response.model import ResponseApi


class ResponseWorkspacesShares(ResponseApi):
    workspaces: list[WorkspaceShareResponse]


class ResponseWorkspacePublic(ResponseApi):
    workspaces: list[WorkspacePublicResponse]


class ResponseGuests(ResponseApi):
    guests: list[GuestResponse]


class ResponseGuest(ResponseApi):
    guest: GuestResponse


# New response models for CRUD operations
class WorkspacesResponse(ResponseApi):
    data: list[WorkspaceResponse]


class WorkspacesAllResponse(ResponseApi):
    workspaces: list[WorkspaceResponse]


class WorkspaceDataResponse(ResponseApi):
    data: WorkspaceResponse


class WorkspaceDeleteResponse(ResponseApi):
    pass
