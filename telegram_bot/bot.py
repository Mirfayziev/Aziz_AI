import os
import logging
import httpx
from fastapi import FastAPI, Request

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BACKEND_URL = os.getenv("BACKEND_URL", "").strip().rstrip("/")
SEND_VOICE_DEFAULT = os.getenv("SEND_VOICE_DEFAULT", "1").strip() == "1"

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
if not BACKEND_URL:
    raise RuntimeError("BACKEND_URL is not set (example: https://azizai-production.up.railway.app)")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
TELEGRAM_FILE_API = f"https://api.telegram.org/file/bot{BOT_TOKEN}"

app = FastAPI()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("telegram_bot")


async def tg_send_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )


async def tg_send_voice(chat_id: int, audio_bytes: bytes):
    # Telegram expects OGG/OPUS bytes
    async with httpx.AsyncClient(timeout=60) as client:
        await client.post(
            f"{TELEGRAM_API}/sendVoice",
            data={"chat_id": str(chat_id)},
            files={"voice": ("voice.ogg", audio_bytes, "audio/ogg")},
        )


async def tg_download_file(file_id: str) -> bytes:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{TELEGRAM_API}/getFile", json={"file_id": file_id})
        r.raise_for_status()
        data = r.json()
        file_path = data["result"]["file_path"]

        file_url = f"{TELEGRAM_FILE_API}/{file_path}"
        fr = await client.get(file_url)
        fr.raise_for_status()
        return fr.content


def pick_reply_text(payload: dict) -> str:
    # backend responses can be {reply:..} or {text:..}
    for k in ("reply", "text", "message", "answer"):
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # fallback
    return "Xatolik yuz berdi (backend javobi bo‘sh)."


@app.get("/")
async def health():
    return {"ok": True, "service": "telegram_bot"}


@app.get("/webhook")
async def webhook_get():
    # Browser GET should not show "Method Not Allowed"
    return {"ok": True, "hint": "Telegram sends POST updates to this endpoint."}


@app.post("/webhook")
async def webhook_post(req: Request):
    try:
        update = await req.json()
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            return {"ok": True}

        chat_id = msg["chat"]["id"]

        # ============ TEXT ============
        if "text" in msg and msg["text"]:
            text = (msg["text"] or "").strip()

            if text.lower() in ("/start", "start"):
                await tg_send_message(
                    chat_id,
                    "Assalomu alaykum! Men Aziz AI.\n\n"
                    "Yozing yoki voice yuboring — men javob beraman.\n"
                    "Buyruqlar: /start",
                )
                return {"ok": True}

            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    f"{BACKEND_URL}/api/chat/chat",
                    json={"external_id": str(chat_id), "message": text},
                )
                r.raise_for_status()
                data = r.json()

            reply_text = pick_reply_text(data)
            await tg_send_message(chat_id, reply_text)

            if SEND_VOICE_DEFAULT:
                # get TTS audio as raw bytes
                async with httpx.AsyncClient(timeout=120) as client:
                    tr = await client.post(
                        f"{BACKEND_URL}/api/tts",
                        json={"text": reply_text},
                    )
                    tr.raise_for_status()
                    audio_bytes = tr.content
                if audio_bytes:
                    await tg_send_voice(chat_id, audio_bytes)

            return {"ok": True}

        # ============ VOICE ============
        if "voice" in msg and msg["voice"].get("file_id"):
            file_id = msg["voice"]["file_id"]
            voice_bytes = await tg_download_file(file_id)

            # 1) STT
            async with httpx.AsyncClient(timeout=180) as client:
                files = {"file": ("voice.ogg", voice_bytes, "audio/ogg")}
                ar = await client.post(f"{BACKEND_URL}/api/audio", files=files)
                ar.raise_for_status()
                stt = ar.json()

            user_text = (stt.get("text") or "").strip()
            if not user_text:
                await tg_send_message(chat_id, "Ovozni matnga aylantira olmadim. Qayta yuboring.")
                return {"ok": True}

            # 2) Chat
            async with httpx.AsyncClient(timeout=60) as client:
                cr = await client.post(
                    f"{BACKEND_URL}/api/chat/chat",
                    json={"external_id": str(chat_id), "message": user_text},
                )
                cr.raise_for_status()
                data = cr.json()

            reply_text = pick_reply_text(data)
            await tg_send_message(chat_id, f"🎙 Siz: {user_text}\n\n{reply_text}")

            # 3) TTS
            async with httpx.AsyncClient(timeout=120) as client:
                tr = await client.post(f"{BACKEND_URL}/api/tts", json={"text": reply_text})
                tr.raise_for_status()
                audio_bytes = tr.content

            if audio_bytes:
                await tg_send_voice(chat_id, audio_bytes)

            return {"ok": True}

        await tg_send_message(chat_id, "Faqat matn yoki voice yuboring.")
        return {"ok": True}

    except Exception as e:
        # IMPORTANT: never return 500 to Telegram; otherwise it retries
        log.exception("Webhook error: %s", e)
        return {"ok": True}
