from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime

from .db import Base   # MUHIM: sizda Base shu fayldan keladi


class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    source = Column(String, nullable=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
