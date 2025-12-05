import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


def handle_start(chat_id):
    welcome = (
        "👋 *Assalomu alaykum, Aziz!*\n\n"
        "Men – **Aziz AI**, sizning shaxsiy sun'iy intellekt yordamchingiz.\n"
        "Men sizni o‘rganaman, kundalik ishlarda yordam beraman va siz bilan birga rivojlanaman.\n\n"
        "✨ Savolingizni yozing yoki ovoz yuboring."
    )
    send_message(chat_id, welcome)


def handle_voice(chat_id, file_id):
    # Get file URL
    info = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}").json()
    file_path = info["result"]["file_path"]

    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    file_bytes = requests.get(file_url).content

    # Send to backend audio API
    resp = requests.post(AUDIO_URL, files={"file": file_bytes})

    answer = resp.json().get("text", "❌ Xatolik: backend javob bermadi")
    send_message(chat_id, answer)


def handle_text(chat_id, text):
    resp = requests.post(CHAT_URL, json={"message": text})
    answer = resp.json().get("response", "❌ Xatolik: backend javob bermadi")
    send_message(chat_id, answer)


def handle_update(update):
    if "message" not in update:
        return

    msg = update["message"]
    chat_id = msg["chat"]["id"]

    # /start
    if "text" in msg and msg["text"].lower() == "/start":
        handle_start(chat_id)
        return

    # Voice message
    if "voice" in msg:
        file_id = msg["voice"]["file_id"]
        handle_voice(chat_id, file_id)
        return

    # Text
    if "text" in msg:
        handle_text(chat_id, msg["text"])
