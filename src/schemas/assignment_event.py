from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AssignmentEventType(Enum):
    ASSIGNMENT_REMINDER = "assignment.reminder"
    ASSIGNMENT_CREATED = "assignment.created"
    # Add more event types as needed


class AssignmentEvent(BaseModel):
    course_id: str
    assignment_id: str
    assignment_title: str
    assignment_due_date: datetime


class AssignmentReminder(AssignmentEvent):
    event_type: str = Field(default=AssignmentEventType.ASSIGNMENT_REMINDER.value)


class AssignmentCreated(AssignmentEvent):
    event_type: str = Field(default=AssignmentEventType.ASSIGNMENT_CREATED.value)
