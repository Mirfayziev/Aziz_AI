import os
from typing import Optional
from openai import AsyncOpenAI

from app.services.realtime_service import get_realtime_data

# ======================================================
# OpenAI CLIENT (FAQAT SHU YERDA)
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
- Be proactive, not robotic
- Short, human-like answers
- You are evolving with Aziz over time

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
    """Ob-havoni AI’siz, to‘g‘ridan-to‘g‘ri formatlaydi."""
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
# MARKAZIY CHAT FUNKSIYA (YAGONA KIRISH NUQTASI)
# ======================================================

async def chat_with_ai(
    text: str,
    context: Optional[str] = None
) -> str:
    """
    AZIZ AI MARKAZIY MIYASI

    QOIDA:
    - Real-time (ob-havo, yangiliklar) → AI chetlab o‘tiladi
    - Faqat real raqamlar qaytariladi
    - Qolgan hamma savollarda AI ishlaydi
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
            data = realtime["data"]
            return (
                f"Kripto narxlari:\n"
                f"BTC: ${data.get('BTC_USD')}\n"
                f"ETH: ${data.get('ETH_USD')}\n\n"
                "Yana qaysi aktivni ko‘raylik?"
            )

        if realtime["type"] == "currency":
            data = realtime["data"]
            return (
                f"Bugungi kurslar:\n"
                f"USD → UZS: {data['USD_UZS']}\n"
                f"EUR → UZS: {data['EUR_UZS']}\n"
                f"RUB → UZS: {data['RUB_UZS']}\n\n"
                "Yana nimani tekshiray?"
            )

    # ==================================================
    # 2️⃣ AI (REAL-TIME BO‘LMASA)
    # ==================================================
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context:
        messages.append({
            "role": "system",
            "content": f"Kontekst:\n{context}"
        })

    messages.append({"role": "user", "content": text})

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
        max_tokens=900
    )

    answer = response.choices[0].message.content.strip()
    return ensure_dialog(answer)

