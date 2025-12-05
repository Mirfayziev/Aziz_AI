import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")

app = FastAPI()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    if "message" not in data:
        return JSONResponse({"ok": True})

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # /start uchun alohida javob
    if text.lower() == "/start":
        send_message(chat_id, "👋 Salom! Men Aziz AI — sizning shaxsiy yordamchingizman!")
        return JSONResponse({"ok": True})

    # ==== BACKENDGA XABAR YUBORAMIZ ====
    try:
        resp = requests.post(CHAT_URL, json={"message": text})
        ai_msg = resp.json().get("reply", "⚠️ AI javob qaytara olmadi.")
    except Exception as e:
        ai_msg = f"Xatolik: {e}"

    # ==== TELEGRAMGA AI JAVOBINI QAYTARAMIZ ====
    send_message(chat_id, ai_msg)

    return JSONResponse({"ok": True})
