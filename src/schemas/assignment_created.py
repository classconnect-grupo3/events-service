from pydantic import BaseModel
from datetime import datetime

class AssignmentCreatedEvent(BaseModel):
    event_type: str
    course_id: str
    assignment_id: str
    assignment_title: str
    assignment_due_date: datetime
