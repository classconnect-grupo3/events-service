import json
import pika
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.rabbitmq.connection import get_rabbitmq_connection
from src.schemas.assignment_created import AssignmentCreatedEvent
from src.handlers.assignment_created import handle_assignment_created_event


def consume_assignment_created():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue="assignment_created_queue")

    def callback(ch, method, properties, body):
        try:
            payload = json.loads(body)
            event = AssignmentCreatedEvent(**payload)
        except Exception as e:
            print(f"[ERROR] Evento mal formado: {e}")
            return

        db: Session = get_db()
        print(f"[x] Evento recibido: {event.event_type} para {event.course_id}")
        import asyncio

        asyncio.run(handle_assignment_created_event(db, event))
        db.close()

    channel.basic_consume(
        queue="assignment_created_queue", on_message_callback=callback, auto_ack=True
    )
    print("[*] Esperando eventos de asignaciones nuevas. Ctrl+C para salir.")
    channel.start_consuming()
