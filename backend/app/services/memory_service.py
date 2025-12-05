from typing import List, Tuple, Optional

from sqlalchemy.orm import Session

from ..config import get_openai_client, get_settings
from ..models import UserProfile, Memory

settings = get_settings()
client = get_openai_client()


def get_or_create_user(db: Session, external_user_id: str) -> UserProfile:
    user = db.query(UserProfile).filter_by(external_id=external_user_id).first()
    if user:
        return user
    user = UserProfile(external_id=external_user_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embeddings API orqali matnlarni vektor qiladi."""
    if not texts:
        return []
    resp = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
    )
    return [d.embedding for d in resp.data]


def store_memory(
    db: Session,
    user: UserProfile,
    content: str,
    metadata: Optional[dict] = None,
    embed: bool = True,
) -> Memory:
    embedding = None
    if embed:
        embedding = embed_texts([content])[0]
    mem = Memory(
        user_id=user.id,
        content=content,
        metadata=metadata or {},
        embedding=embedding,
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    s_ab = sum(x * y for x, y in zip(a, b))
    s_a = sum(x * x for x in a) ** 0.5
    s_b = sum(y * y for y in b) ** 0.5
    if s_a == 0 or s_b == 0:
        return 0.0
    return s_ab / (s_a * s_b)


def search_memories(
    db: Session,
    user: UserProfile,
    query: str,
    limit: int = 8,
) -> List[Tuple[Memory, float]]:
    """Queryga eng o‘xshash xotiralarni topish."""
    query_emb = embed_texts([query])[0]
    mems: List[Memory] = (
        db.query(Memory)
        .filter(Memory.user_id == user.id)
        .order_by(Memory.created_at.desc())
        .limit(64)
        .all()
    )
    scored = []
    for m in mems:
        if not m.embedding:
            continue
        score = _cosine(query_emb, m.embedding)
        scored.append((m, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]
