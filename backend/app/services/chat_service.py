from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List

from app.services.realtime_service import get_realtime_data
from app.services.openai_client import openai_client
from app.services.memory_service import memory_service

# ✅ AZIZ AI CORE PROMPT ID
AZIZ_CORE_PROMPT_ID = "pmpt_69450c3550c881959870cfc5353c0d730e213568481dfbc7"


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

    # 3️⃣ FINAL INPUT (REAL TIME + USER + MEMORY + CONTEXT)
    parts = [
        _tashkent_now_block(),
        "USER MESSAGE:",
        user_text,
    ]

    if memory_block:
        parts += ["", memory_block]

    if context:
        parts += ["", "ADDITIONAL CONTEXT:", context.strip()]

    final_input = "\n".join(parts).strip()

    # 4️⃣ OPENAI — PROMPT ID ORQALI (MODEL 5.x)
    response = await openai_client.responses.create(
        model="gpt-5.2-pro",
        prompt={
            "id": AZIZ_CORE_PROMPT_ID,
            "version": "1",
        },
        input=final_input,
        max_output_tokens=900,
    )

    answer = (getattr(response, "output_text", "") or "").strip()

    # fallback (ba'zi klientlarda output_text bo'lmasligi mumkin)
    if not answer:
        try:
            answer = (response.output[0].content[0].text or "").strip()
        except Exception:
            answer = ""

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
