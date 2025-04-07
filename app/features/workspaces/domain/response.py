from app.features.workspaces.domain.model import GuestResponse, WorkspacePublicResponse, WorkspaceShareResponse
from app.share.response.model import ResponseApi


class ResponseWorkspacesShares(ResponseApi):
    workspaces: list[WorkspaceShareResponse]


class ResponseWorkspacePublic(ResponseApi):
    workspace: WorkspacePublicResponse


class ResponseGuests(ResponseApi):
    guests: list[GuestResponse]


class ResponseGuest(ResponseApi):
    guest: GuestResponse
