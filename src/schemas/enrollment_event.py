from pydantic import BaseModel, Field
from src.schemas.base_event import BaseEvent
from typing import Dict, Any


class EnrollmentEventType:
    STUDENT_ENROLLED = "student.enrolled"
    STUDENT_UNENROLLED = "student.unenrolled"


class EnrolledStudentToCourseEvent(BaseEvent):
    event_type: str = Field(default=EnrollmentEventType.STUDENT_ENROLLED)
    course_id: str
    student_id: str

    def get_email_data(self) -> Dict[str, Any]:
        """Send email notification for student enrolled."""
        return {
            "subject": f"Inscripción exitosa",
            "content": f"""
            ¡Te has inscrito exitosamente en el curso!
            
            Curso ID: {self.course_id}
            
            Ya puedes acceder al contenido del curso y comenzar tu aprendizaje.
            """,
        }


class UnenrolledStudentFromCourseEvent(BaseEvent):
    event_type: str = Field(default=EnrollmentEventType.STUDENT_UNENROLLED)
    course_id: str
    student_id: str

    def get_email_data(self) -> Dict[str, Any]:
        """Send email notification for student unenrolled."""
        return {
            "subject": f"Has sido desinscrito del curso",
            "content": f"""
            Has sido desinscrito del curso.
            
            Curso ID: {self.course_id}
            
            Ya no tienes acceso al contenido del curso.
            """,
        }
