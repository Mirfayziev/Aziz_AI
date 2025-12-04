import os
import requests
from fastapi import BackgroundTasks  # agar kerak bo'lsa

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

BACKEND_URL = os.getenv("AZIZ_BACKEND_CHAT_URL", "https://azizai-production.up.railway.app")

def send_text(chat_id: int, text: str):
    requests.post(f"{TG_API}/sendMessage", json={"chat_id": chat_id, "text": text})

def handle_update(update: dict):
    if "message" not in update:
        return
    msg = update["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    if text.lower().startswith("/start"):
        send_text(chat_id, "👋 Assalomu alaykum, Aziz! ✨")
        return
    # boshqa xabarlar: backend ga jo'nat
    resp = requests.post(f"{BACKEND_URL}/api/chat", json={"chat_id": chat_id, "message": text})
    if resp.ok:
        reply = resp.json().get("reply", "")
    else:
        reply = "Server bilan bog'lanishda xato"
    send_text(chat_id, reply)
