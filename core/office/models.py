from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class OfficeTask(Base):
    __tablename__ = "office_tasks"

    id = Column(String, primary_key=True, default=gen_id)
    type = Column(String)    # "word" | "excel" | "ppt"
    input = Column(JSON)
    output = Column(JSON)
