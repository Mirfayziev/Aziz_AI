from sqlalchemy import Column, Integer, String, Time, Date, ForeignKey
from app.core.database import Base


class DailyRoutine(Base):
    __tablename__ = "daily_routines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    date = Column(Date, nullable=False)

    wake_time = Column(Time)
    work_start_time = Column(Time)
    lunch_time = Column(Time)
    rest_after_lunch_min = Column(Integer)
    work_end_time = Column(Time)
    dinner_time = Column(Time)
    night_work_start = Column(Time)
    night_work_end = Column(Time)

    sleep_quality = Column(String, default="unknown")   # low / medium / high
    energy_level = Column(String, default="medium")    # low / medium / high
    stress_level = Column(String, default="medium")    # low / medium / high
