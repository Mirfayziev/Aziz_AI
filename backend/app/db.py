# backend/app/db.py

import os
from datetime import datetime
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# MUHIM: User modeli faqat models.py da bo‘ladi
from app.models import User, UserContext

# ======================================================
# DATABASE CONFIG
# ======================================================

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
# SESSION DEPENDENCY
# ======================================================

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================================================
# USER HELPERS (BARCHA SERVICELAR UCHUN)
# ======================================================

def get_or_create_user(db: Session, external_id: str) -> User:
    user = db.query(User).filter(User.external_id == external_id).first()
    if user:
        return user

    user = User(external_id=external_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ======================================================
# INIT TABLES
# ======================================================

# MUHIM: create_all faqat bitta joyda bo‘lishi kerak
from app.models import Base as ModelsBase
ModelsBase.metadata.create_all(bind=engine)
