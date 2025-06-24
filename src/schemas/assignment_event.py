from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any


class AssignmentEventType(Enum):
    ASSIGNMENT_REMINDER = "assignment.reminder"
    ASSIGNMENT_CREATED = "assignment.created"
    # Add more event types as needed


class AssignmentEvent(BaseModel):
    event_type: str
    course_id: str
    assignment_id: str
    assignment_title: str
    assignment_due_date: datetime

    def get_email_data(self) -> Dict[str, Any]:
        """Base method that should be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement get_email_data")


class AssignmentReminder(AssignmentEvent):
    event_type: str = Field(default=AssignmentEventType.ASSIGNMENT_REMINDER.value)

    def get_email_data(self) -> Dict[str, Any]:
        """Send email notification for assignment reminder."""
        return {
            "subject": f"Recordatorio de asignación: {self.assignment_title}",
            "content": f"""
            Recordatorio: Tienes una asignación próxima a vencer.
            
            Título: {self.assignment_title}
            Fecha de entrega: {self.assignment_due_date.strftime('%d/%m/%Y %H:%M')}
            
            ¡Asegúrate de completarla antes de la fecha límite!
            """,
        }


class AssignmentCreated(AssignmentEvent):
    event_type: str = Field(default=AssignmentEventType.ASSIGNMENT_CREATED.value)

    def get_email_data(self) -> Dict[str, Any]:
        """Send email notification for assignment created."""
        return {
            "subject": f"Nueva asignación: {self.assignment_title}",
            "content": f"""
            Se ha creado una nueva asignación en tu curso.
            
            Título: {self.assignment_title}
            Fecha de entrega: {self.assignment_due_date.strftime('%d/%m/%Y %H:%M')}
            
            ¡No olvides completarla a tiempo!
            """,
        }
