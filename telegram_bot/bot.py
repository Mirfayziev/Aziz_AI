import os
import binascii
import httpx
from fastapi import FastAPI, Request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BACKEND_URL = os.getenv("BACKEND_URL", "").rstrip("/")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
if not BACKEND_URL:
    raise RuntimeError("BACKEND_URL is not set")

app = FastAPI()


async def tg_api(method: str, *, json=None, data=None, files=None, params=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=json, data=data, files=files, params=params)
        r.raise_for_status()
        return r.json()


async def send_message(chat_id: int, text: str):
    await tg_api("sendMessage", json={"chat_id": chat_id, "text": text})


async def send_voice(chat_id: int, audio_bytes: bytes):
    # audio_bytes expected to be OPUS (ogg/opus container is acceptable for Telegram voice)
    await tg_api(
        "sendVoice",
        data={"chat_id": str(chat_id)},
        files={"voice": ("answer.ogg", audio_bytes, "audio/ogg")}
    )


async def download_telegram_file(file_id: str) -> bytes:
    info = await tg_api("getFile", params={"file_id": file_id})
    file_path = info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(file_url)
        r.raise_for_status()
        return r.content


async def backend_text_chat(text: str) -> dict:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{BACKEND_URL}/assistant-message", json={"text": text})
        r.raise_for_status()
        return r.json()


async def backend_voice_chat(audio_bytes: bytes) -> dict:
    async with httpx.AsyncClient(timeout=180) as client:
        files = {"file": ("voice.ogg", audio_bytes, "audio/ogg")}
        r = await client.post(f"{BACKEND_URL}/voice-chat", files=files)
        r.raise_for_status()
        return r.json()


@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    message = update.get("message") or update.get("edited_message")
    if not message:
        return {"ok": True}

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if not chat_id:
        return {"ok": True}

    # 1) TEXT flow
    if "text" in message and message["text"]:
        user_text = message["text"].strip()
        res = await backend_text_chat(user_text)
        answer = res.get("text") or ""
        audio_hex = res.get("audio") or ""
        await send_message(chat_id, answer)

        if audio_hex:
            try:
                audio_bytes = binascii.unhexlify(audio_hex)
                await send_voice(chat_id, audio_bytes)
            except Exception:
                # If audio fails, we still delivered text.
                pass

        return {"ok": True}

    # 2) VOICE flow
    if "voice" in message and message["voice"]:
        file_id = message["voice"].get("file_id")
        if not file_id:
            return {"ok": True}

        try:
            voice_bytes = await download_telegram_file(file_id)
            res = await backend_voice_chat(voice_bytes)

            if res.get("error"):
                await send_message(chat_id, f"STT xato: {res['error']}")
                return {"ok": True}

            answer = res.get("text") or ""
            audio_hex = res.get("audio") or ""
            await send_message(chat_id, answer)

            if audio_hex:
                try:
                    audio_bytes = binascii.unhexlify(audio_hex)
                    await send_voice(chat_id, audio_bytes)
                except Exception:
                    pass

        except Exception:
            await send_message(chat_id, "Ovozli xabarni qayta ishlashda xatolik yuz berdi.")
        return {"ok": True}

    return {"ok": True}
