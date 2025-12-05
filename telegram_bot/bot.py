import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")

BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{BASE}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def handle_telegram_update(update):
    if "message" not in update:
        return
    
    msg = update["message"]
    chat_id = msg["chat"]["id"]

    # /start komandasi
    if msg.get("text") == "/start":
        send_message(chat_id, 
                     "✨ *AzizAI — Sizning shaxsiy super assistentingiz!* \n\n"
                     "Menga istalgan savolni yozing 😊")
        return

    # Oddiy matn
    if "text" in msg:
        user_text = msg["text"]
        resp = requests.post(CHAT_URL, json={"message": user_text})
        answer = resp.json().get("response", "⚠️ Xatolik yuz berdi")
        send_message(chat_id, answer)
        return
