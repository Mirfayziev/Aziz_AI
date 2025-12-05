import os
import requests
from flask import Flask, request

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    # ------------------------
    # 1️⃣ Matnli xabar
    # ------------------------
    if "text" in msg:
        text = msg["text"]

        # /start
        if text.lower().startswith("/start"):
            welcome = (
                "✨ *Assalomu alaykum, Aziz!* ✨\n\n"
                "Men — **Aziz AI**, sizning shaxsiy sun’iy intellekt yordamchingizman.\n"
                "Savolingizni yuboring yoki ovozli habar jo‘nating 🎙️👇"
            )
            send_message(chat_id, welcome)
            return {"ok": True}

        try:
            res = requests.post(CHAT_URL, json={"message": text, "user_id": str(chat_id)})
            ai_answer = res.json().get("response", "AI javob bera olmadi.")
        except Exception as e:
            ai_answer = f"❗ Server bilan muammo: {str(e)}"

        send_message(chat_id, ai_answer)
        return {"ok": True}

    # ------------------------
    # 2️⃣ Voice (Ovozli habar)
    # ------------------------
    if "voice" in msg:
        try:
            file_id = msg["voice"]["file_id"]

            # Telegramdan file linkni olish
            file_info = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"
            ).json()

            file_path = file_info["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

            # Audio faylni yuklab olish
            audio_bytes = requests.get(file_url).content

            # Backendga yuborish
            files = {"file": ("voice.ogg", audio_bytes)}
            res = requests.post(AUDIO_URL, files=files)

            text = res.json().get("text", "Ovozni matnga aylantirib bo‘lmadi.")

            # Endi matnni chat-modelga yuborish
            chat_res = requests.post(CHAT_URL, json={"message": text, "user_id": str(chat_id)})
            ai_answer = chat_res.json().get("response", text)

        except Exception as e:
            ai_answer = f"🎙️ Ovozli xabarda xatolik: {e}"

        send_message(chat_id, ai_answer)
        return {"ok": True}

    return {"ok": True}


@app.route("/")
def home():
    return "Bot ishlayapti!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
