from sqlalchemy import Column, String
from core.database import Base

class AgentSession(Base):
    __tablename__ = "agent_sessions"

    chat_id = Column(String, primary_key=True)
    state = Column(String)
