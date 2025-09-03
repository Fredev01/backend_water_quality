from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from app.share.email.infra.html_template import HtmlTemplate
from app.share.meter_records.domain.repository import (
    MeterRecordsRepository,
)
from app.share.meter_records.infrastructure.meter_records_impl import (
    MeterRecordsRepositoryImpl,
)
from app.share.users.domain.repository import UserRepository
from app.share.users.infra.users_repo_impl import UserRepositoryImpl
from app.share.workspace.workspace_access import WorkspaceAccess


@lru_cache()
def get_html_template() -> HtmlTemplate:
    return HtmlTemplate()


@lru_cache()
def get_user_repo() -> UserRepository:
    return UserRepositoryImpl()


@lru_cache()
def get_workspace_access(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> WorkspaceAccess:

    return WorkspaceAccess(user_repo=user_repo)


@lru_cache()
def get_meter_records_repo(
    workspace_access: Annotated[WorkspaceAccess, Depends(get_workspace_access)],
) -> MeterRecordsRepository:

    return MeterRecordsRepositoryImpl(workspace_access=workspace_access)
