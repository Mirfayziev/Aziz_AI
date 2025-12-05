from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Backend boshlanganda chaqiriladigan funksiya
def create_db_and_tables():
    import core.models  # barcha modellaring shu yerga ulanadi
    Base.metadata.create_all(bind=engine)
