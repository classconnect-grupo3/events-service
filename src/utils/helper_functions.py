import httpx
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from src.repository.notifications_preferences import get_preferences_by_user_id
from src.utils.logger import setup_logger
from notifications.email import send_notification_email
from notifications.push import send_push_to_token, get_user_fcm_tokens
from utils.result import Success

logger = setup_logger(__name__)


async def get_user_email(user_id: str) -> Optional[str]:
    """Fetch user email from users service."""
    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f"https://users-service-production-968d.up.railway.app/users/{user_id}"
            )
            user_response.raise_for_status()
            user_data = user_response.json()["data"]
            return user_data["email"]
    except Exception as e:
        logger.error(f"Could not get user information for {user_id}: {e}")
        return None


async def send_email_notification(user_email: str, event) -> bool:
    """Send email notification to user using the event's send_email_notification method."""
    try:
        email_data = event.get_email_data()
        result = await send_notification_email(
            user_email, email_data["subject"], email_data["content"]
        )
        if isinstance(result, Success):
            logger.info(f"Email successfully sent to {user_email}")
            return True
        else:
            logger.error(f"Error sending email to {user_email}: {result.error}")
            return False
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False


async def send_notifications_based_on_preferences(
    user_id: str, event, email_enabled: bool, push_enabled: bool
) -> None:
    
    if email_enabled:
        user_email = await get_user_email(user_id)
        if user_email:
            await send_email_notification(user_email, event)

    if push_enabled:
        fcm_tokens = await get_user_fcm_tokens(user_id)

        if not fcm_tokens:
            logger.info(f"No FCM tokens found for user {user_id}")
            return

        # Send push notification to all user's devices
        for token in fcm_tokens:
            await send_push_to_token(token, event)


async def process_user_notification(user_id: str, event, db: Session) -> None:
    """
    Main function to process notifications for a user.
    This handles the common logic of checking preferences and sending notifications.
    """
    preferences = get_preferences_by_user_id(db, user_id)
    pref = next((p for p in preferences if p.event_type == event.event_type), None)

    if not pref:
        logger.info(f"No matching preference found for event type {event.event_type}")
        return

    await send_notifications_based_on_preferences(
        user_id, event, pref.email_enabled, pref.push_enabled
    )
