import resend
from resend.exceptions import ApplicationError
from app.share.email.domain.config import EmailConfig
from app.share.email.domain.errors import EmailSeedError
from app.share.email.domain.repo import EmailRepository


class ResendEmailService(EmailRepository):
    config: EmailConfig = EmailConfig()

    def send(self, to, subject, body, raise_error=False):
        try:
            resend.api_key = self.config.api_key

            params: resend.Emails.SendParams = {
                "from": "no-reply <no-reply@aqua-minds.org>",
                "to": [to],
                "subject": subject,
                "html": body
            }
            resend.Emails.send(params)
        except ApplicationError as e:
            print(e.__class__.__name__)
            print(e)

            if raise_error:
                raise EmailSeedError(e.message, e.status_code)
        except Exception as e:
            print(e.__class__.__name__)
            print(e)
