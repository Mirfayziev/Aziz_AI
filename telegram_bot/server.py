# server.py
import os
from flask import Flask, request, jsonify
from bot import handle_update

app = Flask(__name__)

PORT = int(os.getenv("PORT", 8000))
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Aziz AI Telegram Bot is running!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data:
        handle_update(data)

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
