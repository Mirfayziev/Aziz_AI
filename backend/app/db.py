# backend/app/db.py

import os
from datetime import datetime
from typing import Generator

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ======================================================
# DATABASE CONFIG
# ======================================================
# Agar Railway / prod bo‘lsa -> env dan oladi
# Aks holda -> local sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./azizai.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# ======================================================
# MODELS (MINIMAL, CORE)
# ======================================================

class User(Base):
    """
    Aziz AI uchun yagona user jadvali
    external_id = telegram_id / web_id / boshqa
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserContext(Base):
    """
    Qisqa text-based context (legacy + fallback)
    Vector memory bilan parallel ishlaydi
    """
    __tablename__ = "user_context"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    context = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ======================================================
# SESSION DEPENDENCY (FastAPI)
# ======================================================

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================================================
# USER HELPERS (PLANNER + AI CORE UCHUN MUHIM)
# ======================================================

def get_or_create_user(db: Session, external_id: str) -> User:
    """
    external_id -> user
    Agar bo‘lmasa yaratadi
    """
    user = db.query(User).filter(User.external_id == external_id).first()
    if user:
        return user

    user = User(external_id=external_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ======================================================
# CONTEXT HELPERS (BACKWARD COMPATIBILITY)
# ======================================================

def save_user_context(db: Session, external_id: str, context: str) -> None:
    user = get_or_create_user(db, external_id)

    obj = db.query(UserContext).filter(UserContext.user_id == user.id).first()
    if obj:
        obj.context = context
    else:
        obj = UserContext(user_id=user.id, context=context)
        db.add(obj)

    db.commit()

def get_user_context(db: Session, external_id: str) -> str:
    user = get_or_create_user(db, external_id)

    obj = db.query(UserContext).filter(UserContext.user_id == user.id).first()
    if obj:
        return obj.context or ""
    return ""

# ======================================================
# INIT TABLES
# ======================================================

Base.metadata.create_all(bind=engine)
