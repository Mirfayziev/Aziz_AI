import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10
    )

def handle_update(update):
    if "message" not in update:
        return
    msg = update["message"]
    chat_id = msg["chat"]["id"]

    if "text" in msg:
        text = msg["text"]
        if text.lower() == "/start":
            send_message(chat_id, "👋 Assalomu alaykum, Aziz! ✨")
            return
        resp = requests.post(CHAT_URL, json={"chat_id": chat_id, "message": text})
        if resp.ok:
            reply = resp.json().get("reply", "")
        else:
            reply = "Server bilan bog‘lanishda xato"
        send_message(chat_id, reply)
        return

    if "voice" in msg:
        file_id = msg["voice"]["file_id"]
        info = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}", timeout=10).json()
        file_path = info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        file_bytes = requests.get(file_url, timeout=20).content

        files = {"file": file_bytes}
        resp = requests.post(AUDIO_URL, files=files, timeout=60)
        if resp.ok:
            reply = resp.json().get("text", "")
        else:
            reply = "Server bilan bog‘lanishda xato"
        send_message(chat_id, reply)
        return
