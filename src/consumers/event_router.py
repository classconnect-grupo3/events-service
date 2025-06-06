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
from handlers.send_notifications import (
    send_notifications,
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

    def _get_event_class(self, event_type: str) -> type[AssignmentEvent]:
        """Get the appropriate event class based on event type."""
        event_map = {
            "assignment.created": AssignmentCreated,
            "assignment.reminder": AssignmentReminder,
        }
        return event_map.get(event_type)

    def _get_event_handler(self, event_type: str):
        """Get the appropriate handler function based on event type."""
        handler_map = {
            "assignment.created": send_notifications,
            "assignment.reminder": send_notifications,
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
