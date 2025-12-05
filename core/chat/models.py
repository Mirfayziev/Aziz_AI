from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=gen_id)
    role = Column(String)          # "user" | "assistant"
    content = Column(String)
    meta = Column(JSON)
