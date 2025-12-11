# app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./azizai.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# MUHIM: FASTAPI uchun get_db generatori
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# AGAR kerak bo'lsa xotira saqlash uchun (chat messages)
def save_ai_message(db, user_id, role, content):
    pass  # keyin to'ldiramiz

def get_user_context(db, user_id):
    return ""
