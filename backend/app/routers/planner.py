import os
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session

from app import schemas
from app.core.config import settings
from app.database import get_db

router = APIRouter(prefix="/planner", tags=["planner"])

client = OpenAI(api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))


@router.post("/day", response_model=schemas.DayPlanResponse)
def generate_day_plan(
    req: schemas.DayPlanRequest,
    db: Session = Depends(get_db),
):
    if not settings.OPENAI_API_KEY and not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY topilmadi")

    use_date = req.date or date.today()
    goals_text = "\n".join(req.goals or [])

    prompt = f"""Aziz uchun quyidagi sana bo'yicha samarali kun rejasini tuzing: {use_date}.
Ma'lumotlar:
{goals_text or 'Maxsus maqsadlar berilmagan, umumiy produktiv kun rejasini tuzing.'}

Jadvalni 30-60 daqiqalik bloklarga bo'ling.
Har bir band uchun:
- vaqt (masalan 07:00-07:30)
- qisqa sarlavha
- izoh

Natijani JSON ko'rinishida qaytaring:
{{
  "date": "YYYY-MM-DD",
  "items": [
    {{"time": "07:00-07:30", "title": "Uyg'onish", "note": "..."}}
  ]
}}
"""

    try:
        completion = client.responses.create(
            model=settings.OPENAI_MODEL,
            input=prompt,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI xato: {e}")

    content = completion.output[0].content[0].text
    import json

    try:
        data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=500, detail="AI noto'g'ri format qaytardi")

    items = [schemas.DayPlanItem(**item) for item in data.get("items", [])]
    return schemas.DayPlanResponse(date=use_date, items=items)
