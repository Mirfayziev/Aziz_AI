# backend/app/services/assistant_service.py

from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session

from app.services.chat_service import chat_with_ai
from app.services.planner_service import generate_and_save_tomorrow_plan


# ======================================================
# CHAT
# ======================================================

async def brain_query(text: str) -> Tuple[str, bytes]:
    answer = await chat_with_ai(text)
    return answer, b""


# ======================================================
# SUMMARY (LAZY IMPORT — CIRCULAR YO‘Q)
# ======================================================

async def get_daily_summary() -> str:
    from app.services.summary_service import summary_service
    return await summary_service.generate_daily_summary()


async def get_weekly_summary() -> str:
    from app.services.summary_service import summary_service
    return await summary_service.generate_weekly_summary()


# ======================================================
# PLAN (VARIANT A — DIRECT CALL)
# ======================================================

async def generate_tomorrow_plan(
    db: Session,
    external_id: str,
) -> Dict[str, Any]:
    return await generate_and_save_tomorrow_plan(
        db=db,
        external_id=external_id,
    )
