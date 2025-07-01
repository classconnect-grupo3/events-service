import httpx
from typing import List
from sqlalchemy.orm import Session
from src.utils.logger import setup_logger
from src.schemas.forum_event import ForumActivityEvent
from src.utils.helper_functions import process_user_notification

logger = setup_logger(__name__)


async def get_forum_participants(course_id: str) -> List[str]:
    """Fetch list of user IDs who have participated in the forum."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://courses-service-production.up.railway.app/forum/courses/{course_id}/participants"
            )
            response.raise_for_status()
            response_data = response.json()

            if response is None:
                logger.error("No response received from courses service")
                return []

            # Extract participants from the response structure
            participants = response_data.get("participants", [])

            # Ensure we return a list of strings (user IDs)
            if isinstance(participants, list):
                return [str(p) for p in participants if p]

            return []

    except Exception as e:
        logger.error(f"Could not get forum participants for course {course_id}: {e}")
        return []


async def send_forum_notifications(db: Session, event: ForumActivityEvent) -> None:
    """Main function to handle forum notification sending."""
    logger.info(f"Forum event received: '{event}'")

    # Get forum participants instead of all enrollments
    participants = await get_forum_participants(event.course_id)

    if not participants:
        logger.warning(f"No forum participants found for course {event.course_id}")
        return

    logger.info(f"Starting to process {len(participants)} forum participants")
    for participant_id in participants:
        await process_user_notification(participant_id, event, db)
