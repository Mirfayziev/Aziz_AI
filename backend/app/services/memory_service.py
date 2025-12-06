from sqlalchemy.orm import Session
import numpy as np
from openai import OpenAI
from ..config import get_settings
from ..models import Memory, User

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_or_create_user(db: Session, external_id: str) -> User:
    user = db.query(User).filter_by(external_id=external_id).first()
    if not user:
        user = User(external_id=external_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def embed_text(text: str) -> list[float]:
    emb = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text
    )
    return emb.data[0].embedding

def store_memory(db: Session, external_id: str, content: str, tags: list[str] | None = None):
    user = get_or_create_user(db, external_id)
    vec = embed_text(content)
    m = Memory(user_id=user.id, content=content, tags=tags, embedding=vec)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def search_memories(db: Session, external_id: str, query: str, top_k: int = 3) -> list[Memory]:
    user = get_or_create_user(db, external_id)
    q_emb = np.array(embed_text(query))
    memories = db.query(Memory).filter_by(user_id=user.id).all()
    if not memories:
        return []
    scored = []
    for m in memories:
        if not m.embedding:
            continue
        v = np.array(m.embedding)
        denom = (np.linalg.norm(q_emb) * np.linalg.norm(v)) or 1.0
        score = float(q_emb.dot(v) / denom)
        scored.append((score, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:top_k]]
