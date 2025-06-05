import httpx
from sqlalchemy.orm import Session
from src.repository.notifications_preferences import get_preferences_by_user_id
from src.utils.logger import setup_logger
from src.utils.email_sender import send_notification_email
from utils.result import Success
from typing import List, Dict, Optional
from src.schemas.assignment_event import (
    AssignmentEvent,
    AssignmentReminder,
    AssignmentCreated,
)

logger = setup_logger(__name__)


async def check_submission_status(assignment_id: str, student_id: str) -> bool:
    """
    Check if a student has already submitted an assignment.
    Returns True if the student has submitted (status is 'submitted' or 'late'),
    False otherwise.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://courses-service-production.up.railway.app/students/{student_id}/submissions"
            )
            response.raise_for_status()
            submissions = response.json()

            # Find submission for this specific assignment
            assignment_submission = next(
                (sub for sub in submissions if sub["assignment_id"] == assignment_id),
                None,
            )

            if assignment_submission:
                # Check if submission status is 'submitted' or 'late'
                return assignment_submission["status"] in ["submitted", "late"]

            return False

    except Exception as e:
        logger.error(
            f"Error checking submission status for student {student_id} and assignment {assignment_id}: {e}"
        )
        return False


async def get_course_enrollments(course_id: str) -> List[Dict]:
    """Fetch enrollments for a given course."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://courses-service-production.up.railway.app/courses/{course_id}/enrollments"
            )
            response.raise_for_status()
            response_data = response.json()

            if response is None:
                logger.error("No response received from courses service")
                return []

            return (
                response_data
                if isinstance(response_data, list)
                else response_data.get("data", [])
            )
    except Exception as e:
        logger.error(f"Could not get enrollments for course {course_id}: {e}")
        return []


async def get_user_email(student_id: str) -> Optional[str]:
    """Fetch user email from users service."""
    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"https://users-service-production-968d.up.railway.app/users/{student_id}"
            )
            user_response.raise_for_status()
            user_data = user_response.json()["data"]
            return user_data["email"]
    except Exception as e:
        logger.error(f"Could not get user information for {student_id}: {e}")
        return None


async def send_email_notification(user_email: str, event: AssignmentEvent) -> bool:
    """Send email notification to user."""
    try:
        event_data = {
            "assignment_title": event.assignment_title,
            "assignment_due_date": event.assignment_due_date,
        }

        result = await send_notification_email(user_email, event.event_type, event_data)
        if isinstance(result, Success):
            logger.info(f"Email successfully sent to {user_email}")
            return True
        else:
            logger.error(f"Error sending email to {user_email}: {result.error}")
            return False
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False


async def process_enrollment(
    enrollment: Dict, event: AssignmentEvent, db: Session
) -> None:
    """Process a single enrollment for notifications."""
    student_id = enrollment["student_id"]

    # For AssignmentReminder events, check if student has already submitted
    if isinstance(event, AssignmentReminder):
        has_submitted = await check_submission_status(event.assignment_id, student_id)
        if has_submitted:
            logger.info(
                f"Student {student_id} has already submitted assignment {event.assignment_id}, skipping reminder"
            )
            return

    preferences = get_preferences_by_user_id(db, student_id)
    pref = next((p for p in preferences if p.event_type == event.event_type), None)

    if not pref:
        logger.info(f"No matching preference found for event type {event.event_type}")
        return

    if pref.email_enabled:
        user_email = await get_user_email(student_id)
        if user_email:
            await send_email_notification(user_email, event)

    if pref.push_enabled:
        logger.info(f"Sending push to {student_id}")
        # Implement push notification logic here


async def send_notifications(db: Session, event: AssignmentEvent) -> None:
    """Main function to handle notification sending."""
    logger.info(f"Event received: '{event}'")

    enrollments = await get_course_enrollments(event.course_id)

    if not enrollments:
        logger.warning(f"No enrollments found for course {event.course_id}")
        return

    logger.info(f"Starting to process {len(enrollments)} enrollments")
    for enrollment in enrollments:
        await process_enrollment(enrollment, event, db)
