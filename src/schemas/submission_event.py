from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from src.schemas.base_event import BaseEvent


class SubmissionEventType:
    SUBMISSION_CORRECTED = "submission.corrected"


class SubmissionCorrectedEvent(BaseEvent):
    event_type: str = Field(default=SubmissionEventType.SUBMISSION_CORRECTED)
    course_id: str
    assignment_id: str
    submission_id: str
    student_id: str
    score: Optional[float] = None
    feedback: str
    correction_type: str  # "automatic", "needs_manual_review"
    needs_manual_review: bool
    corrected_at: datetime

    def get_email_data(self) -> Dict[str, Any]:
        """Send email notification for submission corrected."""
        score_text = (
            f"Puntuación: {self.score}" if self.score is not None else "Sin puntuación"
        )
        review_text = (
            "Necesita revisión manual"
            if self.needs_manual_review
            else "Corrección automática"
        )

        return {
            "subject": f"Tu entrega ha sido corregida",
            "content": f"""
            Tu entrega ha sido corregida.
            
            Curso ID: {self.course_id}
            Asignación ID: {self.assignment_id}
            {score_text}
            Tipo de corrección: {review_text}
            Feedback: {self.feedback}
            Fecha de corrección: {self.corrected_at.strftime('%d/%m/%Y %H:%M')}
            
            ¡Revisa los resultados!
            """,
        }
