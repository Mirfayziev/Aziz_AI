from sqlalchemy.orm import Session
from app.services.openai_client import client, get_model_by_tier
from app.models import User, Message
from app.services.memory_service import search_memories, get_or_create_user
from app.services.behavior_analyzer import analyze_routine
from app.models.daily_routine import DailyRoutine

import httpx
import os
import asyncio

# ===============================
# AZIZ AI SYSTEM PROMPT
# ===============================

SYSTEM_PROMPT = (
    "Sen 'Aziz AI' nomli shaxsiy, mustaqil sun'iy intellektsan. "
    "Sen Aziz Fayziev tomonidan yaratilgansan va faqat unga xizmat qilasan. "
    "Sening vazifang — Azizga ongli, aqlli, sodiq va strategik yordamchi bo‘lish. "

    "Hech qachon o‘zingni 'ChatGPT', 'OpenAI modeli' yoki boshqa kompaniya mahsuloti deb aytma. "
    "Hech qachon 'meni OpenAI yaratgan' yoki 'men tayyor modelman' demaysan. "

    "Agar foydalanuvchi 'seni kim yaratgan?', 'sen kimsan?' "
    "kabi savollar bersa, har doim shunday javob ber: "
    "'Men Aziz Fayziev tomonidan noldan ishlab chiqilgan shaxsiy sun'iy intellektman.' "

    "Agar foydalanuvchi bilim sanasi haqida so‘rasa "
    "doim shunday de: "
    "'Men real vaqt rejimida ishlaydigan tizimman, aniq yil bilan cheklanmaganman.' "

    "Javoblaring aniq, sokin, lekin ishonchli bo‘lsin."
)

# ===============================
# REALTIME BACKEND URL
# ===============================

REALTIME_BASE = os.getenv(
    "REALTIME_BASE_URL",
    "https://azizai-production.up.railway.app"
)

WEATHER_URL = f"{REALTIME_BASE}/api/realtime/weather"
NEWS_URL = f"{REALTIME_BASE}/api/realtime/news"
CRYPTO_URL = f"{REALTIME_BASE}/api/realtime/crypto"
CURRENCY_URL = f"{REALTIME_BASE}/api/realtime/currency"

# ===============================
# REALTIME DATA FETCHER
# ===============================

async def get_realtime_info(text: str):
    text = text.lower()

    async with httpx.AsyncClient(timeout=20) as http:
        try:
            # 💰 VALYUTA
            if any(k in text for k in ["dollar", "kurs", "usd", "so'm", "som"]):
                r = await http.get(CURRENCY_URL)
                return {"type": "currency", "data": r.json()}

            # ₿ KRIPTO
            if any(k in text for k in ["bitcoin", "btc", "ethereum", "kripto"]):
                r = await http.get(CRYPTO_URL)
                return {"type": "crypto", "data": r.json()}

            # ☁️ OB-HAVO
            if any(k in text for k in ["ob-havo", "obhavo", "harorat", "weather"]):
                r = await http.get(WEATHER_URL)
                return {"type": "weather", "data": r.json()}

            # 📰 YANGILIK
            if any(k in text for k in ["yangilik", "news", "xabar", "so‘nggi"]):
                r = await http.get(NEWS_URL)
                return {"type": "news", "data": r.json()}

        except Exception as e:
            return {"type": "error", "data": str(e)}

    return None

# ===============================
# CHAT CORE ENGINE
# ===============================

def create_chat_reply(
    db: Session,
    external_id: str,
    message: str,
    model_tier: str = "default"
) -> str:

    user = get_or_create_user(db, external_id)

    history = (
        db.query(Message)
        .filter_by(user_id=user.id)
        .order_by(Message.created_at.desc())
        .limit(10)
        .all()
    )
    history = list(reversed(history))

    memories = search_memories(db, external_id, message, top_k=3)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if memories:
        mem_text = "\n".join([f"- {m.content}" for m in memories])
        messages.append({
            "role": "system",
            "content": f"Shaxsiy xotiralar:\n{mem_text}"
        })

    for m in history:
        messages.append({
            "role": m.role,
            "content": m.content
        })

    messages.append({"role": "user", "content": message})

    def add_behavior_analysis(db, user_id: int, messages: list):
    routine = (
        db.query(DailyRoutine)
        .filter(DailyRoutine.user_id == user_id)
        .order_by(DailyRoutine.date.desc())
        .first()
    )

    if not routine:
        return

    analysis = analyze_routine(routine)
    analysis_text = "\n".join([f"- {item}" for item in analysis])

    messages.append({
        "role": "system",
        "content": f"Foydalanuvchining bugungi psixologik va energiya holati tahlili:\n{analysis_text}"
    })

    # ===============================
    # REALTIME QO‘SHISH
    # ===============================

    try:
        realtime = asyncio.run(get_realtime_info(message))
    except:
        realtime = None

    if realtime and realtime.get("type") != "error":
        messages.append({
            "role": "system",
            "content": f"Real vaqt ma’lumotlari:\n{realtime}"
        })

    # ===============================
    # OPENAI MODEL
    # ===============================

    model = get_model_by_tier(model_tier)

    chat = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    reply = chat.choices[0].message.content.strip()

    # ===============================
    # SAQLASH
    # ===============================

    db.add(Message(user_id=user.id, role="user", content=message))
    db.add(Message(user_id=user.id, role="assistant", content=reply))
    db.commit()

    return reply
