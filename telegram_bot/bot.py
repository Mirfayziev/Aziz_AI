import os
import logging
import httpx
from fastapi import FastAPI, Request

# ===================== CONFIG =====================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "").rstrip("/")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
if not BACKEND_URL:
    raise RuntimeError("BACKEND_URL is not set")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
TELEGRAM_FILE_API = f"https://api.telegram.org/file/bot{BOT_TOKEN}"

# ===================== APP =====================
app = FastAPI()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("telegram_bot")

# ===================== TELEGRAM HELPERS =====================
async def tg_send_text(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )

async def tg_send_voice(chat_id: int, audio_bytes: bytes):
    async with httpx.AsyncClient(timeout=60) as client:
        await client.post(
            f"{TELEGRAM_API}/sendVoice",
            data={"chat_id": str(chat_id)},
            files={"voice": ("voice.ogg", audio_bytes, "audio/ogg")},
        )

async def tg_download_voice(file_id: str) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{TELEGRAM_API}/getFile",
            json={"file_id": file_id},
        )
        r.raise_for_status()
        file_path = r.json()["result"]["file_path"]

        fr = await client.get(f"{TELEGRAM_FILE_API}/{file_path}")
        fr.raise_for_status()
        return fr.content

# ===================== HEALTH =====================
@app.get("/")
async def health():
    return {"ok": True}

@app.get("/webhook")
async def webhook_get():
    return {"ok": True}

# ===================== WEBHOOK =====================
@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        update = await req.json()
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            return {"ok": True}

        chat_id = msg["chat"]["id"]

        # ===== TEXT MESSAGE =====
        if "text" in msg:
            user_text = msg["text"].strip()

            if user_text.lower() in ("/start", "start"):
                await tg_send_text(
                    chat_id,
                    "Assalomu alaykum.\n"
                    "Men Aziz AI — sening shaxsiy kloningman.\n\n"
                    "Savol yoz yoki ovoz yubor."
                )
                return {"ok": True}

            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(
                    f"{BACKEND_URL}/assistant-message",
                    json={
                        "external_id": str(chat_id),
                        "message": user_text,
                        "want_voice": True
                    },
                )
                r.raise_for_status()
                data = r.json()

            text_reply = data.get("text") or data.get("reply") or "Javob olinmadi."
            await tg_send_text(chat_id, text_reply)

            if data.get("audio_hex"):
                audio_bytes = bytes.fromhex(data["audio_hex"])
                await tg_send_voice(chat_id, audio_bytes)

            return {"ok": True}

        # ===== VOICE MESSAGE =====
        if "voice" in msg:
            voice_bytes = await tg_download_voice(msg["voice"]["file_id"])

            async with httpx.AsyncClient(timeout=180) as client:
                r = await client.post(
                    f"{BACKEND_URL}/assistant-message",
                    files={"voice": ("voice.ogg", voice_bytes, "audio/ogg")},
                    data={
                        "external_id": str(chat_id),
                        "want_voice": True
                    },
                )
                r.raise_for_status()
                data = r.json()

            text_reply = data.get("text") or "Javob olinmadi."
            await tg_send_text(chat_id, text_reply)

            if data.get("audio_hex"):
                audio_bytes = bytes.fromhex(data["audio_hex"])
                await tg_send_voice(chat_id, audio_bytes)

            return {"ok": True}

        return {"ok": True}

    except Exception as e:
        log.exception("Telegram webhook error: %s", e)
        # MUHIM: Telegram 500 ko‘rmasin
        return {"ok": True}
