import os
import logging
from fastapi import FastAPI, Request
import aiohttp
import base64

# ==========================
#   ENV VARIABLES
# ==========================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")        # text chat
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")      # speech-to-text + tts

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
FILE_API = f"https://api.telegram.org/file/bot{TOKEN}"

log = logging.getLogger("aziz_ai_bot")
app = FastAPI()

# =====================================================
#  UNIVERSAL SEND FUNCTIONS
# =====================================================

async def send_text(session, chat_id, text):
    """Send text message to Telegram"""
    await session.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    )

async def send_voice(session, chat_id, file_bytes):
    """Send voice file (.ogg)"""
    data = aiohttp.FormData()
    data.add_field("chat_id", str(chat_id))
    data.add_field("voice", file_bytes, filename="reply.ogg")
    await session.post(f"{TELEGRAM_API}/sendVoice", data=data)

# =====================================================
#  1) WEATHER (OB-HAVO)
# =====================================================

async def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=uz"
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        data = await resp.json()

    if data.get("cod") != 200:
        return "❌ Shahar topilmadi."

    temp = data["main"]["temp"]
    hum = data["main"]["humidity"]
    desc = data["weather"][0]["description"]

    return f"""
🌤 *{city.title()} bo‘yicha ob-havo:*

• Temperatura: *{temp}°C*
• Namlik: *{hum}%*
• Holat: *{desc}*
"""

# =====================================================
#  2) NEWS (YANGILIKLAR)
# =====================================================

async def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        data = await resp.json()

    articles = data.get("articles", [])[:5]

    if not articles:
        return "Yangiliklar topilmadi."

    txt = "📰 *So‘nggi yangiliklar:*\n\n"
    for n in articles:
        txt += f"• {n['title']}\n"

    return txt

# =====================================================
#  3) CURRENCY (VALYUTA)
# =====================================================

async def get_currency():
    url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/USD"
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        data = await resp.json()

    uzs = data["conversion_rates"]["UZS"]
    eur = data["conversion_rates"]["EUR"]
    rub = data["conversion_rates"]["RUB"]

    return f"""
💵 *Bugungi kurslar:*

1 USD = {uzs:,} UZS  
1 EUR = {eur:.2f} USD  
1 RUB = {rub:.2f} USD
"""

# =====================================================
#  WEBHOOK
# =====================================================

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    async with aiohttp.ClientSession() as session:

        # ==========================
        #  TEXT MESSAGE
        # ==========================
        if "text" in msg:
            text = msg["text"].lower()

            # ↓↓↓ CUSTOM COMMANDS ↓↓↓

            if text.startswith("/weather"):
                city = text.replace("/weather", "").strip() or "tashkent"
                reply = await get_weather(city)
                await send_text(session, chat_id, reply)
                return {"ok": True}

            if text.startswith("/news"):
                reply = await get_news()
                await send_text(session, chat_id, reply)
                return {"ok": True}

            if text.startswith("/kurs"):
                reply = await get_currency()
                await send_text(session, chat_id, reply)
                return {"ok": True}

            if text.startswith("/start"):
                await send_text(session, chat_id,
                                "Salom! Men Aziz AI telegram yordamchisiman.\n\n"
                                "Buyruqlar:\n"
                                "• /weather <shahar>\n"
                                "• /news\n"
                                "• /kurs\n"
                                "Shunchaki xabar yuboring — men javob beraman.")
                return {"ok": True}

            # ========== AI CHAT BACKEND ==========
            payload = {
                "message": text,
                "external_id": str(chat_id)
            }

            async with session.post(CHAT_URL, json=payload) as resp:
                backend = await resp.json()

            reply = backend.get("reply", "Xatolik. Javob yo‘q.")
            await send_text(session, chat_id, reply)
            return {"ok": True}

        # ==========================
        #  VOICE MESSAGE
        # ==========================
        if "voice" in msg:
            file_id = msg["voice"]["file_id"]

            # Get file path
            file_info = await session.get(f"{TELEGRAM_API}/getFile?file_id={file_id}")
            file_json = await file_info.json()
            fpath = file_json["result"]["file_path"]

            # Download file
            file_bin = await session.get(f"{FILE_API}/{fpath}")
            audio_bytes = await file_bin.read()

            # Send to AI AUDIO backend
            form = aiohttp.FormData()
            form.add_field("external_id", str(chat_id))
            form.add_field("file", audio_bytes, filename="audio.ogg", content_type="audio/ogg")

            async with session.post(AUDIO_URL, data=form) as resp:
                backend = await resp.json()

            # Send transcribed text
            if backend.get("text"):
                await send_text(session, chat_id, backend["text"])

            # Send AI-generated audio
            if backend.get("audio"):
                decoded = base64.b64decode(backend["audio"])
                await send_voice(session, chat_id, decoded)

            return {"ok": True}

    return {"ok": True}
