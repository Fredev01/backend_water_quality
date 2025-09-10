from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from app.features.workspaces.domain.repository import WorkspaceRepository
from app.features.workspaces.domain.workspace_share_repo import WorkspaceGuestRepository
from app.features.workspaces.infrastructure.repo_impl import WorkspaceRepositoryImpl
from app.features.workspaces.infrastructure.repo_share_impl import (
    WorkspaceGuestRepositoryImpl,
)
from app.share.depends import get_user_repo, get_workspace_access
from app.share.email.domain.repo import EmailRepository
from app.share.email.service.resend_email import ResendEmailService
from app.share.users.domain.repository import UserRepository
from app.share.workspace.workspace_access import WorkspaceAccess


@lru_cache()
def get_workspace_repo(
    workspace_access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> WorkspaceRepository:

    return WorkspaceRepositoryImpl(access=workspace_access, user_repo=user_repo)


@lru_cache()
def get_workspace_guest_repo(
    workspace_access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> WorkspaceGuestRepository:
    return WorkspaceGuestRepositoryImpl(access=workspace_access, user_repo=user_repo)
