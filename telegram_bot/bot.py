import os
from io import BytesIO

import requests
from fastapi import FastAPI, Request
from openai import OpenAI

API_URL = os.getenv("AZIZ_BACKEND_CHAT_URL", "http://backend:8000/api/chat/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI()


def send_text(chat_id: int, text: str):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )


def send_voice(chat_id: int, text: str):
    if not OPENAI_API_KEY:
        return

    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )

    audio_bytes = speech.to_bytes()

    files = {"voice": ("reply.ogg", audio_bytes, "audio/ogg")}
    requests.post(
        f"{TELEGRAM_API}/sendVoice",
        data={"chat_id": chat_id},
        files=files,
        timeout=20,
    )


def transcribe_voice(file_bytes: bytes) -> str:
    audio_file = BytesIO(file_bytes)
    audio_file.name = "voice.ogg"

    resp = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=audio_file,
    )

    return resp.text


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    # VOICE → TEXT
    if "voice" in msg and TELEGRAM_BOT_TOKEN and OPENAI_API_KEY:
        try:
            file_id = msg["voice"]["file_id"]

            file_info = requests.get(
                f"{TELEGRAM_API}/getFile",
                params={"file_id": file_id},
                timeout=10,
            ).json()

            file_path = file_info["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"

            file_bytes = requests.get(file_url, timeout=20).content
            text = transcribe_voice(file_bytes)

        except Exception:
            text = "(ovozni o'qishda xato)"
    else:
        text = msg.get("text") or ""

    # /START — PREMIUM WELCOME
    if text.lower().startswith("/start"):
        welcome = (
            "✨ *Assalomu alaykum, Aziz!*\n\n"
            "Men — **Aziz AI**, sizning shaxsiy sun'iy intellekt yordamchingiz.\n"
            "Men sizning odatlaringizni, uslublaringizni va ehtiyojlaringizni asta-sekin o‘rganaman.\n\n"
            "💡 Men nima qila olaman?\n"
            "— Savollaringizga inson darajasida javob berish\n"
            "— Kun tartibi va rejalarni yaratish\n"
            "— Fikringizni tartibga solish\n"
            "— Ovoz bilan suhbatlashish\n\n"
            "🧠 *Aziz, men endi doimo yoningizdan joy oldim.*\n"
            "Xohlagan savolingizni yozing yoki ovoz yuboring 👇"
        )

        send_text(chat_id, welcome)
        return {"ok": True}

    # BACKEND → CHAT RESPONSE
    try:
        r = requests.post(API_URL, json={"chat_id": str(chat_id), "message": text}, timeout=60)

        if r.status_code == 200:
            reply = r.json().get("reply", "Javobni o‘qib bo‘lmadi.")
        else:
            reply = f"Backend xato: {r.text}"

    except Exception as e:
        reply = f"Backendga ulanishda xato: {e}"

    # SEND TEXT
    send_text(chat_id, reply)

    # OPTIONAL: SEND VOICE
    try:
        send_voice(chat_id, reply)
    except Exception:
        pass

    return {"ok": True}
