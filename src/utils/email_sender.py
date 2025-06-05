import os
from email.message import EmailMessage
import aiosmtplib
from typing import Union
from datetime import datetime

from utils.logger import setup_logger
from utils.result import Failure, Success

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
logger = setup_logger(__name__)


async def send_notification_email(
    to_email: str, event_type: str, event_data: dict
) -> Union[Success, Failure]:
    """
    Send a notification email about an event.

    Args:
        to_email: Recipient's email address
        event_type: Type of event (e.g., 'assignment.created')
        event_data: Dictionary containing event details
    """
    try:
        message = EmailMessage()
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email

        if event_type == "assignment.created":
            message["Subject"] = f"Nueva asignación: {event_data['assignment_title']}"
            content = f"""
            Se ha creado una nueva asignación en tu curso.
            
            Título: {event_data['assignment_title']}
            Fecha de entrega: {event_data['assignment_due_date'].strftime('%d/%m/%Y %H:%M')}
            
            ¡No olvides completarla a tiempo!
            """
        elif event_type == "assignment.reminder":
            message["Subject"] = (
                f"Recordatorio de asignación: {event_data['assignment_title']}"
            )
            content = f"""
            Recordatorio: Tienes una asignación próxima a vencer.
            
            Título: {event_data['assignment_title']}
            Fecha de entrega: {event_data['assignment_due_date'].strftime('%d/%m/%Y %H:%M')}
            
            ¡Asegúrate de completarla antes de la fecha límite!
            """
        else:
            logger.info("Evento no reconocido")

        message.set_content(content)

        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=EMAIL_ADDRESS,
            password=EMAIL_APP_PASSWORD,
        )
        return Success(f"Email de notificación enviado exitosamente a {to_email}")
    except Exception as e:
        return Failure(Exception(f"Error al enviar email: {e}"))
