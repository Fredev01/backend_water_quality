from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from app.features.workspaces.domain.repository import WorkspaceRepository
from app.features.workspaces.domain.workspace_share_repo import WorkspaceGuestRepository
from app.features.workspaces.infrastructure.repo_impl import WorkspaceRepositoryImpl
from app.features.workspaces.infrastructure.repo_share_impl import WorkspaceGuestRepositoryImpl
from app.share.users.domain.repository import UserRepository
from app.share.users.infra.users_repo_impl import UserRepositoryImpl
from app.share.workspace.workspace_access import WorkspaceAccess


"""
user_repo = UserRepositoryImpl()
workspace_access = WorkspaceAccess(user_repo=user_repo)

workspace_repo = WorkspaceRepositoryImpl(
    access=workspace_access, user_repo=user_repo)

workspace_guest_repo = WorkspaceGuestRepositoryImpl(
    access=workspace_access, user_repo=user_repo)
    
"""


@lru_cache()
def get_user_repo() -> UserRepository:
    return UserRepositoryImpl()


@lru_cache()
def get_workspace_access(user_repo: Annotated[UserRepository, Depends(get_user_repo)]) -> WorkspaceAccess:

    return WorkspaceAccess(user_repo=user_repo)


@lru_cache()
def get_workspace_repo(
    workspace_access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)]
) -> WorkspaceRepository:

    return WorkspaceRepositoryImpl(
        access=workspace_access,
        user_repo=user_repo
    )


@lru_cache()
def get_workspace_guest_repo(
    workspace_access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)]
) -> WorkspaceGuestRepository:
    return WorkspaceGuestRepositoryImpl(
        access=workspace_access, user_repo=user_repo)
