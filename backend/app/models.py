from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .db import Base, utcnow


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True, unique=True)  # masalan Telegram user_id
    name = Column(String, nullable=True)
    language = Column(String, default="uz")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    memories = relationship("Memory", back_populates="user")
    planners = relationship("PlannerItem", back_populates="user")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), index=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)  # masalan {"source": "chat", ...}
    embedding = Column(JSONB, nullable=True)  # [float, float, ...]
    created_at = Column(DateTime, default=utcnow)

    user = relationship("UserProfile", back_populates="memories")


class PlannerItem(Base):
    __tablename__ = "planner_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), index=True)
    date_str = Column(String, index=True)  # "2025-12-05"
    kind = Column(String, default="today")  # today/tomorrow/week
    plan_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("UserProfile", back_populates="planners")
