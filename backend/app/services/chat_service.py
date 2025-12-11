# app/services/chat_service.py
import asyncio
import aiohttp
from sqlalchemy.orm import Session
from app.config import OPENAI_API_KEY
from app.config import WEATHER_API_KEY, NEWS_API_KEY

# -----------------------------------------
# REALTIME MA'LUMOT FUNKSIYASI (Ixtiyoriy bo‘lim)
# -----------------------------------------
async def get_realtime_info(message: str):
    message_lower = message.lower()

    if any(k in message_lower for k in ["ob-havo", "havo", "weather"]):
        return "Hozirgi ob-havo bo‘yicha real ma’lumot olish xizmati ulanmagan."

    if any(k in message_lower for k in ["yangilik", "news"]):
        return "So‘nggi yangiliklarni olish funksiyasi faol emas."

    return None


# -----------------------------------------
# ASOSIY JAVOB GENERATSIYASI
# -----------------------------------------
async def _generate_reply(message: str, personality: str = "") -> str:
    """
    AI’dan tekst javob yaratish (async)
    """
    import openai
    openai.api_key = OPENAI_API_KEY

    prompt = f"""
Sen — Aziz AI. Professional yordamchi.
Foydalanuvchi shaxsiy profili:
{personality}

Xabar: {message}
Javobni samimiy, aniq va qisqa qilib yoz.
"""

    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message["content"]


# -----------------------------------------
# SYNC FUNKSIYA — Router shu funksiyani chaqiradi
# -----------------------------------------
def create_chat_reply(db: Session, external_id: str, message: str) -> str:
    """
    Bu funksiya FastAPI router tomonidan chaqiriladi.
    Ichida async kodni boshqarish uchun asyncio.run ishlatiladi.
    """

    # 1) Realtime tekshiruv
    try:
        realtime = asyncio.run(get_realtime_info(message))
        if realtime:
            return realtime
    except Exception as e:
        print("Realtime xato:", e)

    # 2) AI javob yaratish
    try:
        reply = asyncio.run(_generate_reply(message))
        return reply
    except Exception as e:
        print("AI xato:", e)
        return "⚠️ Javob yaratishda xatolik yuz berdi."
