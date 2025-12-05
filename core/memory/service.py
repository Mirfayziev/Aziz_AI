# core/memory/service.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from core.memory.models import MemoryVector
from core.memory.embeddings import get_embedding

async def add_memory(db: Session, user_id: str, content: str):
    vector = await get_embedding(content)

    memory = MemoryVector(
        user_id=user_id,
        content=content,
        embedding=vector
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


async def search_memory(db: Session, query: str, top_k: int = 5):
    vector = await get_embedding(query)

    sql = text("""
        SELECT id, user_id, content, created_at
        FROM memory_vectors
        ORDER BY embedding <-> :vector
        LIMIT :limit
    """)

    rows = db.execute(sql, {"vector": vector, "limit": top_k}).fetchall()
    return [dict(row._mapping) for row in rows]


async def delete_memory(db: Session, memory_id: int):
    item = db.query(MemoryVector).filter(MemoryVector.id == memory_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False
