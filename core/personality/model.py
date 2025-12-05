from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class PersonalityProfile(Base):
    __tablename__ = "personality_profile"

    id = Column(String, primary_key=True, default=gen_id)
    traits = Column(JSON)
    preferences = Column(JSON)
