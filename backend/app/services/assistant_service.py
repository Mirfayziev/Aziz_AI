from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.chat_service import chat_with_ai
from app.services.summary_service import summary_service
from app.services.planner_service import generate_and_save_tomorrow_plan


# ======================================================
# ASOSIY AI CHAT (TEXT)
# ======================================================

async def brain_query(text: str) -> Tuple[str, bytes]:
    """
    Text -> Aziz AI -> (answer, audio_bytes)
    Hozircha audio_bytes bo‘sh (ovoz strategik o‘chiq)
    """
    answer = await chat_with_ai(text)
    return answer, b""


# ======================================================
# SUMMARY WRAPPERS
# ======================================================

async def get_daily_summary() -> str:
    return await summary_service.generate_daily_summary()


async def get_weekly_summary() -> str:
    return await summary_service.generate_weekly_summary()


# ======================================================
# PLAN GENERATION (SUMMARY → DB)
# ======================================================

async def generate_tomorrow_plan(
    db: Session,
    external_id: str,
) -> Dict[str, Any]:
    """
    Daily summary -> AI -> Plan table
    """
    return await generate_and_save_tomorrow_plan(
        db=db,
        external_id=external_id,
    )
