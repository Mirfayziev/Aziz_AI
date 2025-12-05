from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.profiling.service import log_event, get_events

router = APIRouter(prefix="/api/profiling", tags=["Profiling"])

@router.get("/")
def fetch_events(db: Session = Depends(get_db)):
    return get_events(db)

@router.post("/")
def create_event(data: dict, db: Session = Depends(get_db)):
    return log_event(
        db,
        event_type=data.get("event_type", "unknown"),
        metadata=data.get("metadata", {})
    )
