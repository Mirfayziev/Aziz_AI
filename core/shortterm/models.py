from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class ShortTermMemory(Base):
    __tablename__ = "shortterm_memory"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String)
    data = Column(JSON)
