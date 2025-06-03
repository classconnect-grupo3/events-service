import httpx
from sqlalchemy.orm import Session
from src.repository.notifications_preferences import get_preferences_by_user_id
from src.schemas.assignment_created import AssignmentCreatedEvent
from src.utils.logger import setup_logger
from src.utils.email_sender import send_notification_email
from utils.result import Success

logger = setup_logger(__name__)


async def handle_assignment_created_event(db: Session, event: AssignmentCreatedEvent):

    try:
        async with httpx.AsyncClient() as client:
            # Get enrollments
            response = await client.get(
                f"https://courses-service-production.up.railway.app/courses/{event.course_id}/enrollments"
            )
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"Response data: {response_data}")

            enrollments = (
                response_data
                if isinstance(response_data, list)
                else response_data.get("data", [])
            )

            if not enrollments:
                logger.warning(
                    f"No se encontraron inscripciones para el curso {event.course_id}"
                )
                return

    except Exception as e:
        logger.error(
            f"No se pudieron obtener inscripciones del curso {event.course_id}: {e}"
        )
        return

    for enrollment in enrollments:
        student_id = enrollment["student_id"]

        # Get user data to get their email
        try:
            async with httpx.AsyncClient() as client:
                user_response = await client.get(
                    f"https://users-service-production-968d.up.railway.app/users/{student_id}"
                )
                user_response.raise_for_status()
                user_data = user_response.json()["data"]
                user_email = user_data["email"]
        except Exception as e:
            logger.error(
                f"No se pudo obtener información del usuario {student_id}: {e}"
            )
            continue

        preferences = get_preferences_by_user_id(db, student_id)
        pref = next((p for p in preferences if p.event_type == event.event_type), None)

        if pref:
            if pref.email_enabled:
                logger.info(
                    f"Enviando email a {user_email} sobre la asignación {event.assignment_title}"
                )
                # Convert event to dict for email function
                event_data = {
                    "assignment_title": event.assignment_title,
                    "assignment_due_date": event.assignment_due_date,
                }
                result = await send_notification_email(
                    user_email, event.event_type, event_data
                )
                if isinstance(result, Success):
                    logger.info(f"Email enviado exitosamente a {user_email}")
                else:
                    logger.error(
                        f"Error al enviar email a {user_email}: {result.error}"
                    )
            if pref.push_enabled:
                logger.info(f"Enviar push a {student_id}")
