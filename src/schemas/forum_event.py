from datetime import datetime
from pydantic import BaseModel, Field
from src.schemas.base_event import BaseEvent
from typing import Dict, Any


class ForumEventType:
    FORUM_ACTIVITY = "forum.activity"


class ForumActivityEvent(BaseEvent):
    event_type: str = Field(default=ForumEventType.FORUM_ACTIVITY)
    course_id: str
    student_id: str
    post_id: str
    post_text: str
    post_created_at: datetime

    def get_email_data(self) -> Dict[str, Any]:
        """Send email notification for forum activity."""
        return {
            "subject": f"Nueva actividad en el foro",
            "content": f"""
            Hay nueva actividad en el foro de tu curso.
            
            Curso ID: {self.course_id}
            Post: {self.post_text[:100]}{'...' if len(self.post_text) > 100 else ''}
            Fecha: {self.post_created_at.strftime('%d/%m/%Y %H:%M')}
            
            ¡Participa en la discusión!
            """,
        }
