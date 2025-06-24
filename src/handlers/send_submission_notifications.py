from sqlalchemy.orm import Session
from src.utils.logger import setup_logger
from src.schemas.submission_event import SubmissionCorrectedEvent
from src.utils.helper_functions import process_user_notification

logger = setup_logger(__name__)


async def send_submission_notifications(
    db: Session, event: SubmissionCorrectedEvent
) -> None:
    """Main function to handle submission notification sending."""
    logger.info(f"Submission event received: '{event}'")

    await process_user_notification(event.student_id, event, db)
