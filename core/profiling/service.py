from sqlalchemy.orm import Session
from core.profiling.model import ProfilingEvent

def log_event(db: Session, event_type: str, metadata: dict):
    event = ProfilingEvent(event_type=event_type, metadata=metadata)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def get_events(db: Session):
    return db.query(ProfilingEvent).all()
