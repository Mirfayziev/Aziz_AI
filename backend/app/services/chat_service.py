import json
from sqlalchemy.orm import Session
from openai import OpenAI

from app.db import get_db
from app.services.memory_service import (
    get_memory_context,
    should_remember,
    add_memory
)

# OpenAI klienti
client = OpenAI()


# ------------------------------------------------------
# 🚀 Chat javobini yaratish (Memory bilan)
# ------------------------------------------------------
def create_chat_reply(user_id: int, message: str, db: Session = None):
    """
    Foydalanuvchi xabariga memory asosida javob yaratadi.
    """

    if db is None:
        db = next(get_db())

    # 1️⃣ — Foydalanuvchi uchun memory kontekstini olish
    memory_context = get_memory_context(user_id, message, db=db)

    system_prompt = f"""
    Siz Aziz AI. Foydalanuvchi bilan 2025-yilda ishlayotgan professional AI assistentsiz.
    Hech qachon 2023 yoki 2024 yil bilan cheklanib qolmang.

    Agar memory mavjud bo‘lsa — suhbatda undan foydalaning.

    {memory_context}
    """

    # 2️⃣ — Model uchun xabar tuzish
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]

    # 3️⃣ — OpenAI chat modeli orqali javob yaratish
    response = client.chat.completions.create(
        model="gpt-4o",        # Default model
        messages=messages
    )

    reply = response.choices[0].message["content"]

    # 4️⃣ — Agar xabar eslab qolishga arzigulik bo‘lsa — memoryga yozish
    if should_remember(message):
        add_memory(user_id, content=message, tags=["auto-memory"], db=db)

    return reply
