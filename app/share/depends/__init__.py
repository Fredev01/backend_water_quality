from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from app.share.email.infra.html_template import HtmlTemplate
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
