
import json
import math
from typing import List, Optional
from sqlalchemy.orm import Session
from openai import OpenAI

from app.models import User, Memory

client = OpenAI()


def get_or_create_user(db: Session, external_id: str, full_name: Optional[str] = None) -> User:
    user = db.query(User).filter(User.external_id == external_id).first()
    if not user:
        user = User(external_id=external_id, full_name=full_name)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def embed_text(text: str) -> List[float]:
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding


def save_memory(db: Session, user: User, content: str, tags: Optional[List[str]] = None) -> Memory:
    embedding = embed_text(content)
    mem = Memory(
        user_id=user.id,
        content=content,
        tags=json.dumps(tags or []),
        embedding=json.dumps(embedding),
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem


def search_memories(db: Session, user: User, query: str, limit: int = 5) -> List[Memory]:
    query_emb = embed_text(query)
    all_mems = db.query(Memory).filter(Memory.user_id == user.id).all()
    scored = []
    for m in all_mems:
        if not m.embedding:
            continue
        emb = json.loads(m.embedding)
        score = _cosine(query_emb, emb)
        scored.append((score, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:limit]]


def build_memory_context(memories: List[Memory]) -> str:
    if not memories:
        return ""
    parts = []
    for m in memories:
        parts.append(f"- {m.content}")
    return "\n".join(parts)
