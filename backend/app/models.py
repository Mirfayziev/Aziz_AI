from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # e.g., telegram chat_id
    name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    goals = Column(JSON, nullable=True)
    interests = Column(JSON, nullable=True)

    messages = relationship("Message", back_populates="user")
    memories = relationship("Memory", back_populates="user")
    plans = relationship("Plan", back_populates="user")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    tags = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True)  # list[float]
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memories")

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")
    scheduled_for = Column(String, nullable=True)  # ISO date string
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="plans")
