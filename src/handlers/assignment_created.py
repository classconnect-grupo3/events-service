import httpx
from sqlalchemy.orm import Session
from src.repository.notifications_preferences import get_preferences_by_user_id
from src.schemas.assignment_created import AssignmentCreatedEvent

async def handle_assignment_created_event(db: Session, event: AssignmentCreatedEvent):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://courses-service:8000/courses/{event.course_id}/students")
            response.raise_for_status()
            students = response.json()["data"]
    except Exception as e:
        print(f"[ERROR] No se pudieron obtener estudiantes del curso {event.course_id}: {e}")
        return

    for student in students:
        uid = student["uid"]
        preferences = get_preferences_by_user_id(db, uid)
        pref = next((p for p in preferences if p.event_type == event.event_type), None)

        if pref:
            if pref.email_enabled:
                print(f"📧 Enviar email a {uid} por asignación {event.assignment_title}")
            if pref.push_enabled:
                print(f"📲 Enviar push a {uid} por asignación {event.assignment_title}")
