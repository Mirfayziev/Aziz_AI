# backend/app/services/planner_service.py

from typing import Dict, Any, List
from datetime import date, timedelta
import json

from sqlalchemy.orm import Session

from app.db import get_or_create_user
from app.models import Plan
from app.services.openai_client import openai_client


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


async def generate_and_save_tomorrow_plan(
    db: Session,
    external_id: str,
) -> Dict[str, Any]:
    """
    Daily summary -> AI plan -> plans table
    """

    # ✅ LAZY IMPORT — CIRCULAR YO‘Q
    from app.services.summary_service import summary_service

    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    daily_summary = await summary_service.generate_daily_summary()

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
        plan_json = {
            "focus": ["Stability"],
            "tasks": [
                {
                    "time": "10:00",
                    "title": "Main priority",
                    "description": "Eng muhim vazifani davom ettirish",
                    "priority": "high",
                }
            ],
        }

    user = get_or_create_user(db, external_id)

    db.query(Plan).filter(
        Plan.user_id == user.id,
        Plan.scheduled_for == tomorrow,
    ).delete()
    db.commit()

    for task in plan_json.get("tasks", [])[:7]:
        plan = Plan(
            user_id=user.id,
            title=f"{task.get('time')} — {task.get('title')}",
            description=task.get("description"),
            scheduled_for=tomorrow,
            status=task.get("priority", "medium"),
        )
        db.add(plan)

    db.commit()

    return {
        "date": tomorrow,
        "focus": plan_json.get("focus", []),
        "tasks_created": len(plan_json.get("tasks", [])),
    }
