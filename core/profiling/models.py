from sqlalchemy import Column, String, JSON
from core.database import Base
from core.utils import gen_id

class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(String, primary_key=True, default=gen_id)
    identity = Column(JSON)        # ism, yosh, kasb...
    behavior = Column(JSON)        # fe’l-atvor, gap ohangi
    preferences = Column(JSON)     # qiziqishlar, sevimli mavzular
    stats = Column(JSON)           # qancha marta gaplashgan, so‘nggi faollik
