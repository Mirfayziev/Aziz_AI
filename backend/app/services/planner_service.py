from sqlalchemy.orm import Session
from datetime import datetime, date
from ..models import Plan
from app.db import get_or_create_user

def create_plan(db: Session, external_id: str, title: str, description: str | None, scheduled_for: str | None):
    user = get_or_create_user(db, external_id)
    plan = Plan(
        user_id=user.id,
        title=title,
        description=description,
        scheduled_for=scheduled_for,
        status="pending",
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

def get_today_plans(db: Session, external_id: str):
    user = get_or_create_user(db, external_id)
    today_str = date.today().isoformat()
    return (
        db.query(Plan)
        .filter(Plan.user_id == user.id)
        .filter(Plan.scheduled_for == today_str)
        .all()
    )

