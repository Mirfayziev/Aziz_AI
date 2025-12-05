from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.orm import Session

from ..config import get_openai_client, get_settings
from ..models import PlannerItem
from .memory_service import get_or_create_user

settings = get_settings()
client = get_openai_client()


def _planner_dates(mode: str) -> Tuple[str, str]:
    today = datetime.utcnow().date()
    if mode == "tomorrow":
        d = today + timedelta(days=1)
        return d.isoformat(), "ertangi"
    if mode == "week":
        return today.isoformat(), "shu hafta"
    return today.isoformat(), "bugungi"


def create_plan(
    db: Session,
    external_user_id: str,
    text: str,
    mode: str = "today",
) -> Tuple[str, str]:
    """
    Reja tuzadi va bazaga saqlaydi.
    """
    user = get_or_create_user(db, external_user_id)
    date_str, uz_label = _planner_dates(mode)

    system = (
        "Sen professional shaxsiy rejalashtirish assistenti. "
        "Foydalanuvchiga bugungi/ertangi/haftalik ishlar rejasini aniq, vaqt bilan, "
        "moddama-modd yozib ber. O'zbek tilida, markdown formatida yoz."
    )

    prompt = (
        f"Reja turi: {uz_label}\n"
        f"Foydalanuvchi qo'shimcha ma'lumoti: {text}\n\n"
        f"Kun/hafta bo'yicha aniq vaqt va bloklarga bo'lib reja yoz."
    )

    completion = client.chat.completions.create(
        model=settings.MODEL_DEFAULT,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    plan_text = completion.choices[0].message.content.strip()

    item = PlannerItem(
        user_id=user.id,
        date_str=date_str,
        kind=mode,
        plan_text=plan_text,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return plan_text, date_str
