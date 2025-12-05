# core/memory/models.py

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy import Float
from sqlalchemy.dialects.postgresql import ARRAY
from core.database import Base

class MemoryVector(Base):
    __tablename__ = "memory_vectors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    content = Column(String)
    embedding = Column(VECTOR(1536))   # text-embedding-3-large → 3072 bo'lsa, 3072 qo'yamiz
    created_at = Column(DateTime, server_default=func.now())

