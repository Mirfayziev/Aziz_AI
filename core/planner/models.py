from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from core.database import Base

class PlannerTask(Base):
    __tablename__ = "planner_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    priority = Column(Integer, default=1)   # 1-low, 2-mid, 3-high
    deadline = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")  # pending, done
    created_at = Column(DateTime, server_default=func.now())


class PlannerDailySummary(Base):
    __tablename__ = "planner_daily_summary"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(20), nullable=False)  # yyyy-mm-dd
    summary = Column(Text, nullable=True)
    ai_recommendation = Column(Text, nullable=True)


class PlannerAutoPlan(Base):
    __tablename__ = "planner_auto_plan"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(20), nullable=False)
    ai_plan = Column(Text, nullable=False)
