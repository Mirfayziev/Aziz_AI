from typing import Tuple

from sqlalchemy.orm import Session

from ..config import get_openai_client, get_settings
from ..models import UserProfile
from .memory_service import get_or_create_user, store_memory, search_memories

settings = get_settings()
client = get_openai_client()


def _select_model(tier: str) -> str:
    tier = (tier or "default").lower()
    if tier == "deep":
        return settings.MODEL_DEEP
    if tier == "fast":
        return settings.MODEL_FAST
    return settings.MODEL_DEFAULT


def build_system_prompt(user: UserProfile) -> str:
    return (
        "Sen Aziz AI Pro – foydalanuvchi Azizning shaxsiy assistentisan. "
        "Har doim hurmat bilan, tushunarli va qisqa javob ber. "
        "Tilni foydalanuvchining xabariga mos tanla (o'zbek/rus/ingliz). "
        "Agar foydalanuvchi reja, maqsad, odatlar haqida gapirsa, "
        "bu ma'lumotlarni xotirada saqlaysan va keyingi javoblarda hisobga olasan."
    )


def create_chat_reply(
    db: Session,
    external_user_id: str,
    message: str,
    model_tier: str = "default",
) -> Tuple[str, str]:
    """
    Asosiy chat logikasi: user + memory + OpenAI.
    return: (reply_text, used_model_name)
    """
    user: UserProfile = get_or_create_user(db, external_user_id)

    # 1) Memorydan tegishli xotiralarni topamiz
    similar_mems = search_memories(db, user, message, limit=6)
    memory_context_parts = [f"- {m.content}" for m, score in similar_mems if score > 0.3]
    memory_context = "\n".join(memory_context_parts) if memory_context_parts else ""

    system_prompt = build_system_prompt(user)

    messages = [{"role": "system", "content": system_prompt}]
    if memory_context:
        messages.append(
            {
                "role": "system",
                "content": "Foydalanuvchi haqida eslab qolingan muhim ma'lumotlar:\n"
                + memory_context,
            }
        )

    messages.append({"role": "user", "content": message})

    model_name = _select_model(model_tier)

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
    )

    reply = completion.choices[0].message.content.strip()

    # 2) Memoryga yozib qo'yamiz
    store_memory(
        db,
        user=user,
        content=message,
        metadata={"role": "user"},
        embed=True,
    )
    store_memory(
        db,
        user=user,
        content=reply,
        metadata={"role": "assistant"},
        embed=True,
    )

    return reply, model_name
