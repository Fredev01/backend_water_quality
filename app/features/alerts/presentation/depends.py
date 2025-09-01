from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from app.features.alerts.domain.repo import AlertRepository

from app.features.alerts.infrastructure.repo_impl import AlertRepositoryImpl
from app.share.depends import get_workspace_access
from app.share.workspace.workspace_access import WorkspaceAccess


@lru_cache()
def get_alerts_repo(
    workspace_access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
) -> AlertRepository:
    return AlertRepositoryImpl(access=workspace_access)
