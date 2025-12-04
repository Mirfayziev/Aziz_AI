from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # shaxs modeli (meta-data)
    bio = Column(Text, nullable=True)
    goals = Column(Text, nullable=True)
    interests = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    timezone = Column(String, nullable=True, default="Asia/Tashkent")

    memories = relationship("MemoryEntry", back_populates="user")
