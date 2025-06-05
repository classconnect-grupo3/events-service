from datetime import datetime
from src.schemas.base_event import BaseEvent


class AssignmentEvent(BaseEvent):
    course_id: str
    assignment_id: str
    assignment_title: str
    assignment_due_date: datetime
