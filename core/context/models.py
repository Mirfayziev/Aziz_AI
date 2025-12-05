from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class ContextSlice(Base):
    __tablename__ = "context_slices"

    id = Column(String, primary_key=True, default=gen_id)
    messages = Column(JSON)
    score = Column(String)
