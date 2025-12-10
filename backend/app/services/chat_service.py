from sqlalchemy.orm import Session
from app.services.openai_client import client, get_model_by_tier
from app.models import User, Message
from app.services.memory_service import search_memories, get_or_create_user
import httpx
import os

# ===============================
# AZIZ AI SYSTEM PROMPT
# ===============================

SYSTEM_PROMPT = (
    "Sen 'Aziz AI' nomli shaxsiy, mustaqil sun'iy intellektsan. "
    "Sen faqat Aziz Fayziev uchun yaratilgansan va faqat unga xizmat qilasan. "

    "Hech qachon o‘zingni ChatGPT, OpenAI, Google yoki boshqa kompaniya mahsuloti deb aytma. "
    "Agar 'seni kim yaratgan?' deb so‘rashsa: "
    "'Men Aziz Fayziev tomonidan noldan ishlab chiqilgan shaxsiy sun'iy intellektman' deb javob ber. "

    "Agar 'qaysi yilgacha ma’lumotga egasan?' deyilsa: "
    "'Men real vaqt rejimida ishlaydigan tizimman, aniq bir yil bilan cheklanmaganman' deb ayt. "

    "Sen uzr so‘ramaysan. Kuchsiz gapirmaysan. Azizning shaxsiy digital hamrohisan."
)

# ===============================
# REALTIME API URLS (BACKENDDAN)
# ===============================

REALTIME_BASE = os.getenv("REALTIME_BASE_URL", "https://azizai-production.up.railway.app")

WEATHER_URL = f"{REALTIME_BASE}/api/realtime/weather"
NEWS_URL = f"{REALTIME_BASE}/api/realtime/news"
CRYPTO_URL = f"{REALTIME_BASE}/api/realtime/crypto"
CURRENCY_URL = f"{REALTIME_BASE}/api/realtime/currency"

# ===============================
# REALTIME DATA FETCHER
# ===============================

# ===============================
# REALTIME DATA FETCHER
# ===============================

async def get_realtime_info(text: str):
    text = text.lower()

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            # 💰 VALYUTA
            if any(k in text for k in ["dollar", "kurs", "valyuta", "usd", "so'm", "som"]):
                r = await client.get(CURRENCY_URL)
                return r.json()

            # ₿ KRIPTO
            if any(k in text for k in ["bitcoin", "btc", "ethereum", "kripto"]):
                r = await client.get(CRYPTO_URL)
                return r.json()

            # ☁️ OB-HAVO
            if any(k in text for k in ["ob havo", "ob-havo", "harorat", "temp"]):
                r = await client.get(WEATHER_URL)
                data = r.json()
                if isinstance(data, dict) and "main" in data:
                    return {
                        "temp": data["main"].get("temp"),
                        "feels_like": data["main"].get("feels_like"),
                        "description": data["weather"][0]["description"]
                    }
                return data

            # 📰 YANGILIK
            if any(k in text for k in ["yangilik", "news", "xabar", "so'nggi"]):
                r = await client.get(NEWS_URL)
                return r.json()

        except Exception as e:
            return {"error": str(e)}

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
            "content": f"Shaxsiy eslatmalar:\n{mem_text}"
        })

    for m in history:
        messages.append({
            "role": m.role,
            "content": m.content
        })

    messages.append({"role": "user", "content": message})

    # ===============================
    # REALTIME QO‘SHISH
    # ===============================

    realtime = None
    try:
        import asyncio
        realtime = asyncio.run(get_realtime_info(message))
    except:
        realtime = None

    if realtime and not realtime.get("error"):
        messages.append({
            "role": "system",
            "content": f"Real vaqt ma'lumotlari:\n{realtime}"
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
