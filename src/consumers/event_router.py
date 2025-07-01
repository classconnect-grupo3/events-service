import json
import os
import pika
from src.database.db import get_db
from src.rabbitmq.connection import get_rabbitmq_connection
from src.schemas.base_event import BaseEvent
from src.schemas.assignment_event import (
    AssignmentEvent,
    AssignmentReminder,
    AssignmentCreated,
)
from src.schemas.teacher_event import (
    AuxTeacherAddedEvent,
    AuxTeacherRemovedEvent,
)
from src.schemas.feedback_event import (
    FeedbackCreatedEvent,
)
from src.schemas.enrollment_event import (
    EnrolledStudentToCourseEvent,
    UnenrolledStudentFromCourseEvent,
)
from src.schemas.forum_event import (
    ForumActivityEvent,
)
from src.schemas.submission_event import (
    SubmissionCorrectedEvent,
)
from src.handlers.send_notifications import (
    send_notifications,
)
from src.handlers.send_teacher_notifications import (
    send_teacher_notifications,
)
from src.handlers.send_feedback_notifications import (
    send_feedback_notifications,
)
from src.handlers.send_enrollment_notifications import (
    send_enrollment_notifications,
)
from src.handlers.send_forum_notifications import (
    send_forum_notifications,
)
from src.handlers.send_submission_notifications import (
    send_submission_notifications,
)
from src.utils.logger import setup_logger
import asyncio

logger = setup_logger(__name__)


class EventRouter:
    def __init__(self):
        self.connection = get_rabbitmq_connection()
        self.channel = self.connection.channel()
        self.queue_name = os.getenv("NOTIFICATIONS_QUEUE_NAME")
        self.channel.queue_declare(queue=self.queue_name)

    def _get_event_class(self, event_type: str):
        """Get the appropriate event class based on event type."""
        event_map = {
            "assignment.created": AssignmentCreated,
            "assignment.reminder": AssignmentReminder,
            "aux_teacher.added": AuxTeacherAddedEvent,
            "aux_teacher.removed": AuxTeacherRemovedEvent,
            "feedback.created": FeedbackCreatedEvent,
            "student.enrolled": EnrolledStudentToCourseEvent,
            "student.unenrolled": UnenrolledStudentFromCourseEvent,
            "forum.activity": ForumActivityEvent,
            "submission.corrected": SubmissionCorrectedEvent,
        }
        return event_map.get(event_type)

    def _get_event_handler(self, event_type: str):
        """Get the appropriate handler function based on event type."""
        handler_map = {
            "assignment.created": send_notifications,
            "assignment.reminder": send_notifications,
            "aux_teacher.added": send_teacher_notifications,
            "aux_teacher.removed": send_teacher_notifications,
            "feedback.created": send_feedback_notifications,
            "student.enrolled": send_enrollment_notifications,
            "student.unenrolled": send_enrollment_notifications,
            "forum.activity": send_forum_notifications,
            "submission.corrected": send_submission_notifications,
        }
        return handler_map.get(event_type)

    def _callback(self, ch, method, properties, body):
        try:
            # First try to parse as BaseEvent to get the event type
            base_event = BaseEvent.model_validate_json(body)
            event_type = base_event.event_type

            # Get the appropriate event class and handler
            event_class = self._get_event_class(event_type)
            handler = self._get_event_handler(event_type)

            if not event_class or not handler:
                logger.warning(f"Event type {event_type} not recognized")
                return

            # Parse the full event
            event = event_class.model_validate_json(body)

            # Get database session
            db = next(get_db())
            try:
                logger.info(f"Evento recibido: {event_type}")
                asyncio.run(handler(db, event))
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def start(self):
        """Start consuming messages."""
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self._callback,
            auto_ack=True,
        )
        logger.info(f"Esperando eventos en cola: {self.queue_name}")
        self.channel.start_consuming()
