# core/context/models.py

from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class ContextEvent(Base):
    __tablename__ = "context_events"

    id = Column(String, primary_key=True, default=gen_id)
    type = Column(String, nullable=False)
    payload = Column(JSON)
