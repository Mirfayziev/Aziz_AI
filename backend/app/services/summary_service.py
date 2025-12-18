from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import json

from app.models import Plan
from app.services.openai_client import openai_client
from app.services.summary_service import summary_service
from app.services.memory_service import get_or_create_user


# ======================================================
# AI PROMPT — TOMORROW PLAN
# ======================================================

PLANNER_PROMPT = """
You are Aziz AI planning tomorrow for Aziz.

Based on the daily summary, generate a realistic plan for tomorrow.

Return ONLY valid JSON in this exact schema:
{
  "focus": ["..."],
  "tasks": [
    {
      "time": "09:00",
      "title": "...",
      "description": "...",
      "priority": "high|medium|low"
    }
  ]
}

Rules:
- Max 7 tasks
- Practical and realistic
- Times must be HH:MM (24h)
- Do not mention AI, models, or analysis
- JSON only, no extra text
""".strip()


# ======================================================
# BASIC CRUD (SIZDA BOR EDI — SAQLANDI)
# ======================================================

def create_plan(
    db: Session,
    external_id: str,
    title: str,
    description: Optional[str],
    scheduled_for: Optional[str],
):
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


# ======================================================
# AI → TOMORROW PLAN → DATABASE
# ======================================================

async def generate_and_save_tomorrow_plan(
    db: Session,
    external_id: str,
) -> Dict[str, Any]:
    """
    Daily summary -> AI plan -> Plan table ga yoziladi
    """
    # 1️⃣ Ertangi sana
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # 2️⃣ Daily summary olish
    daily_summary = await summary_service.generate_daily_summary()

    # 3️⃣ AI dan plan so‘rash
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": f"Daily summary:\n{daily_summary}"},
        ],
        temperature=0.35,
        max_tokens=700,
    )

    raw = (response.choices[0].message.content or "").strip()

    try:
        plan_json = json.loads(raw)
    except Exception:
        # fallback — tizim hech qachon yiqilmasin
        plan_json = {
            "focus": ["Stability", "Progress"],
            "tasks": [
                {
                    "time": "10:00",
                    "title": "Main priority",
                    "description": "Eng muhim vazifani davom ettirish",
                    "priority": "high",
                }
            ],
        }

    # 4️⃣ Eski ertangi planlarni o‘chiramiz (duplicate bo‘lmasin)
    user = get_or_create_user(db, external_id)
    (
        db.query(Plan)
        .filter(Plan.user_id == user.id)
        .filter(Plan.scheduled_for == tomorrow)
        .delete()
    )
    db.commit()

    # 5️⃣ Yangi planlarni DB ga yozish
    created: List[Plan] = []

    for task in plan_json.get("tasks", [])[:7]:
        title = f"{task.get('time', '')} — {task.get('title', '')}".strip()
        description = (
            f"Priority: {task.get('priority', 'medium')}\n"
            f"{task.get('description', '')}"
        )

        plan = Plan(
            user_id=user.id,
            title=title,
            description=description,
            scheduled_for=tomorrow,
            status="pending",
        )
        db.add(plan)
        created.append(plan)

    db.commit()

    return {
        "date": tomorrow,
        "focus": plan_json.get("focus", []),
        "tasks_created": len(created),
    }
