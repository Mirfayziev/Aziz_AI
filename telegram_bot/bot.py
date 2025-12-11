import os
import requests
import json
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional

# ===== ENV VARIABLES =====
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("AZIZAI_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()
log = logging.getLogger("bot")
log.setLevel(logging.INFO)

# -------------------------------
# Telegram helper sender
# -------------------------------
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def send_voice(chat_id, audio_bytes):
    url = f"{TELEGRAM_API}/sendVoice"
    files = {"voice": ("audio.ogg", audio_bytes, "audio/ogg")}
    data = {"chat_id": chat_id}
    requests.post(url, data=data, files=files)

# -------------------------------
# Weather API
# -------------------------------
def get_weather(city="Tashkent"):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3")
        return r.text
    except:
        return "Ob-havo xizmatida xatolik."

# -------------------------------
# Currency API
# -------------------------------
def get_currency():
    try:
        r = requests.get("https://cbu.uz/ru/arkhiv-kursov-valyut/json/")
        data = r.json()
        usd = next(x for x in data if x["Ccy"] == "USD")["Rate"]
        eur = next(x for x in data if x["Ccy"] == "EUR")["Rate"]
        rub = next(x for x in data if x["Ccy"] == "RUB")["Rate"]
        return f"USD: {usd} UZS\nEUR: {eur} UZS\nRUB: {rub} UZS"
    except:
        return "Valyuta kurslarini olishda xatolik."

# -------------------------------
# News API (Google News)
# -------------------------------
def get_news():
    try:
        r = requests.get("https://newsdata.io/api/1/news?apikey=pub_54087432b0dc044bfc5&country=uz")
        news = r.json()["results"][:5]
        text = "SO‘NGI YANGILIKLAR:\n\n"
        for n in news:
            text += f"- {n['title']}\n"
        return text
    except:
        return "Yangiliklarni olishda xatolik."

# -------------------------------
# Voice generation (OpenAI)
# -------------------------------
def generate_voice(text):
    import openai
    openai.api_key = OPENAI_KEY

    audio = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    return audio.read()

# ==============================================
# TELEGRAM WEBHOOK ENDPOINT
# ==============================================
class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[dict] = None

@app.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    log.info(f"Update: {update.dict()}")

    if not update.message:
        return {"ok": True}

    chat_id = update.message["chat"]["id"]
    msg = update.message.get("text", "")

    # ----- COMMAND HANDLING -----
    if msg == "/start":
        send_message(chat_id, "Assalomu alaykum! Men Aziz AI botiman.")
        return {"ok": True}

    if msg.lower() == "ob-havo":
        send_message(chat_id, get_weather())
        return {"ok": True}

    if msg.lower() == "valyuta":
        send_message(chat_id, get_currency())
        return {"ok": True}

    if msg.lower() == "yangilik":
        send_message(chat_id, get_news())
        return {"ok": True}

    if msg.lower() == "audio":
        voice = generate_voice("Salom, men Aziz AI botman. Ovozli javob tayyor!")
        send_voice(chat_id, voice)
        return {"ok": True}

    # Default reply
    reply = f"Siz yozdingiz: {msg}"
    send_message(chat_id, reply)

    return {"ok": True}
