# app/services/chat_service.py

from openai import OpenAI
from sqlalchemy.orm import Session
from app.db import get_user_context, save_user_context, save_ai_message
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def create_chat_reply(db: Session, user_id: str, user_message: str) -> str:
    """
    Foydalanuvchi xabariga AI javob yaratadi.
    Barcha ma'lumotlar DB orqali saqlanadi.
    """

    # 1) Eski kontekstni olish
    previous_context = get_user_context(db, user_id)

    messages = []
    if previous_context:
        messages.append({"role": "system", "content": previous_context})

    messages.append({"role": "user", "content": user_message})

    # 2) ChatGPT dan javob
    ai_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply_text = ai_response.choices[0].message["content"]

    # 3) Kontekstni yangilash
    new_context = f"{previous_context}\nUser: {user_message}\nAI: {reply_text}"
    save_user_context(db, user_id, new_context)

    # 4) Tarixga yozish
    save_ai_message(db, user_id, "assistant", reply_text)

    return reply_text
