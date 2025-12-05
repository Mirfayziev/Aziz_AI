from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    # Start komandasiga javob
    if msg.get("text") == "/start":
        send_message(chat_id, 
            "✨ *AzizAI — Sizning shaxsiy sun’iy intellekt yordamchingiz!* \n\n"
            "Menga bemalol savol yuboring 😊"
        )
        return {"ok": True}

    # TEXT message
    if "text" in msg:
        user_text = msg["text"]

        backend_resp = requests.post(
            CHAT_URL,
            json={"message": user_text},
            timeout=20
        ).json()

        # TO‘G‘RI KALIT 🔥
        reply = backend_resp.get("response", "⚠️ Backend javob bermadi")

        send_message(chat_id, reply)

    return {"ok": True}

@app.get("/")
def home():
    return {"status": "running"}
