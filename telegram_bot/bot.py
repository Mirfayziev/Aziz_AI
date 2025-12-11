import os
import logging
from fastapi import FastAPI, Request
import aiohttp
import base64

# =============================
#  ENV VARIABLES
# =============================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")       # Text chat (AI)
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")     # Audio → text → audio

WEATHER_API_KEY  = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY     = os.getenv("NEWS_API_KEY")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
FILE_API     = f"https://api.telegram.org/file/bot{TOKEN}"

log = logging.getLogger("aziz_ai_bot")
app = FastAPI()

# ============================================================
#  YORDAMCHI: MATN JO'NATISH
# ============================================================

async def send_text(session, chat_id, text):
    await session.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    )

# ============================================================
#  YORDAMCHI: AUDIO JO'NATISH (ogg)
# ============================================================

async def send_voice(session, chat_id, file_bytes):
    form = aiohttp.FormData()
    form.add_field("chat_id", str(chat_id))
    form.add_field("voice", file_bytes, filename="voice.ogg", content_type="audio/ogg")

    await session.post(f"{TELEGRAM_API}/sendVoice", data=form)

# ============================================================
#   OB-HAVO FUNKSIYASI
# ============================================================

async def get_weather(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=uz"
    )

    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        data = await resp.json()

    if data.get("cod") != 200:
        return "Shahar topilmadi!"

    temp = data["main"]["temp"]
    hum  = data["main"]["humidity"]
    desc = data["weather"][0]["description"]

    return f"""
🌦 *Ob-havo: {city.title()}*

• Temperatura: *{temp}°C*
• Namlik: *{hum}%*
• Holat: *{desc}*
"""

# ============================================================
#   YANGILIKLAR
# ============================================================

async def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        data = await resp.json()

    articles = data.get("articles", [])[:5]
    if not articles:
        return "Yangiliklar topilmadi!"

    text = "📰 *So‘nggi yangiliklar:*\n\n"
    for a in articles:
        text += f"• {a['title']}\n"

    return text

# ============================================================
#   VALYUTA KURSLARI
# ============================================================

async def get_currency():
    url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/USD"

    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        data = await resp.json()

    rates = data.get("conversion_rates", {})

    return f"""
💵 *Bugungi USD kurslari:*

1 USD = {rates.get('UZS', 0):,} UZS  
1 EUR = {rates.get('EUR', 0):.2f} USD  
1 RUB = {rates.get('RUB', 0):.2f} USD
"""

# ============================================================
#  TELEGRAM WEBHOOK
# ============================================================

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    async with aiohttp.ClientSession() as session:

        # ========================
        #  TEXT MESSAGE
        # ========================
        if "text" in msg:
            text = msg["text"].strip().lower()

            # weather
            if text.startswith("/weather"):
                city = text.replace("/weather", "").strip() or "tashkent"
                reply = await get_weather(city)
                await send_text(session, chat_id, reply)
                return {"ok": True}

            # news
            if text.startswith("/news"):
                reply = await get_news()
                await send_text(session, chat_id, reply)
                return {"ok": True}

            # currency
            if text.startswith("/kurs"):
                reply = await get_currency()
                await send_text(session, chat_id, reply)
                return {"ok": True}

            # =====================
            #  AI TEXT RESPONSE
            # =====================
            payload = {
                "message": text,
                "external_id": str(chat_id)
            }

            async with session.post(CHAT_URL, json=payload) as resp:
                backend = await resp.json()

            answer = backend.get("reply", "Xatolik yuz berdi.")
            await send_text(session, chat_id, answer)
            return {"ok": True}

        # ========================
        #  VOICE MESSAGE
        # ========================
        if "voice" in msg:
            file_id = msg["voice"]["file_id"]

            # getFile → path
            info = await session.get(f"{TELEGRAM_API}/getFile?file_id={file_id}")
            info_json = await info.json()
            file_path = info_json["result"]["file_path"]

            # download audio
            file_binary = await session.get(f"{FILE_API}/{file_path}")
            audio_bytes = await file_binary.read()

            # send to backend
            form = aiohttp.FormData()
            form.add_field("external_id", str(chat_id))
            form.add_field("file", audio_bytes, filename="audio.ogg", content_type="audio/ogg")

            async with session.post(AUDIO_URL, data=form) as resp:
                backend = await resp.json()

            # backend → text
            if backend.get("text"):
                await send_text(session, chat_id, backend["text"])

            # backend → audio (base64 → bytes)
            if backend.get("audio"):
                decoded = base64.b64decode(backend["audio"])
                await send_voice(session, chat_id, decoded)

            return {"ok": True}

    return {"ok": True}
