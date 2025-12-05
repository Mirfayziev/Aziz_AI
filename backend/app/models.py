from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # masalan: Telegram chat_id, yoki boshqa tashqi ID
    external_id = Column(String, unique=True, index=True)

    name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

    # JSON ko‘rinishida saqlanadigan maqsadlar, qiziqishlar
    goals = Column(JSON, nullable=True)       # ["AI o‘rganish", "Ingliz tilini B2"]
    interests = Column(JSON, nullable=True)   # ["fitness", "startup", "trading"]

    # Aloqalar
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="user", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    # "user" yoki "assistant"
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")


class Memory(Base):
    """
    Memory (xotira) yozuvlari:
    - content: AI eslab qolishi kerak bo‘lgan matn
    - tags: ["personal", "goal", "preference"] kabi taglar
    - embedding: OpenAI embedding vektori (list[float]) JSON ko‘rinishida
    """
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    content = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)        # ["personal"], ["goal"], ...
    embedding = Column(JSON, nullable=True)   # [0.123, 0.456, ...]
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memories")


class Plan(Base):
    """
    Planner modulidagi rejalar:
    - title: qisqa nom (masalan, "Bugungi reja", "Haftalik maqsadlar")
    - description: to‘liq matnli reja
    - status: "pending", "done", ...
    - scheduled_for: ISO formatdagi sana / vaqt (str sifatida saqlayapmiz)
    """
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")
    scheduled_for = Column(String, nullable=True)  # masalan: "2025-12-06"

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="plans")
