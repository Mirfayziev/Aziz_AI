import os
import requests
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

import openai

# ================= ENV =================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

openai.api_key = OPENAI_API_KEY

# ================= APP =================
app = FastAPI()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("aziz_ai_bot")

# ================= HELPERS =================
def send_message(chat_id: int, text: str):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def send_voice(chat_id: int, audio_bytes: bytes):
    requests.post(
        f"{TELEGRAM_API}/sendVoice",
        data={"chat_id": chat_id},
        files={"voice": ("voice.ogg", audio_bytes, "audio/ogg")}
    )

# ================= SERVICES =================
def get_weather(city="Tashkent"):
    try:
        return requests.get(f"https://wttr.in/{city}?format=3", timeout=10).text
    except:
        return "❌ Ob-havo xizmati ishlamayapti."

def get_currency():
    try:
        data = requests.get("https://cbu.uz/ru/arkhiv-kursov-valyut/json/").json()
        usd = next(x for x in data if x["Ccy"] == "USD")["Rate"]
        eur = next(x for x in data if x["Ccy"] == "EUR")["Rate"]
        rub = next(x for x in data if x["Ccy"] == "RUB")["Rate"]
        return f"💱 Valyuta:\nUSD: {usd}\nEUR: {eur}\nRUB: {rub}"
    except:
        return "❌ Valyuta ma’lumotlari mavjud emas."

def get_news():
    try:
        r = requests.get(
            f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=uz"
        ).json()
        news = r.get("results", [])[:5]
        text = "📰 So‘nggi yangiliklar:\n\n"
        for n in news:
            text += f"• {n['title']}\n"
        return text
    except:
        return "❌ Yangiliklarni olishda xatolik."

# ================= AI =================
def ai_answer(prompt: str) -> str:
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sen Aziz AI. Javoblaring aniq, muloyim va foydali bo‘lsin."},
            {"role": "user", "content": prompt}
        ]
    )
    return resp.choices[0].message.content

def ai_voice(text: str) -> bytes:
    audio = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    return audio.read()

# ================= WEBHOOK =================
class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[dict] = None

@app.post("/webhook")
async def webhook(update: TelegramUpdate):
    if not update.message:
        return {"ok": True}

    chat_id = update.message["chat"]["id"]
    text = update.message.get("text", "").lower()

    log.info(f"Message: {text}")

    # ---- Commands ----
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

    if text == "ob-havo":
        send_message(chat_id, get_weather())
        return {"ok": True}

    if text == "valyuta":
        send_message(chat_id, get_currency())
        return {"ok": True}

    if text == "yangilik":
        send_message(chat_id, get_news())
        return {"ok": True}

    if text == "audio":
        answer = "Salom! Men Aziz AI. Ovozli javob berishga tayyorman."
        send_voice(chat_id, ai_voice(answer))
        return {"ok": True}

    # ---- AI CHAT ----
    answer = ai_answer(text)
    send_message(chat_id, answer)

    # optional voice
    voice = ai_voice(answer)
    send_voice(chat_id, voice)

    return {"ok": True}
