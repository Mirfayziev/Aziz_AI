from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app import models
from backend.app.schemas import ChatRequest, ChatResponse
from backend.app.health_models import HealthRecordCreate, HealthRecordOut

models.Base.metadata.create_all(bind=models.engine)

app = FastAPI(
    title="Aziz AI",
    version="1.0.0"
)

# ----------------------
# Healthcheck
# ----------------------
@app.get("/")
async def healthcheck():
    return {"status": "ok", "service": "Aziz AI"}


# ----------------------
# CHAT (existing)
# ----------------------
@app.post("/aziz-ai", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply = f"Sening savoling: {req.message}"
    return ChatResponse(reply=reply)


# ----------------------
# HEALTH API
# ----------------------

# ➤ Yangi yozuv qo‘shish (Apple Health dan keladigan data)
@app.post("/health", response_model=HealthRecordOut)
def create_health_record(
    payload: HealthRecordCreate,
    db: Session = Depends(get_db)
):
    record = models.HealthRecord(
        user_external_id=payload.user_external_id,
        metric_type=payload.metric_type,
        value=payload.value,
        unit=payload.unit,
        recorded_at=payload.recorded_at
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ➤ Foydalanuvchi bo‘yicha ko‘rish
@app.get("/health/{user_external_id}", response_model=list[HealthRecordOut])
def list_health_records(user_external_id: str, db: Session = Depends(get_db)):
    records = (
        db.query(models.HealthRecord)
        .filter(models.HealthRecord.user_external_id == user_external_id)
        .order_by(models.HealthRecord.recorded_at.desc())
        .all()
    )
    return records
