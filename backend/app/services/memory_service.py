from app.db import SessionLocal
from app.models import User, Memory


# ----------------------------
# USER GET/CREATE
# ----------------------------
def get_or_create_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        user = User(id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


# ----------------------------
# GET USER MEMORIES
# ----------------------------
def get_user_memories(user_id: int, limit: int = 10):
    db = SessionLocal()
    memories = (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .limit(limit)
        .all()
    )
    return memories


# ----------------------------
# SAVE NEW MEMORY
# ----------------------------
def save_memory(user_id: int, text: str):
    db = SessionLocal()
    memory = Memory(
        user_id=user_id,
        text=text
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


# ----------------------------
# SHOULD THIS MESSAGE BE SAVED AS MEMORY?
# ----------------------------

KEYWORDS = [
    "mening ismim",
    "ismim",
    "mening maqsadim",
    "maqsadim",
    "men doim",
    "men yoqtiraman",
    "menga yoqadi",
    "men shunday odamman",
    "men yashayman",
    "manzilim",
    "kasbim",
    "men ishlayman"
]

def should_save_memory(text: str) -> bool:
    text = text.lower().strip()
    return any(k in text for k in KEYWORDS)


# ----------------------------
# BUILD MEMORY CONTEXT FOR AI
# ----------------------------
def build_memory_context(memories):
    if not memories:
        return ""

    lines = []
    for m in memories:
        lines.append(f"- {m.text}")

    return "\n".join(lines)
