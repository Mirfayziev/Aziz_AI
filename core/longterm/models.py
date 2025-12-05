from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class LongTermMemory(Base):
    __tablename__ = "longterm_memory"

    id = Column(String, primary_key=True, default=gen_id)
    key = Column(String)
    value = Column(JSON)
