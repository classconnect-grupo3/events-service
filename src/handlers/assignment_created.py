import httpx
from sqlalchemy.orm import Session
from src.repository.notifications_preferences import get_preferences_by_user_id
from src.schemas.assignment_created import AssignmentCreatedEvent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def handle_assignment_created_event(db: Session, event: AssignmentCreatedEvent):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://class-connect-main-6b7ca6f.d2.zuplo.dev/courses/{event.course_id}/enrollments"
            )
            response.raise_for_status()
            enrollments = response.json()["data"]
    except Exception as e:
        logger.error(
            f"No se pudieron obtener inscripciones del curso {event.course_id}: {e}"
        )
        return

    for enrollment in enrollments:
        student_id = enrollment["student_id"]
        preferences = get_preferences_by_user_id(db, student_id)
        pref = next((p for p in preferences if p.event_type == event.event_type), None)

        if pref:
            if pref.email_enabled:
                logger.info(f"Enviar email a {student_id}")
            if pref.push_enabled:
                logger.info(f"Enviar push a {student_id}")
