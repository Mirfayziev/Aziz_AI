import openai
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from . import models, schemas
import numpy as np

EMBED_MODEL = "text-embedding-3-large"

# 1) Query embedding
def embed_text(content: str) -> list:
    resp = openai.embeddings.create(
        model=EMBED_MODEL,
        input=content
    )
    return resp.data[0].embedding

# 2) Xotiraga yozish
def add_memory(db: Session, data: schemas.MemoryAdd):
    emb = embed_text(data.text)

    record = models.MemoryRecord(
        user_id=data.user_id,
        text=data.text,
        embedding=emb,
        source=data.source
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# 3) Vector search (pgvector)
def search_memory(db: Session, query: str, top_k: int = 5):
    query_emb = embed_text(query)

    q = db.query(
        models.MemoryRecord.text,
        sql_text(f"(embedding <=> '({','.join(str(x) for x in query_emb)})') as score")
    ).order_by(sql_text("score ASC")).limit(top_k)

    results = q.all()

    return [
        schemas.MemorySearchResult(text=row[0], score=float(row[1]))
        for row in results
    ]

# 4) Ro'yxat
def list_memory(db: Session):
    return db.query(models.MemoryRecord).order_by(models.MemoryRecord.id.desc()).all()
