from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..health_models import HealthRecord

router = APIRouter(prefix="/health", tags=["Health"])


@router.post("/")
def save_health_record(
    metric: str,
    value: float,
    unit: str = "",
    db: Session = Depends(get_db)
):
    record = HealthRecord(metric=metric, value=value, unit=unit)
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"saved": True, "id": record.id}


@router.get("/")
def list_health_records(db: Session = Depends(get_db)):
    return db.query(HealthRecord).order_by(HealthRecord.recorded_at.desc()).limit(50).all()
