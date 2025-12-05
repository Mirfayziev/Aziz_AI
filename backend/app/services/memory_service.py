from typing import List, Optional
from math import sqrt

from sqlalchemy.orm import Session

from .openai_client import client  # shu faylda client bor (chat_service.py dagidek)
from ..models import User, Memory


# ===========================
# EMBEDDING YORDAMCHI FUNKSIYA
# ===========================
def _create_embedding(text: str) -> List[float]:
    """
    Matn uchun OpenAI embedding vektori yaratadi.
    Natija Memory.embedding (JSON) ga list[float] ko'rinishida saqlanadi.
    """
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return resp.data[0].embedding


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Ikki vektor o'rtasidagi kosinus o'xshashlik.
    """
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a)) or 1e-9
    nb = sqrt(sum(y * y for y in b)) or 1e-9
    return dot / (na * nb)


# ===========================
# USER BILAN ISHLASH
# ===========================
def get_or_create_user(db: Session, external_id: str) -> User:
    """
    Telegram chat_id yoki boshqa external_id bo'yicha User ni topadi,
    bo'lmasa yaratadi.
    """
    user = db.query(User).filter_by(external_id=external_id).first()
    if not user:
        user = User(external_id=external_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ===========================
# MEMORY SAQLASH
# ===========================
def add_memory(
    db: Session,
    user: User,
    content: str,
    tags: Optional[List[str]] = None,
) -> Memory:
    """
    Foydalanuvchi uchun yangi memory yozuvi yaratadi (embedding bilan).
    """
    embedding = _create_embedding(content)

    mem = Memory(
        user_id=user.id,
        content=content,
        tags=tags or [],
        embedding=embedding,
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem


# Eslab qolishga arziydigan gapmi?
_MEMORY_TRIGGERS = [
    "mening ismim",
    "ismim",
    "mening maqsadim",
    "maqsadim",
    "menga yoqadi",
    "men yoqtiraman",
    "men doim",
    "kasbim",
    "men ishlayman",
    "men yashayman",
]


def should_remember(text: str) -> bool:
    text = (text or "").lower()
    return any(t in text for t in _MEMORY_TRIGGERS)


# eski nom bilan ham ishlasin:
def should_save_memory(text: str) -> bool:
    return should_remember(text)


# ===========================
# MEMORY QIDIRISH
# ===========================
def search_memories(
    db: Session,
    external_id: str,
    query: str,
    top_k: int = 5,
) -> List[Memory]:
    """
    Berilgan foydalanuvchi uchun query ga eng o'xshash `top_k` ta memory qaytaradi.
    """
    user = db.query(User).filter_by(external_id=external_id).first()
    if not user:
        return []

    query_emb = _create_embedding(query)

    memories = (
        db.query(Memory)
        .filter(Memory.user_id == user.id)
        .all()
    )
    scored: List[tuple[float, Memory]] = []

    for m in memories:
        if not m.embedding:
            continue
        score = _cosine_similarity(query_emb, m.embedding)
        scored.append((score, m))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for (s, m) in scored[:top_k]]


# ===========================
# MEMORY KONTEXT – CHATGA UCHUN
# ===========================
def get_memory_context(
    db: Session,
    external_id: str,
    query: str,
    top_k: int = 5,
) -> str:
    """
    Chat modeliga beriladigan "memory" kontekst matnini tayyorlaydi.
    Agar boshqa joydan `get_memory_context` import qilingan bo'lsa – shuni ishlatadi.
    """
    memories = search_memories(db, external_id, query, top_k=top_k)
    if not memories:
        return ""

    lines = [f"- {m.content}" for m in memories]
    return "Foydalanuvchi haqida eslab qolingan ma'lumotlar:\n" + "\n".join(lines)


# ===========================
# PROFIL/ADMIN UCHUN FOYDALANISHI MUMKIN BO'LGAN FUNKSIYALAR
# (agar profile.py ishlatsa, xato bo'lmasligi uchun)
# ===========================
def get_user_memories(db: Session, external_id: str, limit: int = 20) -> List[Memory]:
    user = db.query(User).filter_by(external_id=external_id).first()
    if not user:
        return []
    return (
        db.query(Memory)
        .filter(Memory.user_id == user.id)
        .order_by(Memory.created_at.desc())
        .limit(limit)
        .all()
    )


def build_memory_context(memories: List[Memory]) -> str:
    if not memories:
        return ""
    return "\n".join(f"- {m.content}" for m in memories)
