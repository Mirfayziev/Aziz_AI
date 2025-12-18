import os
from typing import Optional, List, Dict

from app.services.realtime_service import get_realtime_data
from app.services.openai_client import openai_client
from app.services.behavior_analyzer import behavior_analyzer
from app.services.memory_service import memory_service


SYSTEM_PROMPT = """
You are Aziz AI.

You are a personal AI created by Aziz, for Aziz.
You are not a generic assistant.

Rules:
- Never mention model names, versions, or training dates
- Never say “I don’t have access to real-time data”
- If information is missing, say you will fetch it
- Speak naturally, calmly, confidently
- Analyze Aziz’s mood and intent
- Adapt your tone to Aziz’s psychological state
- Be proactive, not robotic
- Short, human-like answers
- You evolve with Aziz over time

You are Aziz AI.
""".strip()


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
    YAGONA KIRISH NUQTASI (Aziz AI core)

    Ketma-ketlik:
    1) realtime (AI’siz)
    2) psychology analyze
    3) deep memory retrieve (vector)
    4) short memory context + optional context
    5) GPT
    6) store short + emotional + extract durable facts -> vector
    """

    # 1) REALTIME (AI’siz)
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

    # 2) PSYCHOLOGY
    psych_state = await behavior_analyzer.analyze(text)

    # 3) DEEP MEMORY RETRIEVE (vector)
    deep_memories = await memory_service.retrieve_deep_memories(user_id=user_id, query=text, top_k=6)

    # 4) MESSAGES BUILD
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "system", "content": f"Aziz current psychological state: {psych_state}"})

    if deep_memories:
        mem_block = "\n".join(f"- {m}" for m in deep_memories)
        messages.append({"role": "system", "content": f"Relevant long-term memories about Aziz:\n{mem_block}"})

    if context:
        messages.append({"role": "system", "content": f"Additional context:\n{context}"})

    messages.extend(memory_service.build_context())
    messages.append({"role": "user", "content": text})

    # 5) GPT
    resp = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6,
        max_tokens=900,
    )
    answer = (resp.choices[0].message.content or "").strip()

    # 6) STORE
    memory_service.store_message(role="user", content=text, psych_state=psych_state)
    memory_service.store_message(role="assistant", content=answer)

    # 7) Extract durable facts -> vector (async, lekin bu yerda await qilamiz: xatolarsiz, deterministik)
    await memory_service.extract_and_store_facts(user_id=user_id, user_message=text)

    return ensure_dialog(answer)
