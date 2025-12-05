
from sqlalchemy.orm import Session
from openai import OpenAI

from app.models import Message
from app.services.memory_service import (
    get_or_create_user,
    save_memory,
    search_memories,
    build_memory_context,
)

client = OpenAI()


def create_chat_reply(db: Session, external_user_id: str, message: str, full_name: str | None = None) -> str:
    # 1) User
    user = get_or_create_user(db, external_id=external_user_id, full_name=full_name)

    # 2) Save user message
    msg = Message(user_id=user.id, role="user", content=message)
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # 3) Relevant memories
    mems = search_memories(db, user, message, limit=8)
    mem_context = build_memory_context(mems)

    system_prompt = f"""Siz Aziz AI nomli shaxsiy yordamchisiz.
Siz foydalanuvchi bilan uzoq muddatli munosabatdasiz.
Agar kerak bo'lsa, xotiradagi kontekstdan foydalaning.

Foydalanuvchi xotirasi:
{mem_context}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    reply = completion.choices[0].message.content

    # 4) Save assistant message
    bot_msg = Message(user_id=user.id, role="assistant", content=reply)
    db.add(bot_msg)
    db.commit()

    # 5) Optionally store memory about this turn
    if len(message.split()) > 3:
        save_memory(db, user, message, tags=["conversation", "user"])
    if len(reply.split()) > 3:
        save_memory(db, user, reply, tags=["conversation", "assistant"])

    return reply
