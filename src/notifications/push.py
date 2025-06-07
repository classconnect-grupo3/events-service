from firebase_admin import messaging
import httpx
from src.utils.logger import setup_logger
from typing import List
from src.schemas.assignment_event import (
    AssignmentEvent,
    AssignmentReminder,
    AssignmentCreated,
)

logger = setup_logger(__name__)


def _get_notification_content(event: AssignmentEvent) -> tuple[str, str]:
    """
    Generate notification title and body based on event type.

    Args:
        event (AssignmentEvent): The event to generate notification content for

    Returns:
        tuple[str, str]: A tuple containing (title, body)
    """
    if isinstance(event, AssignmentReminder):
        return (
            "Assignment Reminder",
            f"Reminder: {event.assignment_title} is due on {event.assignment_due_date}",
        )
    elif isinstance(event, AssignmentCreated):
        return ("New Assignment", f"New assignment available: {event.assignment_title}")


async def send_push_to_token(token: str, event: AssignmentEvent):
    """
    Send a push notification to a specific FCM token.

    Args:
        token (str): The FCM token to send the notification to
        event (AssignmentEvent): The event to generate notification content from

    Returns:
        bool: True if the notification was sent successfully, False otherwise
    """
    try:
        title, body = _get_notification_content(event)
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        messaging.send(message)
        logger.info(f"✅ Push notification sent to token: {token}")
    except messaging.UnregisteredError:
        logger.warning(f"❌ Invalid or expired token: {token}")
        await delete_token(token=token)
    except Exception as e:
        logger.error(f"Error sending push notification: {e}, for token: {token}")


async def get_user_fcm_tokens(uid: str) -> List[str]:
    """
    Get all FCM tokens associated with a user.

    Args:
        uid (str): The user ID to get tokens for

    Returns:
        List[str]: List of FCM tokens for the user
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://notifications-service-production.up.railway.app/notifications/tokens",
                params={"uid": uid},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            return [t["fcm_token"] for t in data]
    except Exception as e:
        logger.error(f"Error getting FCM tokens for user {uid}: {e}")
        return []


async def delete_token(token: str) -> None:
    """
    Delete an FCM token from the notifications service.

    Args:
        token (str): The FCM token to delete
    """
    try:
        async with httpx.AsyncClient() as client:
            await client.delete(
                "https://notifications-service-production.up.railway.app/notifications/token",
                params={"token": token},
                timeout=5,
            )
            logger.info(f"Successfully deleted token: {token}")
    except Exception as e:
        logger.error(f"Error deleting token {token}: {e}")
