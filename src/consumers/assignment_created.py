import json
import pika
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.rabbitmq.connection import get_rabbitmq_connection
from src.schemas.assignment_created import AssignmentCreatedEvent
from src.handlers.assignment_created import handle_assignment_created_event
from src.utils.logger import setup_logger
import asyncio

logger = setup_logger(__name__)


def consume_assignment_created():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue="assignment_created_queue")

    def callback(ch, method, properties, body):
        try:
            payload = json.loads(body)
            event = AssignmentCreatedEvent(**payload)
        except Exception as e:
            logger.error(f"Evento mal formado: {e}")
            return

        # Get the actual session from the generator
        db = next(get_db())
        try:
            logger.info(f"Evento recibido: {event.event_type} para {event.course_id}")
            asyncio.run(handle_assignment_created_event(db, event))
        finally:
            db.close()

    channel.basic_consume(
        queue="assignment_created_queue", on_message_callback=callback, auto_ack=True
    )
    logger.info("Esperando eventos de asignaciones nuevas.")
    channel.start_consuming()
