import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


def send_verification_code(recipient: str, code: str) -> None:
    """Send an OTP through SMTP, or log it for local development."""
    if not settings.SMTP_HOST:
        if settings.ENVIRONMENT.lower() == "production":
            raise RuntimeError("SMTP_HOST must be configured in production")
        logger.info("Email verification OTP for %s: %s", recipient, code)
        return

    message = EmailMessage()
    message["Subject"] = f"{settings.PROJECT_NAME} email verification"
    message["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME or "no-reply@example.com"
    message["To"] = recipient
    message.set_content(
        f"Your verification code is {code}. It expires in {settings.OTP_EXPIRY_MINUTES} minutes."
    )

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
        if settings.SMTP_USE_TLS:
            smtp.starttls()
        if settings.SMTP_USERNAME:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
        smtp.send_message(message)
