import os
import httpx
from fastapi import FastAPI, Request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")  # masalan: https://azizai-production.up.railway.app

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]

    # TEXT
    if "text" in message:
        text = message["text"]
        answer, audio_hex = await ask_backend(text)

        await send_message(chat_id, answer)
        await send_voice(chat_id, bytes.fromhex(audio_hex))

    return {"ok": True}


async def ask_backend(text: str):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"{BACKEND_URL}/assistant-message",
            json={"text": text}
        )
        r.raise_for_status()
        data = r.json()
        return data["text"], data["audio"]


async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )


async def send_voice(chat_id: int, audio_bytes: bytes):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice",
            data={"chat_id": chat_id},
            files={"voice": ("answer.ogg", audio_bytes)}
        )
