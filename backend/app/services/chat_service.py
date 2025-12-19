from typing import Optional, List

from app.services.realtime_service import get_realtime_data
from app.services.openai_client import openai_client
from app.services.behavior_analyzer import behavior_analyzer
from app.services.memory_service import memory_service


# ✅ AZIZ AI CORE PROMPT ID
AZIZ_CORE_PROMPT_ID = "pmpt_69450c3550c881959870cfc5353c0d730e213568481dfbc7"


def ensure_dialog(text: str) -> str:
    if "?" in text:
        return text
    return text + "\n\nDavom ettiramizmi?"


def format_weather(data: dict) -> str:
    return (
        f"Bugun {data['city']}da ob-havo {data['weather']}. "
        f"Harorat {data['temp']}°C, sezilishi {data['feels_like']}°C. "
        f"Namlik {data['humidity']}%. "
        "Yana qaysi shaharni tekshiray?"
    )


def format_news(items: list) -> str:
    lines = [f"• {n['title']}" for n in items[:5]]
    return (
        "Bugungi asosiy yangiliklar:\n"
        + "\n".join(lines)
        + "\n\nQaysi birini batafsil ko‘raylik?"
    )


async def chat_with_ai(
    text: str,
    context: Optional[str] = None,
    user_id: str = "aziz",
) -> str:
    """
    AZIZ AI — YAGONA KIRISH NUQTASI

    Ketma-ketlik:
    1) realtime (AI’siz)
    2) psychology analyze
    3) long-term memory retrieve
    4) prompt input build
    5) OpenAI (Prompt ID)
    6) memory store
    """

    # 1️⃣ REALTIME (AI’siz)
    realtime = await get_realtime_data(text)
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
                f"ETH: ${d.get('ETH_USD')}\n\n"
                "Yana qaysi aktivni ko‘raylik?"
            )
        if t == "currency":
            d = realtime["data"]
            return (
                "Bugungi kurslar:\n"
                f"USD → UZS: {d['USD_UZS']}\n"
                f"EUR → UZS: {d['EUR_UZS']}\n"
                f"RUB → UZS: {d['RUB_UZS']}\n\n"
                "Yana nimani tekshiray?"
            )

    # 2️⃣ PSYCHOLOGICAL ANALYSIS
    psych_state = await behavior_analyzer.analyze(text)

    # 3️⃣ LONG-TERM MEMORY
    deep_memories: List[str] = await memory_service.retrieve_deep_memories(
        user_id=user_id,
        query=text,
        top_k=6,
    )

    memory_block = ""
    if deep_memories:
        memory_block = "Relevant memories:\n" + "\n".join(f"- {m}" for m in deep_memories)

    # 4️⃣ FINAL INPUT (PROMPT + CONTEXT)
    final_input = f"""
User message:
{text}

Psychological state:
{psych_state}

{memory_block}

{context or ""}
""".strip()

    # 5️⃣ OPENAI — PROMPT ID ORQALI
    response = await openai_client.responses.create(
        model="gpt-4.1",
        prompt={
            "id": AZIZ_CORE_PROMPT_ID,
            "version": "1",
        },
        input=final_input,
        max_output_tokens=900,
    )

    answer = (response.output_text or "").strip()

    # 6️⃣ MEMORY STORE
    memory_service.store_message(
        role="user",
        content=text,
        psych_state=psych_state,
    )
    memory_service.store_message(
        role="assistant",
        content=answer,
    )

    await memory_service.extract_and_store_facts(
        user_id=user_id,
        user_message=text,
    )

    return ensure_dialog(answer)
