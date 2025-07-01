from pydantic import BaseModel, Field
from src.schemas.base_event import BaseEvent
from typing import Dict, Any


class TeacherEventType:
    AUX_TEACHER_ADDED = "aux_teacher.added"
    AUX_TEACHER_REMOVED = "aux_teacher.removed"


class AuxTeacherAddedEvent(BaseEvent):
    event_type: str = Field(default=TeacherEventType.AUX_TEACHER_ADDED)
    course_id: str
    course_name: str
    teacher_id: str

    def get_email_data(self) -> Dict[str, Any]:
        """Send email notification for aux teacher added."""
        return {
            "subject": f"Has sido agregado como profesor auxiliar",
            "content": f"""
            Has sido agregado como profesor auxiliar en el curso.
            
            Curso: {self.course_name}
            ID del curso: {self.course_id}
            
            Ya puedes acceder al contenido y gestionar el curso.
            """,
        }


class AuxTeacherRemovedEvent(BaseEvent):
    event_type: str = Field(default=TeacherEventType.AUX_TEACHER_REMOVED)
    course_id: str
    course_name: str
    teacher_id: str

    def get_email_data(self) -> Dict[str, Any]:
        """Send email notification for aux teacher removed."""
        return {
            "subject": f"Has sido removido como profesor auxiliar",
            "content": f"""
            Has sido removido como profesor auxiliar del curso.
            
            Curso: {self.course_name}
            ID del curso: {self.course_id}
            
            Ya no tienes acceso al contenido del curso.
            """,
        }
