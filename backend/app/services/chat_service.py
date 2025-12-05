import json
from sqlalchemy.orm import Session
from openai import OpenAI

from app.db import get_db
from app.services.memory_service import (
    get_memory_context,
    should_remember,
    add_memory
)

client = OpenAI()


def create_chat_reply(user_id: int, message: str, db: Session = None):
    if db is None:
        db = next(get_db())

    memory_context = get_memory_context(user_id, message, db=db)

    system_prompt = f"""
    Siz Aziz AI. Siz 2025-yilda ishlayapsiz. 
    Hech qachon 2023 yoki 2024 yil bilan cheklanib qolmang. 
    Foydalanuvchi uchun shaxsiy yordamchi sifatida aniq, zamonaviy javoblar bering.

    Agar foydalanuvchining memory’si bo‘lsa — undan foydalaning.

    {memory_context}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    reply = response.choices[0].message["content"]

    if should_remember(message):
        add_memory(user_id, content=message, tags=["auto-memory"], db=db)

    return reply
