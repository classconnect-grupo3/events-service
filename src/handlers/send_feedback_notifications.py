from sqlalchemy.orm import Session
from src.utils.logger import setup_logger
from src.schemas.feedback_event import FeedbackCreatedEvent
from src.utils.helper_functions import process_user_notification

logger = setup_logger(__name__)


async def send_feedback_notifications(db: Session, event: FeedbackCreatedEvent) -> None:
    """Main function to handle feedback notification sending."""
    logger.info(f"Feedback event received: '{event}'")

    await process_user_notification(event.student_id, event, db)
