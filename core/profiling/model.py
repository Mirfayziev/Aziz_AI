from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class ProfilingEvent(Base):
    __tablename__ = "profiling_events"

    id = Column(String, primary_key=True, default=gen_id)
    event = Column(String)
    event_data = Column(JSON)   # metadata O‘RNIGA event_data
