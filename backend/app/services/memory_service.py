from sqlalchemy.orm import Session
from app.models import Memory
from datetime import datetime


# ===== Xotiradan kontekst olish =====
def get_memory_context(user_id: int, db: Session):
    records = (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .limit(10)
        .all()
    )

    # Faqat matnni qaytaramiz
    context = "\n".join([f"User: {m.user_message}\nAI: {m.ai_reply}" for m in records])
    return context



# ===== Xotirani saqlash =====
def save_memory(user_id: int, message: str, reply: str, db: Session):
    obj = Memory(
        user_id=user_id,
        user_message=message,
        ai_reply=reply,
        created_at=datetime.utcnow()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj



# ===== Foydalanuvchi tarixini olish (ixtiyoriy) =====
def get_user_history(user_id: int, db: Session, limit: int = 20):
    records = (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .limit(limit)
        .all()
    )
    return records
