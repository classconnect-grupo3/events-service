from sqlalchemy.orm import Session
from src.model.notification_preferences import NotificationPreferences


def get_preferences_by_user_id(
    db: Session, user_id: str
) -> list[NotificationPreferences]:
    return (
        db.query(NotificationPreferences)
        .filter(NotificationPreferences.uid == user_id)
        .all()
    )
