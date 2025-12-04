import os
from flask import Flask, request, jsonify
from bot import handle_update

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Telegram bot running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    handle_update(update)
    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
