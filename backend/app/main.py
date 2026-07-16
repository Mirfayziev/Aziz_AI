from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db import engine, get_db
from app.models import Base, HealthRecord
from app.schemas import ChatRequest, ChatResponse
from app.health_models import HealthRecordCreate, HealthRecordOut
from app.services.chat_service import chat_with_ai
from app.routers import chat, profile, planner, audio, external, realtime, tts, assistant

# DB jadvallarini yaratish
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aziz AI",
    version="1.0.0"
)

app.include_router(chat.router)
app.include_router(profile.router)
app.include_router(planner.router)
app.include_router(audio.router)
app.include_router(external.router)
app.include_router(realtime.router)
app.include_router(tts.router)
app.include_router(assistant.router)


# ----------------------
# HEALTHCHECK
# ----------------------
@app.get("/")
async def healthcheck():
    return {
        "status": "ok",
        "service": "Aziz AI"
    }


# ----------------------
# CHAT
# ----------------------
@app.post("/aziz-ai", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        answer = await chat_with_ai(
            text=req.message,
            user_id=req.user_external_id,
        )
        return ChatResponse(reply=answer)
    except Exception as e:
        return ChatResponse(reply=f"⚠️ AI xato: {e}")


# ----------------------
# HEALTH API
# ----------------------

# ➤ Yangi yozuv qo‘shish
@app.post("/health", response_model=HealthRecordOut)
def create_health_record(
    payload: HealthRecordCreate,
    db: Session = Depends(get_db)
):
    record = HealthRecord(
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
        db.query(HealthRecord)
        .filter(HealthRecord.user_external_id == user_external_id)
        .order_by(HealthRecord.recorded_at.desc())
        .all()
    )
    return records
