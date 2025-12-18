import os
from typing import Optional, List, Dict
from openai import AsyncOpenAI

from app.services.realtime_service import get_realtime_data
from app.services.behavior_analyzer import behavior_analyzer
from app.services.memory_service import memory_service
from app.services.openai_client import openai_client

# ======================================================
# OPENAI CLIENT (FAQAT SHU YERDA)
# ======================================================

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ======================================================
# AZIZ AI — MARKAZIY SYSTEM PROMPT
# ======================================================

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
"""

# ======================================================
# YORDAMCHI FUNKSIYALAR
# ======================================================

def ensure_dialog(text: str) -> str:
    """Agar javob savolsiz tugasa, dialogni davom ettiradi."""
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

# ======================================================
# MARKAZIY CHAT FUNKSIYA — AZIZ AI MIYASI
# ======================================================

async def chat_with_ai(
    text: str,
    context: Optional[str] = None
) -> str:
    """
    AZIZ AI MARKAZIY MIYASI

    QOIDALAR:
    - Real-time (ob-havo, yangilik, kurs, kripto) → AI chetlab o‘tiladi
    - AI faqat real-time bo‘lmagan savollarda ishlaydi
    - Memory + psixologik holat har doim hisobga olinadi
    """

    # ==================================================
    # 1️⃣ REAL-TIME TEKSHIRUV (AI’siz)
    # ==================================================
    realtime = await get_realtime_data(text)

    if realtime:
        if realtime["type"] == "weather":
            return format_weather(realtime["data"])

        if realtime["type"] == "news":
            return format_news(realtime["data"])

        if realtime["type"] == "crypto":
            d = realtime["data"]
            return (
                f"Kripto narxlari:\n"
                f"BTC: ${d.get('BTC_USD')}\n"
                f"ETH: ${d.get('ETH_USD')}\n\n"
                "Yana qaysi aktivni ko‘raylik?"
            )

        if realtime["type"] == "currency":
            d = realtime["data"]
            return (
                f"Bugungi kurslar:\n"
                f"USD → UZS: {d['USD_UZS']}\n"
                f"EUR → UZS: {d['EUR_UZS']}\n"
                f"RUB → UZS: {d['RUB_UZS']}\n\n"
                "Yana nimani tekshiray?"
            )

    # ==================================================
    # 2️⃣ PSIXOLOGIK ANALIZ
    # ==================================================
    psych_state = await behavior_analyzer.analyze(text)

    # ==================================================
    # 3️⃣ MEMORY KONTEXT YIG‘ISH
    # ==================================================
    memory_context: List[Dict] = memory_service.build_context()

    # ==================================================
    # 4️⃣ GPT UCHUN XABARLAR YIG‘ISH
    # ==================================================
    messages: List[Dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": f"Aziz current psychological state: {psych_state}"
        }
    ]

    if context:
        messages.append({
            "role": "system",
            "content": f"Additional context:\n{context}"
        })

    messages.extend(memory_context)
    messages.append({"role": "user", "content": text})

    # ==================================================
    # 5️⃣ OPENAI CHAQIRUVI
    # ==================================================
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6,
        max_tokens=900
    )

    answer = response.choices[0].message.content.strip()

    # ==================================================
    # 6️⃣ MEMORY SAQLASH
    # ==================================================
    memory_service.store_message(
        role="user",
        content=text,
        psych_state=psych_state
    )
    memory_service.store_message(
        role="assistant",
        content=answer
    )

    return ensure_dialog(answer)

