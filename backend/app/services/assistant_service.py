# backend/app/services/assistant_service.py

import json
from typing import Tuple, Dict, Any

from app.services.openai_client import openai_client
from app.services.chat_service import chat_with_ai
from app.services.planner_service import generate_and_save_tomorrow_plan
from app.schemas import (
    SocialReplyRequest,
    SocialReplyResponse,
    OfficeDocPlanRequest,
    OfficeDocPlanResponse,
    OfficeDocSection,
    OfficeTableSpec,
)


# ======================================================
# CHAT
# ======================================================

async def brain_query(text: str) -> Tuple[str, bytes]:
    answer = await chat_with_ai(text)
    return answer, b""


# ======================================================
# SOCIAL REPLY
# ======================================================

async def generate_social_reply(req: SocialReplyRequest) -> SocialReplyResponse:
    system_prompt = (
        f"You write a short {req.tone} reply for a {req.platform} message. "
        f"Purpose: {req.purpose}. Reply in the same language as the incoming message. "
        "Return ONLY the reply text, no explanations."
    )

    resp = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.message},
        ],
        temperature=0.6,
        max_tokens=300,
    )

    reply = (resp.choices[0].message.content or "").strip()
    return SocialReplyResponse(reply=reply)


# ======================================================
# OFFICE DOC PLAN
# ======================================================

OFFICE_DOC_PROMPT = """
You plan the structure of a {doc_type} document.
Return ONLY valid JSON in this exact schema:
{{
  "outline": [{{"title": "...", "content": "..."}}],
  "tables": [{{"name": "...", "description": "...", "columns": ["..."]}}],
  "notes_for_user": "..."
}}
No extra text.
""".strip()


async def plan_office_doc(req: OfficeDocPlanRequest) -> OfficeDocPlanResponse:
    system_prompt = OFFICE_DOC_PROMPT.format(doc_type=req.doc_type)
    user_prompt = (
        f"Topic: {req.topic}\nPurpose: {req.purpose}\nDetails: {req.details or '-'}"
    )

    resp = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=700,
    )

    raw = (resp.choices[0].message.content or "").strip()
    try:
        data = json.loads(raw)
    except Exception:
        data = {"outline": [], "tables": [], "notes_for_user": "AI javobini o'qib bo'lmadi."}

    outline = [OfficeDocSection(**s) for s in data.get("outline", [])]
    tables = [OfficeTableSpec(**t) for t in data.get("tables", [])]
    return OfficeDocPlanResponse(
        outline=outline,
        tables=tables,
        notes_for_user=data.get("notes_for_user"),
    )


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
    db,
    external_id: str,
) -> Dict[str, Any]:
    return await generate_and_save_tomorrow_plan(
        db=db,
        external_id=external_id,
    )
