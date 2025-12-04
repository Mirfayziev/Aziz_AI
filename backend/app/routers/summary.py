import os
from datetime import date, datetime, timedelta

import requests
from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session

from app import schemas
from app.core.config import settings
from app.database import get_db
from app.models import MemoryEntry

router = APIRouter(prefix="/summary", tags=["summary"])

client = OpenAI(api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))


def _build_daily_context(db: Session, chat_id: str, day: date) -> str:
    start = datetime(day.year, day.month, day.day)
    end = start + timedelta(days=1)
    entries = (
        db.query(MemoryEntry)
        .filter(
            MemoryEntry.chat_id == chat_id,
            MemoryEntry.created_at >= start,
            MemoryEntry.created_at < end,
        )
        .order_by(MemoryEntry.created_at.asc())
        .all()
    )
    lines = []
    for m in entries:
        prefix = "User" if m.role == "user" else "AI"
        lines.append(f"[{prefix}] {m.content}")
    return "\n".join(lines)


@router.post("/daily", response_model=schemas.DailySummaryResponse)
def daily_summary(req: schemas.DailySummaryRequest, db: Session = Depends(get_db)):
    if not settings.OPENAI_API_KEY and not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY topilmadi")

    use_date = req.date or date.today()
    context = _build_daily_context(db, req.chat_id, use_date)

    if not context.strip():
        raise HTTPException(status_code=404, detail="Bu kun uchun xotira yo'q")

    prompt = f"""Quyidagi suhbatlar Azizning bugungi kuni haqida.
Uning kayfiyati, muammolari, muvaffaqiyatlari va asosiy g'oyalari haqida qisqa, lekin chuqur tahlil qiling.
Oxirida 3-5 ta aniq maslahat bering.

Suhbatlar:
{context}
"""

    try:
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Sen psixologik yordamchi va hayot kouchisan."},
                {"role": "user", "content": prompt},
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI xato: {e}")

    summary = completion.choices[0].message["content"]
    return schemas.DailySummaryResponse(date=use_date, summary=summary)


@router.post("/daily/push/{chat_id}")
def daily_summary_push(chat_id: str, db: Session = Depends(get_db)):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="TELEGRAM_BOT_TOKEN sozlanmagan")

    today = date.today()
    data = daily_summary(schemas.DailySummaryRequest(chat_id=chat_id, date=today), db=db)

    text = f"📋 Bugungi kundalik xulosang:\n\n{data.summary}"
    resp = requests.post(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Telegramga yuborishda xato")
    return {"ok": True}
