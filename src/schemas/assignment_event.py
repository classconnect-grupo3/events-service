from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AssignmentEventType(Enum):
    ASSIGNMENT_REMINDER = "assignment.reminder"
    ASSIGNMENT_CREATED = "assignment.created"
    # Add more event types as needed


@dataclass
class AssignmentEvent:
    course_id: str
    assignment_id: str
    assignment_title: str
    assignment_due_date: datetime


@dataclass
class AssignmentReminder(AssignmentEvent):
    def __post_init__(self):
        self.event_type = AssignmentEventType.ASSIGNMENT_REMINDER.value


@dataclass
class AssignmentCreated(AssignmentEvent):
    def __post_init__(self):
        self.event_type = AssignmentEventType.ASSIGNMENT_CREATED.value
