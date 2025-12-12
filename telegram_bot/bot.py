import os
import logging
import httpx
from fastapi import FastAPI, Request, HTTPException

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BACKEND_URL = os.getenv("BACKEND_URL", "").strip().rstrip("/")
SEND_VOICE_DEFAULT = os.getenv("SEND_VOICE_DEFAULT", "1").strip() == "1"

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("telegram_bot")

CHAT = {}

def want_voice(chat_id: int) -> bool:
    return CHAT.get(chat_id, {}).get("voice", SEND_VOICE_DEFAULT)

def set_voice(chat_id: int, v: bool):
    st = CHAT.get(chat_id, {})
    st["voice"] = v
    CHAT[chat_id] = st

async def tg_send_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=20) as client:
        await client.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

async def tg_send_voice(chat_id: int, audio_hex: str):
    audio_bytes = bytes.fromhex(audio_hex)
    files = {"voice": ("answer.ogg", audio_bytes, "audio/ogg")}
    data = {"chat_id": str(chat_id)}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{TELEGRAM_API}/sendVoice", data=data, files=files)
        r.raise_for_status()

@app.get("/")
async def health():
    return {"ok": True, "service": "telegram_bot"}

@app.post("/webhook")
async def webhook(request: Request):
    if not BACKEND_URL:
        raise HTTPException(status_code=500, detail="BACKEND_URL is not set")

    update = await request.json()
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()

    if text.lower() in ["/start", "/help"]:
        await tg_send_message(
            chat_id,
            "Assalomu alaykum! Men Aziz AI botiman.\n\n"
            "Buyruqlar:\n"
            "• /ob-havo Toshkent\n"
            "• /yangilik sun'iy intellekt\n"
            "• /valyuta\n"
            "• /voice on | /voice off\n\n"
            "Yoki oddiy savol yozing — men javob beraman."
        )
        return {"ok": True}

    if text.lower().startswith("/voice"):
        parts = text.split()
        if len(parts) >= 2 and parts[1].lower() == "on":
            set_voice(chat_id, True)
            await tg_send_message(chat_id, "✅ Ovozli javob yoqildi.")
        elif len(parts) >= 2 and parts[1].lower() == "off":
            set_voice(chat_id, False)
            await tg_send_message(chat_id, "✅ Ovozli javob o‘chirildi.")
        else:
            await tg_send_message(chat_id, f"Ovozli javob: {'ON' if want_voice(chat_id) else 'OFF'}")
        return {"ok": True}

    payload = {"external_id": str(chat_id), "message": text, "want_voice": want_voice(chat_id)}

    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(f"{BACKEND_URL}/api/assistant/assistant-message", json=payload)
        r.raise_for_status()
        data = r.json()

    reply_text = data.get("text") or "Xatolik yuz berdi."
    await tg_send_message(chat_id, reply_text)

    audio_hex = data.get("audio_hex")
    if audio_hex:
        try:
            await tg_send_voice(chat_id, audio_hex)
        except Exception as e:
            log.exception("Failed to send voice: %s", e)

    return {"ok": True}
