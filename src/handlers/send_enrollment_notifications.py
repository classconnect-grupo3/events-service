from sqlalchemy.orm import Session
from src.utils.logger import setup_logger
from src.schemas.enrollment_event import (
    EnrolledStudentToCourseEvent,
    UnenrolledStudentFromCourseEvent,
)
from src.utils.helper_functions import process_user_notification

logger = setup_logger(__name__)


async def send_enrollment_notifications(
    db: Session, event: EnrolledStudentToCourseEvent | UnenrolledStudentFromCourseEvent
) -> None:
    """Main function to handle enrollment notification sending."""
    logger.info(f"Enrollment event received: '{event}'")

    await process_user_notification(event.student_id, event, db)
