from datetime import datetime
from pydantic import BaseModel, Field
from src.schemas.base_event import BaseEvent
from typing import Dict, Any


class FeedbackEventType:
    FEEDBACK_CREATED = "feedback.created"


class FeedbackCreatedEvent(BaseEvent):
    event_type: str = Field(default=FeedbackEventType.FEEDBACK_CREATED)
    course_id: str
    student_id: str
    feedback_id: str
    feedback_text: str
    feedback_rating: int
    feedback_created_at: datetime

    def get_email_data(self) -> Dict[str, Any]:
        """Send email notification for feedback created."""
        return {
            "subject": f"Nuevo feedback recibido",
            "content": f"""
            Has recibido nuevo feedback de tu profesor.
            
            Curso ID: {self.course_id}
            Calificación: {self.feedback_rating}/5
            Comentario: {self.feedback_text}
            Fecha: {self.feedback_created_at.strftime('%d/%m/%Y %H:%M')}
            
            ¡Revisa el feedback para mejorar tu desempeño!
            """,
        }
