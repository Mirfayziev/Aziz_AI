# core/context/service.py

from core.context.models import ContextEvent
from core.database import Session

def my_context_service(data: dict):
    """Context event yaratish xizmati"""
    with Session() as session:
        event = ContextEvent(
            type=data.get("type"),
            payload=data.get("payload"),
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        return {"status": "ok", "event_id": event.id}
