from sqlalchemy.orm import Session
from src.utils.logger import setup_logger
from src.schemas.teacher_event import (
    AuxTeacherAddedEvent,
    AuxTeacherRemovedEvent,
)
from src.utils.helper_functions import process_user_notification

logger = setup_logger(__name__)


async def send_teacher_notifications(
    db: Session, event: AuxTeacherAddedEvent | AuxTeacherRemovedEvent
) -> None:
    """Main function to handle teacher notification sending."""
    logger.info(f"Teacher event received: '{event}'")

    await process_user_notification(event.teacher_id, event, db)
