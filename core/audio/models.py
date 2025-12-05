from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class AudioTask(Base):
    __tablename__ = "audio_tasks"

    id = Column(String, primary_key=True, default=gen_id)
    text = Column(String)
    audio_url = Column(String)
