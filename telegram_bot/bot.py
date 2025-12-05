import os
import requests
from flask import Flask, request

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")  # e.g. https://azizai-production.up.railway.app/chat
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")  # e.g. https://azizai-production.up.railway.app/audio

app = Flask(__name__)

def tg_send(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data.get("message"):
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    if "text" in msg:
        text = msg["text"]
        if text.startswith("/start"):
            tg_send(chat_id, "👋 Salom! Aziz AI, sizning yordamchingiz.")
            return {"ok": True}
        # matnli xabar
        try:
            resp = requests.post(CHAT_URL, json={"message": text})
            ai_ans = resp.json().get("response", "⚠️ AI javobi topilmadi")
        except Exception as e:
            ai_ans = f"❗ Server xatosi: {e}"
        tg_send(chat_id, ai_ans)
        return {"ok": True}

    if "voice" in msg:
        # ovozli xabarni Telegram fayldan yuklab → backend /audio ga yubor → matnga aylantir → chatga yubor
        file_id = msg["voice"]["file_id"]
        file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        audio_bytes = requests.get(file_url).content

        files = {"file": ("voice.ogg", audio_bytes)}
        try:
            resp = requests.post(AUDIO_URL, files=files, timeout=30)
            text = resp.json().get("text", "")
        except Exception as e:
            text = f"🎙️ Ovozni matnga aylantirishda xato: {e}"

        # AI ga yubor
        try:
            resp2 = requests.post(CHAT_URL, json={"message": text})
            ai_ans = resp2.json().get("response", "⚠️ AI javobi topilmadi")
        except Exception as e:
            ai_ans = f"❗ Server xatosi: {e}"

        tg_send(chat_id, ai_ans)
        return {"ok": True}

    return {"ok": True}

@app.route("/", methods=["GET"])
def home():
    return "Bot server ishlayapti", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
