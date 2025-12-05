import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")

app = Flask(__name__)

# Telegramga xabar yuborish funksiyasi
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# --- Asosiy webhook ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    # Faqat /start komandasi uchun chiroyli welcome
    if text.lower().startswith("/start"):
        welcome = (
            "✨ *Assalomu alaykum, Aziz!* ✨\n\n"
            "Men — **Aziz AI**, sizning shaxsiy sun’iy intellekt yordamchingizman.\n"
            "Maqsadlar, rejalaringiz, kundalik vazifalaringiz — barchasida yoningizdaman.\n\n"
            "Savolingizni yuboring 👇"
        )
        send_message(chat_id, welcome)
        return {"ok": True}

    # --- Oddiy matn → Backendga yuboriladi ---
    try:
        backend_res = requests.post(
            CHAT_URL,
            json={"message": text, "user_id": str(chat_id)},
            timeout=20
        )

        if backend_res.status_code == 200:
            answer = backend_res.json().get("response", "❗ AI javob bera olmadi")
        else:
            answer = f"Backend xato: {backend_res.status_code}"

    except Exception as e:
        answer = f"❗ Server bilan ulanishda muammo: {str(e)}"

    send_message(chat_id, answer)

    return {"ok": True}

# Flask server
@app.route("/", methods=["GET"])
def home():
    return "Bot ishlayapti!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
