# backend/app/db.py

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "sqlite:///./azizai.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserContext(Base):
    __tablename__ = "user_context"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    context = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_ai_message(db: Session, user_id: str, role: str, content: str) -> None:
    # hozircha bo'sh, lekin mavjud bo‘lishi shart
    return


def save_user_context(db: Session, user_id: str, context: str) -> None:
    obj = db.query(UserContext).filter(UserContext.user_id == user_id).first()

    if obj:
        obj.context = context
    else:
        obj = UserContext(user_id=user_id, context=context)
        db.add(obj)

    db.commit()
    db.refresh(obj)


def get_user_context(db: Session, user_id: str) -> str:
    obj = db.query(UserContext).filter(UserContext.user_id == user_id).first()
    if obj:
        return obj.context or ""
    return ""


Base.metadata.create_all(bind=engine)
