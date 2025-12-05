from sqlalchemy import Column, Integer, Text, String, DateTime, func
from sqlalchemy.dialects.postgresql import VECTOR
from core.database import Base

class MemoryRecord(Base):
    __tablename__ = "memory_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, default="aziz")

    text = Column(Text, nullable=False)
    embedding = Column(VECTOR(1536))

    source = Column(String(50), default="chat")
    created_at = Column(DateTime, server_default=func.now())
