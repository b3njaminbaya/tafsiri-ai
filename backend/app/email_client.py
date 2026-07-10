import logging
import smtplib
from email.message import EmailMessage

from .core.config import settings

logger = logging.getLogger("app.email")


class EmailClient:
    """Sends transactional email (password reset, verification, GDPR export
    links) via SMTP if configured. If SMTP_HOST is unset, sending degrades to
    logging the message that would have been sent — this makes every flow
    that depends on email (password reset, verification) fully testable and
    usable in local/CI environments with zero mail infrastructure, rather
    than hard-failing when nobody's configured one.
    """

    def __init__(self, host: str, port: int, username: str, password: str, from_address: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_address = from_address

    @property
    def is_configured(self) -> bool:
        return bool(self.host)

    def send(self, to_address: str, subject: str, body: str) -> None:
        if not self.is_configured:
            logger.info(
                "SMTP not configured — logging email instead of sending.\nTo: %s\nSubject: %s\n%s",
                to_address,
                subject,
                body,
            )
            return

        message = EmailMessage()
        message["From"] = self.from_address
        message["To"] = to_address
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            if self.username:
                server.login(self.username, self.password)
            server.send_message(message)


def get_email_client() -> EmailClient:
    return EmailClient(
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_username,
        settings.smtp_password,
        settings.smtp_from_address,
    )
