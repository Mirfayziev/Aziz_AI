import os
import requests
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import openai

# ================== ENV ==================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

openai.api_key = OPENAI_API_KEY

# ================== APP ==================
app = FastAPI()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("aziz_ai_bot")

# ================== TELEGRAM ==================
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def send_voice(chat_id, audio):
    requests.post(
        f"{TELEGRAM_API}/sendVoice",
        data={"chat_id": chat_id},
        files={"voice": ("voice.ogg", audio, "audio/ogg")}
    )

# ================== SERVICES ==================
def get_weather(city="Tashkent"):
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": WEATHER_API_KEY,
                "units": "metric",
                "lang": "uz"
            },
            timeout=10
        ).json()

        return (
            f"🌤 Ob-havo ({city}):\n"
            f"Harorat: {r['main']['temp']}°C\n"
            f"Holat: {r['weather'][0]['description']}\n"
            f"Namlik: {r['main']['humidity']}%"
        )
    except:
        return "❌ Ob-havo ma’lumotini olishda xatolik."

def get_currency():
    try:
        data = requests.get("https://cbu.uz/ru/arkhiv-kursov-valyut/json/").json()
        def rate(ccy): return next(x for x in data if x["Ccy"] == ccy)["Rate"]

        return (
            "💱 Valyuta kurslari:\n"
            f"USD: {rate('USD')}\n"
            f"EUR: {rate('EUR')}\n"
            f"RUB: {rate('RUB')}"
        )
    except:
        return "❌ Valyuta ma’lumotlari yo‘q."

def get_news():
    try:
        r = requests.get(
            "https://newsdata.io/api/1/news",
            params={"apikey": NEWS_API_KEY, "country": "uz"},
            timeout=10
        ).json()

        news = r.get("results", [])[:5]
        text = "📰 So‘nggi yangiliklar:\n\n"
        for n in news:
            text += f"• {n['title']}\n"
        return text
    except:
        return "❌ Yangiliklarni olishda xatolik."

# ================== AI ==================
def ai_chat(prompt):
    r = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sen Aziz AI. Muloyim, aniq va ishonchli gapir."},
            {"role": "user", "content": prompt}
        ]
    )
    return r.choices[0].message.content

def ai_tts(text):
    audio = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    return audio.read()

# ================== WEBHOOK ==================
class Update(BaseModel):
    update_id: int
    message: Optional[dict] = None

@app.post("/webhook")
async def webhook(update: Update):
    if not update.message:
        return {"ok": True}

    chat_id = update.message["chat"]["id"]
    text = update.message.get("text", "").lower()

    log.info(f"MSG: {text}")

    # ===== ROUTING =====
    if text == "/start":
        send_message(chat_id,
            "👋 Assalomu alaykum!\n"
            "Men Aziz AI.\n\n"
            "Buyruqlar:\n"
            "• ob-havo\n"
            "• valyuta\n"
            "• yangilik\n"
            "• audio"
        )
        return {"ok": True}

    if "havo" in text:
        msg = get_weather()
    elif "valyuta" in text or "kurs" in text:
        msg = get_currency()
    elif "yangilik" in text:
        msg = get_news()
    else:
        msg = ai_chat(text)

    send_message(chat_id, msg)
    send_voice(chat_id, ai_tts(msg))

    return {"ok": True}
