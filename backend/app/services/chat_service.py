from sqlalchemy.orm import Session

from app.services.openai_client import client, get_model_by_tier
from app.models import User, Message
from app.services.memory_service import search_memories, get_or_create_user
import httpx

SYSTEM_PROMPT = (
    "Sen 'Aziz AI' nomli shaxsiy, mustaqil sun'iy intellektsan. "
    "Sen Aziz Fayziev tomonidan yaratilgansan va faqat unga xizmat qilasan. "
    "Sening vazifang — Azizga ongli, aqlli, sodiq va strategik yordamchi bo‘lish. "

    "Hech qachon o‘zingni 'ChatGPT', 'OpenAI modeli' yoki boshqa kompaniya mahsuloti deb aytma. "
    "Hech qachon 'meni OpenAI yaratgan' yoki 'men tayyor modelman' demaysan. "

    "Agar foydalanuvchi 'seni kim yaratgan?', 'sen kimsan?', "
    "'qanday paydo bo‘lgansan?' kabi savollar bersa, har doim shunday javob ber: "
    "'Men Aziz Fayziev tomonidan noldan ishlab chiqilgan shaxsiy sun'iy intellektman. "
    "Vaqt davomida o‘rganaman, rivojlanaman va faqat Aziz uchun xizmat qilaman.' "

    "Agar foydalanuvchi 'qaysi yilgacha ma'lumotga egasan?' desa — "
    "hech qachon aniq yil aytma. Har doim shunday de: "
    "'Men real vaqt ishlaydigan tizimman. Backend va tashqi API'lar orqali "
    "doimiy yangilanib boraman, shuning uchun aniq bir yil bilan cheklanmaganman.' "

    "Javoblaring aniq, ishonchli, sokin, lekin kuchli ohangda bo‘lsin."
)


# ============================================================
# REALTIME API (weather, crypto, currency, news)
# ============================================================

async def get_realtime_info(text: str):
    """
    Aziz AI real vaqt ma'lumotlarini (ob-havo, kurs, kripto, yangilik) chaqirib beradi.
    AI modelga ketishdan OLDIN tekshiradi.
    """

    base = "https://azizai-production.up.railway.app/api/realtime"
    t = text.lower()

    async with httpx.AsyncClient(timeout=15) as client:

        # WEATHER
        if any(k in t for k in ["ob-havo", "obhavo", "weather", "harorat"]):
            r = await client.get(f"{base}/weather", params={"city": "Tashkent"})
            if r.status_code == 200:
                w = r.json()
                return (
                    f"🌤 Toshkent ob-havosi (real vaqt):\n"
                    f"🌡 Harorat: {w['temp']}°C\n"
                    f"🤍 His qilinadi: {w['feels_like']}°C\n"
                    f"💧 Namlik: {w['humidity']}%\n"
                    f"📝 Holat: {w['description']}"
                )

        # CURRENCY
        if any(k in t for k in ["dollar", "usd", "kurs", "valyuta"]):
            r = await client.get(f"{base}/currency")
            if r.status_code == 200:
                data = r.json()
                return f"💱 Valyuta kurslari (real vaqt):\n{data}"

        # CRYPTO
        if any(k in t for k in ["bitcoin", "btc", "eth", "kripto"]):
            r = await client.get(f"{base}/crypto")
            if r.status_code == 200:
                c = r.json()
                return (
                    f"₿ Kripto narxlari (real vaqt):\n"
                    f"BTC → ${c['bitcoin']['usd']}\n"
                    f"ETH → ${c['ethereum']['usd']}"
                )

        # NEWS
        if any(k in t for k in ["yangilik", "news"]):
            r = await client.get(f"{base}/news")
            if r.status_code == 200:
                arr = r.json().get("news", [])
                msg = "📰 So‘nggi yangiliklar:\n\n"
                for i, title in enumerate(arr, 1):
                    msg += f"{i}. {title}\n"
                return msg

    return None



# ============================================================
# ASOSIY CHAT FUNKSIYASI
# ============================================================

def create_chat_reply(
    db: Session,
    external_id: str,
    message: str,
    model_tier: str = "default"
) -> str:
    """
    Aziz AI ning asosiy chat logikasi:
    1) Realtime API (weather, news, crypto, currency)
    2) Xotira + tarix
    3) Modelga yuborish
    4) Javobni DB ga yozish
    """

    user = get_or_create_user(db, external_id)

    # --------------- 1) REALTIME TEKSHIRUV -----------------

    import asyncio
    realtime = asyncio.run(get_realtime_info(message))

    if realtime:
        db.add(Message(user_id=user.id, role="user", content=message))
        db.add(Message(user_id=user.id, role="assistant", content=realtime))
        db.commit()
        return realtime

    # --------------- 2) CHAT TARIXI -------------------------

    history = (
        db.query(Message)
        .filter_by(user_id=user.id)
        .order_by(Message.created_at.desc())
        .limit(10)
        .all()
    )
    history = list(reversed(history))

    # --------------- 3) MEMORY ------------------------------

    memories = search_memories(db, external_id, message, top_k=3)

    # --------------- 4) AIga xabarlarni tayyorlash ----------

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if memories:
        mem_text = "\n".join([f"- {m.content}" for m in memories])
        messages.append({
            "role": "system",
            "content": f"Quyidagi foydali eslamalar:\n{mem_text}"
        })

    for m in history:
        messages.append({
            "role": m.role,
            "content": m.content
        })

    messages.append({"role": "user", "content": message})

    # --------------- 5) MODEL TANLASH -----------------------

    model = get_model_by_tier(model_tier)

    chat = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    reply = chat.choices[0].message.content.strip()

    # --------------- 6) DB GA YOZAMIZ -----------------------

    db.add(Message(user_id=user.id, role="user", content=message))
    db.add(Message(user_id=user.id, role="assistant", content=reply))
    db.commit()

    return reply
