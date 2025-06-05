import json
import pika
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.rabbitmq.connection import get_rabbitmq_connection
from src.schemas.base_event import BaseEvent
from schemas.assignment_event import AssignmentEvent
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
        self.channel.queue_declare(queue="notifications_queue")

    def _get_event_class(self, event_type: str) -> type[BaseEvent]:
        """Get the appropriate event class based on event type."""
        event_map = {
            "assignment.created": AssignmentEvent,
            "assiggnment.reminder": AssignmentEvent,
        }
        return event_map.get(event_type)

    def _get_event_handler(self, event_type: str):
        """Get the appropriate handler function based on event type."""
        handler_map = {
            "assignment.created": send_notifications,
            "assiggnment.reminder": send_notifications,
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
            queue="notifications_queue",
            on_message_callback=self._callback,
            auto_ack=True,
        )
        logger.info("Esperando eventos...")
        self.channel.start_consuming()
