from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..health_models import HealthRecord


router = APIRouter(
    prefix="/api/health",
    tags=["Health"]
)


@router.post("/import")
async def import_health(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    record = HealthRecord(
        id=str(datetime.utcnow().timestamp()),
        source=payload.get("source", "apple_health"),
        data=payload
    )

    db.add(record)
    db.commit()

    return {"status": "ok"}
