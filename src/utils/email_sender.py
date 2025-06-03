import os
from email.message import EmailMessage
import aiosmtplib
from typing import Union
from datetime import datetime

from utils.result import Failure, Success

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


async def send_notification_email(
    to_email: str, event_type: str, event_data: dict
) -> Union[Success, Failure]:
    """
    Send a notification email about an event.

    Args:
        to_email: Recipient's email address
        event_type: Type of event (e.g., 'assignment_created')
        event_data: Dictionary containing event details
    """
    try:
        message = EmailMessage()
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email

        # Customize subject and content based on event type
        if event_type == "assignment.created":
            message["Subject"] = f"Nueva asignación: {event_data['assignment_title']}"
            content = f"""
            Se ha creado una nueva asignación en tu curso.
            
            Título: {event_data['assignment_title']}
            Fecha de entrega: {event_data['assignment_due_date'].strftime('%d/%m/%Y %H:%M')}
            
            ¡No olvides completarla a tiempo!
            """
        else:
            message["Subject"] = f"Nueva notificación: {event_type}"
            content = f"Has recibido una nueva notificación de tipo: {event_type}"

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
