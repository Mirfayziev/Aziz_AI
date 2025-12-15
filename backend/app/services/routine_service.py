from sqlalchemy.orm import Session
from datetime import date
from app.models.daily_routine import DailyRoutine


def save_daily_routine(db: Session, user_id: int, data: dict):
    routine = DailyRoutine(
        user_id=user_id,
        date=date.today(),

        wake_time=data.get("wake_time"),
        work_start_time=data.get("work_start_time"),
        lunch_time=data.get("lunch_time"),
        rest_after_lunch_min=data.get("rest_after_lunch_min"),
        work_end_time=data.get("work_end_time"),
        dinner_time=data.get("dinner_time"),
        night_work_start=data.get("night_work_start"),
        night_work_end=data.get("night_work_end"),

        sleep_quality="medium",
        energy_level="medium",
        stress_level="medium",
    )

    db.add(routine)
    db.commit()
    db.refresh(routine)

    return routine
