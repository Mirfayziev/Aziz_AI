from sqlalchemy.orm import Session, sessionmaker
from app.db import engine
from app.models import Message
from app.services.memory_service import (
    get_or_create_user,
    save_memory,
    search_memory
)
from openai import OpenAI

client = OpenAI()
SessionLocal = sessionmaker(bind=engine)


def create_chat_reply(user_external_id: str, text: str):
    db = SessionLocal()

    # 1) Foydalanuvchi olish/yaratish
    user = get_or_create_user(db, external_id=user_external_id)

    # 2) Xabarni saqlash
    msg = Message(user_id=user.id, role="user", content=text)
    db.add(msg)
    db.commit()

    # 3) Xotiradan mos ma’lumotlarni olish
    memories = search_memory(db, user.id, text)
    memory_text = "\n".join([m.content for m in memories])

    # 4) Xotiraga yangi narsani qo‘shish
    if len(text.split()) > 3:
        save_memory(db, user.id, text, tags=["conversation"])

    # 5) AI modeldan javob
    prompt = f"""
User message:
{text}

Relevant memories:
{memory_text}

Respond naturally as Aziz AI assistant.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    reply_text = response.choices[0].message["content"]

    # 6) Javobni tarixga yozish
    bot_msg = Message(user_id=user.id, role="assistant", content=reply_text)
    db.add(bot_msg)
    db.commit()

    db.close()
    return reply_text
