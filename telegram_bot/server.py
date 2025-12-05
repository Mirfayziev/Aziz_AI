from flask import Flask, request
import os
from bot import handle_telegram_update

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "AzizAI Telegram Bot Running ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    print("🔔 Update received:", update)
    handle_telegram_update(update)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
