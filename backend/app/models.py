# backend/app/models.py

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserContext(Base):
    __tablename__ = "user_context"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    context = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text)
    scheduled_for = Column(String, index=True)  # YYYY-MM-DD
    status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)
