from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.assistant_service import (
    brain_query,
    get_daily_summary,
    get_weekly_summary,
    generate_tomorrow_plan,
)

app = FastAPI(
    title="Aziz AI",
    version="1.0.0",
)


@app.get("/")
async def healthcheck():
    return {"status": "ok"}


# ======================================================
# YAGONA AZIZ AI ENDPOINT
# ======================================================

@app.post("/aziz-ai")
async def aziz_ai(request: Request, db: Session = Depends(get_db)):
    """
    Unified Aziz AI endpoint

    Examples:
    { "type": "chat", "text": "Bugun nima qilay?" }
    { "type": "summary", "period": "daily" }
    { "type": "summary", "period": "weekly" }
    { "type": "plan", "external_id": "telegram_123" }
    """

    data = await request.json()
    req_type = data.get("type")

    # ---------------- CHAT ----------------
    if req_type == "chat":
        text = (data.get("text") or "").strip()
        if not text:
            return {"error": "Text is empty"}

        answer, meta = await brain_query(text)
        return {
            "type": "chat",
            "text": answer,
            "meta": meta,
        }

    # ---------------- SUMMARY ----------------
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

    # ---------------- PLAN ----------------
    if req_type == "plan":
        external_id = data.get("external_id")
        if not external_id:
            return {"error": "external_id is required"}

        plan = await generate_tomorrow_plan(
            db=db,
            external_id=external_id,
        )

        return {
            "type": "plan",
            "result": plan,
        }

    return {"error": "Invalid request type"}
