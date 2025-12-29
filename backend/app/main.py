from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.assistant_service import (
    brain_query,
    get_daily_summary,
    get_weekly_summary,
    generate_tomorrow_plan,
)
from app.services.memory_service import memory_service

# ⬇️ YANGI: Health data model
from app.models import HealthMetric


app = FastAPI(
    title="Aziz AI",
    version="1.0.0",
)


@app.get("/")
async def healthcheck():
    return {"status": "ok"}


# ======================================================
# 1️⃣  HEALTH DATA IMPORT (Apple / Auto Export)
# ======================================================
@app.post("/health/import")
async def import_health(request: Request, db: Session = Depends(get_db)):
    """
    Health Auto Export → Aziz AI ga ma'lumot yuborish.

    Example payload (oddiy misol):
    {
        "metric": "heart_rate",
        "value": 78,
        "unit": "bpm",
        "recorded_at": "2025-12-29T10:00:00Z",
        "raw": {...}
    }
    """

    data = await request.json()

    metric = data.get("metric")
    value = data.get("value")

    if not metric or value is None:
        return {"error": "metric va value majburiy"}

    record = HealthMetric(
        metric=metric,
        value=float(value),
        unit=data.get("unit"),
        recorded_at=data.get("recorded_at"),
        raw=data,
        user_id="aziz",
    )

    db.add(record)
    db.commit()

    return {"status": "saved"}


# ======================================================
# 2️⃣  YAGONA AZIZ AI ENDPOINT
# ======================================================

@app.post("/aziz-ai")
async def aziz_ai(request: Request, db: Session = Depends(get_db)):
    """
    Unified Aziz AI endpoint
    """

    data = await request.json()
    req_type = data.get("type")

    # ================= CHAT =================
    if req_type == "chat":
        text = (data.get("text") or "").strip()
        if not text:
            return {"error": "Text is empty"}

        memory_service.store_message(role="user", content=text)

        answer, meta = await brain_query(text)

        memory_service.store_message(role="assistant", content=answer)

        try:
            await memory_service.extract_and_store_facts(
                user_id="aziz",
                user_message=text,
            )
        except Exception:
            pass

        return {"type": "chat", "text": answer, "meta": meta}

    # ================= SUMMARY =================
    if req_type == "summary":
        period = data.get("period", "daily")

        if period == "weekly":
            return {
                "type": "summary",
                "period": "weekly",
                "text": await get_weekly_summary(),
            }

        return {
            "type": "summary",
            "period": "daily",
            "text": await get_daily_summary(),
        }

    # ================= PLAN =================
    if req_type == "plan":
        external_id = data.get("external_id")
        if not external_id:
            return {"error": "external_id is required"}

        plan = await generate_tomorrow_plan(db=db, external_id=external_id)

        return {"type": "plan", "result": plan}

    return {"error": "Invalid request type"}
