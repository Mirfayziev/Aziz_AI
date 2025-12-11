import os
import logging
from fastapi import FastAPI, Request
import aiohttp

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_URL = os.getenv("AZIZ_BACKEND_AUDIO_URL")
TTS_URL = os.getenv("AZIZ_BACKEND_TTS_URL")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
TELEGRAM_FILE_API = f"https://api.telegram.org/file/bot{TOKEN}"

log = logging.getLogger("aziz_ai_bot")
app = FastAPI()


async def tg_send_message(session, chat_id, text, reply_to=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    await session.post(f"{TELEGRAM_API}/sendMessage", json=payload)


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    async with aiohttp.ClientSession() as session:
        # BACKEND CHAT
        params = {"message": text, "external_id": str(chat_id)}
        async with session.post(CHAT_URL, params=params) as resp:
            backend = await resp.json()

        reply = backend.get("reply", "⚠️ Xato: backend javob bermadi")

        await tg_send_message(session, chat_id, reply)

    return {"ok": True}


@app.get("/")
def home():
    return {"status": "telegram bot is running"}
