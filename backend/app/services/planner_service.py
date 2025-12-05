
from sqlalchemy.orm import Session
from openai import OpenAI

from app.services.memory_service import get_or_create_user, search_memories, build_memory_context

client = OpenAI()


def create_plan(db: Session, external_user_id: str, query: str | None = None) -> str:
    user = get_or_create_user(db, external_id=external_user_id)

    base_query = query or "bugungi ishlar rejasini tuzib ber"
    mems = search_memories(db, user, base_query, limit=5)
    mem_context = build_memory_context(mems)

    prompt = f"""Siz Aziz AI nomli shaxsiy rejalashtiruvchi asistentsiz.
Foydalanuvchiga kunlik/haftalik reja tuzib berasiz.
Reja strukturalangan, punktli va vaqtlarga bo'lingan bo'lsin.

Foydalanuvchi haqidagi foydali xotiralar:
{mem_context}

So'rov:
{base_query}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    plan = completion.choices[0].message.content
    return plan
