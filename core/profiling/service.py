from core.profiling.model import ProfilingEvent
from core.database import SessionLocal

def get_events():
    db = SessionLocal()
    events = db.query(ProfilingEvent).all()
    return [ {"id": e.id, "event": e.event, "metadata": e.metadata} for e in events ]

def add_event(data: dict):
    db = SessionLocal()
    ev = ProfilingEvent(event=data.get("event"), metadata=data.get("metadata"))
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return {"id": ev.id}
