# backend/app/services/chat_service.py

import os
from typing import List, Dict
from sqlalchemy.orm import Session
from openai import OpenAI

# Optional DB hooks (if they exist)
try:
    from app.db import get_user_context, save_user_context, save_ai_message
except Exception:
    get_user_context = None
    save_user_context = None
    save_ai_message = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


SYSTEM_PROMPT = (
    "Sen Aziz AI assistantsan. Javoblar aniq, qisqa va foydali bo‘lsin. "
    "Agar aniq ma’lumot kerak bo‘lsa, foydalanuvchidan 1 ta aniq savol bilan so‘rab aniqlashtir. "
    "Foydalanuvchi aytgan gapni shunchaki takrorlama."
)


def _build_messages(previous_context: str, user_message: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if previous_context and previous_context.strip():
        # Keep context compact
        ctx = previous_context.strip()
        if len(ctx) > 4000:
            ctx = ctx[-4000:]
        messages.append({"role": "system", "content": f"Oldingi kontekst:\n{ctx}"})
    messages.append({"role": "user", "content": user_message})
    return messages


def create_chat_reply(db: Session, external_id: str, user_message: str) -> str:
    """
    external_id: Telegram chat_id (string)
    user_message: user text
    """
    if not client:
        return "OPENAI_API_KEY yo‘q. Backend Variables’da OPENAI_API_KEY ni qo‘ying."

    # 1) oldingi kontekst
    previous_context = ""
    if get_user_context:
        try:
            previous_context = get_user_context(db, external_id) or ""
        except Exception:
            previous_context = ""

    messages = _build_messages(previous_context, user_message)

    # 2) OpenAI chat
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.5,
    )

    reply_text = (resp.choices[0].message.content or "").strip()
    if not reply_text:
        reply_text = "Javob topilmadi. Savolni biroz boshqacha yozib ko‘ring."

    # 3) kontekstni yangilash
    if save_user_context:
        try:
            new_context = f"{previous_context}\nUser: {user_message}\nAI: {reply_text}".strip()
            # clamp
            if len(new_context) > 8000:
                new_context = new_context[-8000:]
            save_user_context(db, external_id, new_context)
        except Exception:
            pass

    # 4) tarix
    if save_ai_message:
        try:
            save_ai_message(db, external_id, "assistant", reply_text)
        except Exception:
            pass

    return reply_text
