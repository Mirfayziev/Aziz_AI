from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.types import JSON, Float
from sqlalchemy.dialects.postgresql import ARRAY

from app.database import Base
from app.core.config import settings


# PostgreSQL bo'lsa ARRAY(Float), aks holda JSON(list of floats) ishlatamiz
if settings.SQLALCHEMY_DATABASE_URI.startswith("postgresql"):
    embedding_type = ARRAY(Float)
else:
    embedding_type = JSON


class VectorMemory(Base):
    __tablename__ = "vector_memories"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True, nullable=False)
    message_id = Column(Integer, nullable=True)  # MemoryEntry.id bilan bog'lash mumkin
    role = Column(String, nullable=False)        # odatda "user"
    content = Column(String, nullable=False)
    embedding = Column(embedding_type, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
