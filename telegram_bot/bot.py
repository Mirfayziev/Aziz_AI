import os
import requests

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_URL = os.environ["AZIZ_BACKEND_CHAT_URL"]
AUDIO_URL = os.environ["AZIZ_BACKEND_AUDIO_URL"]

BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_text(chat_id, text):
    url = f"{BASE}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def handle_update(update):
    if "message" not in update:
        return

    msg = update["message"]
    chat_id = msg["chat"]["id"]

    # START komandasi
    if "text" in msg and msg["text"].lower().startswith("/start"):
        welcome = (
            "👋 *Assalomu alaykum, Aziz!* \n\n"
            "Men — **Aziz AI**, sizning shaxsiy sun'iy intellekt yordamchingiz.\n"
            "Savollaringizni yozing yoki ovoz yuboring 🎤"
        )
        send_text(chat_id, welcome)
        return

    # Matn xabar → BACKEND CHAT API
    if "text" in msg:
        text = msg["text"]
        response = requests.post(CHAT_URL, json={"text": text})
        reply = response.json().get("reply", "Xatolik yuz berdi")
        send_text(chat_id, reply)
        return

    # Ovoz xabar → BACKEND AUDIO API
    if "voice" in msg:
        file_id = msg["voice"]["file_id"]
        response = requests.post(AUDIO_URL, json={"file_id": file_id})
        reply = response.json().get("text", "Xatolik yuz berdi")
        send_text(chat_id, reply)
        return
