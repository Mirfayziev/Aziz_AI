from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class Plan(Base):
    __tablename__ = "planner_ai"

    id = Column(String, primary_key=True, default=gen_id)
    input = Column(String)
    steps = Column(JSON)
    deadline = Column(String)
    meta = Column(JSON)
