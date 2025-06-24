import os
from email.message import EmailMessage
import aiosmtplib
from typing import Union

from utils.logger import setup_logger
from utils.result import Failure, Success

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
logger = setup_logger(__name__)


async def send_notification_email(
    to_email: str, subject: str, content: str
) -> Union[Success, Failure]:
    """
    Send a notification email with the provided subject and content.

    Args:
        to_email: Recipient's email address
        subject: Email subject line
        content: Email body content
    """
    try:
        message = EmailMessage()
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(content)

        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=EMAIL_ADDRESS,
            password=EMAIL_APP_PASSWORD,
        )

        logger.info(f"Email sent successfully to {to_email} with subject: {subject}")
        return Success(f"Email de notificación enviado exitosamente a {to_email}")

    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return Failure(Exception(f"Error al enviar email: {e}"))
