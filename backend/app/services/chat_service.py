from __future__ import annotations

import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List

from app.services.realtime_service import get_realtime_data
from app.services.openai_client import openai_client
from app.services.memory_service import memory_service

AZIZ_SYSTEM_PROMPT = (
    "You are Aziz AI, a helpful personal assistant for Aziz. "
    "Reply in the same language the user wrote in. Be concise and helpful."
)
CHAT_MODEL = os.getenv("AZIZAI_CHAT_MODEL", "gpt-4o-mini")


def format_weather(data: dict) -> str:
    return (
        f"Bugun {data['city']}da ob-havo {data['weather']}. "
        f"Harorat {data['temp']}°C, sezilishi {data['feels_like']}°C. "
        f"Namlik {data['humidity']}%."
    )


def format_news(items: list) -> str:
    lines = [f"• {n['title']}" for n in items[:5]]
    return "Bugungi asosiy yangiliklar:\n" + "\n".join(lines)


def _tashkent_now_block() -> str:
    """
    Model real vaqtni bilmaydi.
    Shuning uchun real sana/vaqtni backend o'zi beradi.
    """
    tz = ZoneInfo("Asia/Tashkent")
    now = datetime.now(tz)
    return (
        "SYSTEM CONTEXT (authoritative):\n"
        f"- Current date: {now.strftime('%Y-%m-%d')}\n"
        f"- Current time: {now.strftime('%H:%M')}\n"
        "- Timezone: Asia/Tashkent\n"
    )


async def _retrieve_memory_block(user_id: str, query: str, top_k: int = 6) -> str:
    """
    Memory bor bo'lsa ishlatamiz, lekin psychology qo'shmaymiz.
    """
    try:
        deep_memories: List[str] = await memory_service.retrieve_deep_memories(
            user_id=user_id,
            query=query,
            top_k=top_k,
        )
    except Exception:
        deep_memories = []

    if not deep_memories:
        return ""

    return "Relevant memories (use only if helpful):\n" + "\n".join(f"- {m}" for m in deep_memories)


async def chat_with_ai(
    text: str,
    context: Optional[str] = None,
    user_id: str = "aziz",
) -> str:
    """
    AZIZ AI — yagona kirish nuqtasi (toza, universal).

    Ketma-ketlik:
    1) realtime (AI’siz)
    2) memory retrieve (psychologiyasiz)
    3) OpenAI (Prompt ID)
    4) memory store
    """

    user_text = (text or "").strip()
    if not user_text:
        return "Savolingizni yozing."

    # 1️⃣ REALTIME (AI’siz)
    realtime = await get_realtime_data(user_text)
    if realtime:
        t = realtime.get("type")
        if t == "weather":
            return format_weather(realtime["data"])
        if t == "news":
            return format_news(realtime["data"])
        if t == "crypto":
            d = realtime["data"]
            return (
                "Kripto narxlari:\n"
                f"BTC: ${d.get('BTC_USD')}\n"
                f"ETH: ${d.get('ETH_USD')}"
            )
        if t == "currency":
            d = realtime["data"]
            return (
                "Bugungi kurslar:\n"
                f"USD → UZS: {d['USD_UZS']}\n"
                f"EUR → UZS: {d['EUR_UZS']}\n"
                f"RUB → UZS: {d['RUB_UZS']}"
            )

    # 2️⃣ MEMORY (psychologiyasiz)
    memory_block = await _retrieve_memory_block(user_id=user_id, query=user_text, top_k=6)

    # 3️⃣ SYSTEM CONTEXT (REAL TIME + MEMORY + CONTEXT)
    system_parts = [AZIZ_SYSTEM_PROMPT, "", _tashkent_now_block()]

    if memory_block:
        system_parts += ["", memory_block]

    if context:
        system_parts += ["", "ADDITIONAL CONTEXT:", context.strip()]

    system_prompt = "\n".join(system_parts).strip()

    # 4️⃣ OPENAI — CHAT COMPLETIONS
    response = await openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        max_tokens=900,
    )

    answer = (response.choices[0].message.content or "").strip()

    if not answer:
        answer = "Javob olinmadi."

    # 5️⃣ MEMORY STORE (psych_state YO'Q)
    try:
        memory_service.store_message(role="user", content=user_text)
        memory_service.store_message(role="assistant", content=answer)
        await memory_service.extract_and_store_facts(
            user_id=user_id,
            user_message=user_text,
        )
    except Exception:
        # memory ishlamasa ham chat ishlasin
        pass

    return answer
