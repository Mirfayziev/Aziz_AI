import os
import uuid
import httpx
from fastapi import FastAPI, Request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")  # masalan: https://azizai-production.up.railway.app

app = FastAPI()


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    if "text" in message:
        await handle_text(chat_id, message["text"])

    elif "voice" in message:
        await handle_voice(chat_id, message["voice"]["file_id"])

    return {"ok": True}


async def handle_text(chat_id: int, text: str):
    answer, voice = await ask_backend(text)
    await send_text(chat_id, answer)
    await send_voice(chat_id, voice)


async def handle_voice(chat_id: int, file_id: str):
    answer, voice = await ask_backend_voice(file_id)
    await send_text(chat_id, answer)
    await send_voice(chat_id, voice)


async def ask_backend(text: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_URL}/assistant-message",
            json={"message": text}
        )
        r.raise_for_status()
        data = r.json()
        return data["answer"], data["voice_base64"]


async def ask_backend_voice(file_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_URL}/assistant-voice",
            json={"file_id": file_id}
        )
        r.raise_for_status()
        data = r.json()
        return data["answer"], data["voice_base64"]


async def send_text(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )


async def send_voice(chat_id: int, voice_base64: str):
    import base64
    voice_bytes = base64.b64decode(voice_base64)
    filename = f"/tmp/{uuid.uuid4()}.mp3"

    with open(filename, "wb") as f:
        f.write(voice_bytes)

    async with httpx.AsyncClient() as client:
        with open(filename, "rb") as f:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice",
                data={"chat_id": chat_id},
                files={"voice": f}
            )
