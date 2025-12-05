from sqlalchemy.orm import Session
from app.models import User, Memory, Message
from app.db import engine
from openai import OpenAI
import json

client = OpenAI()


# --- FOYDALANUVCHI OLISH yoki YARATISH ---
def get_or_create_user(db: Session, external_id: str):
    user = db.query(User).filter(User.external_id == external_id).first()
    if not user:
        user = User(external_id=external_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# --- XOTIRA SAQLASH ---
def save_memory(db: Session, user_id: int, text: str, tags=None):
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

    mem = Memory(
        user_id=user_id,
        content=text,
        tags=tags or [],
        embedding=embedding
    )
    db.add(mem)
    db.commit()
    return mem


# --- XOTIRANI TOPISH (vektor bo‘yicha) ---
def search_memory(db: Session, user_id: int, query: str, limit: int = 5):
    query_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    memories = db.query(Memory).filter(Memory.user_id == user_id).all()

    def cosine(a, b):
        import math
        return sum(i*j for i, j in zip(a, b)) / (
            math.sqrt(sum(i*i for i in a)) *
            math.sqrt(sum(j*j for j in b))
        )

    scored = [
        (cosine(query_embedding, m.embedding), m)
        for m in memories if m.embedding
    ]

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:limit]]
