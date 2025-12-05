from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings  # settings obyektini import qilamiz

DATABASE_URL = settings.DATABASE_URL  # configdan olamiz

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_db_and_tables():
    import core.models  # barcha modellaring shu yerda import qilinadi
    Base.metadata.create_all(bind=engine)
