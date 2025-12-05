import json
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from openai import OpenAI

from app.models import Memory
from app.models import User
from app.db import get_db


# 🔑 OpenAI klientini ishga tushirish
client = OpenAI()


# -----------------------------------------
# 🚀 Embedding yaratish funksiyasi
# -----------------------------------------
def create_embedding(text: str) -> List[float]:
    """
    Matn uchun embedding vektor yaratadi.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


# -----------------------------------------
# 🚀 Yangi memory qo‘shish
# -----------------------------------------
def add_memory(user_id: int, content: str, tags=None, db: Session = None):
    """
    Foydalanuvchi xotirasiga yangi yozuv saqlash.
    - content: eslanadigan matn
    - tags: ["personal", "goal", ...]
    """
    if db is None:
        db = next(get_db())

    embedding = create_embedding(content)

    memory = Memory(
        user_id=user_id,
        content=content,
        tags=tags or [],
        embedding=embedding,
        created_at=datetime.utcnow(),
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory


# -----------------------------------------
# 🚀 Vektor bo‘yicha eng yaqin 5 ta memory qidirish
# -----------------------------------------
def search_memories(user_id: int, query: str, db: Session = None, top_k: int = 5):
    """
    Embedding orqali foydalanuvchining xotirasidan eng mos yozuvlarni topadi.
    """
    if db is None:
        db = next(get_db())

    query_embedding = create_embedding(query)

    memories = (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .all()
    )

    if not memories:
        return []

    # Kosinus o‘xshashlik hisoblash
    def cosine_similarity(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b + 1e-9)

    scored = []
    for m in memories:
        if not m.embedding:
            continue
        score = cosine_similarity(query_embedding, m.embedding)
        scored.append((score, m))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [m for _, m in scored[:top_k]]


# -----------------------------------------
# 🚀 Chat modeliga yuboriladigan memory paketini tayyorlash
# -----------------------------------------
def get_memory_context(user_id: int, query: str, db: Session = None):
    """
    Chat servisga yuborish uchun eng mos xotiralarni matn ko‘rinishida beradi.
    """
    results = search_memories(user_id, query, db=db)

    if not results:
        return ""

    context = "\n".join([f"- {m.content}" for m in results])
    return f"Foydalanuvchi haqida eslab qolingan ma'lumotlar:\n{context}\n"


# -----------------------------------------
# 🚀 Yangi xotira qo‘shilish kerakligini aniqlash (oddiy versiya)
# -----------------------------------------
def should_remember(message: str) -> bool:
    """
    AI nimani eslab qolishi kerakligini aniqlash.
    Bu oddiy versiya — keyinchalik murakkablik qo‘shamiz.
    """
    trigger_words = ["mening ismim", "menga yoqadi", "men yoqtiraman", "maqsadim", "rejalarim"]
    return any(word in message.lower() for word in trigger_words)
