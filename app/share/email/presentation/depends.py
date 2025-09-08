from functools import lru_cache
from app.share.email.domain.repo import EmailRepository
from app.share.email.infra.html_template import HtmlTemplate
from app.share.email.service.resend_email import ResendEmailService


@lru_cache()
def get_html_template() -> HtmlTemplate:
    return HtmlTemplate()


@lru_cache()
def get_sender() -> EmailRepository:
    return ResendEmailService()
