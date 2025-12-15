import os
import uuid
import httpx
from fastapi import FastAPI, Request
from services.stt_service import speech_to_text
from services.tts_service import text_to_speech

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    # 1️⃣ TEXT
    if "text" in message:
        user_text = message["text"]
        reply = await send_to_backend(user_text)
        await send_voice_and_text(chat_id, reply)

    # 2️⃣ VOICE
    elif "voice" in message:
        file_id = message["voice"]["file_id"]
        ogg_path = await download_voice(file_id)
        user_text = await speech_to_text(ogg_path)

        reply = await send_to_backend(user_text)
        await send_voice_and_text(chat_id, reply)

    return {"ok": True}


async def send_to_backend(text: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_URL}/assistant-message",
            json={"message": text}
        )
        r.raise_for_status()
        return r.json()["answer"]


async def send_voice_and_text(chat_id: int, text: str):
    voice_path = f"/tmp/{uuid.uuid4()}.mp3"
    await text_to_speech(text, voice_path)

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text}
        )

        with open(voice_path, "rb") as f:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice",
                data={"chat_id": chat_id},
                files={"voice": f}
            )


async def download_voice(file_id: str) -> str:
    async with httpx.AsyncClient() as client:
        file_info = await client.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile",
            params={"file_id": file_id}
        )
        file_path = file_info.json()["result"]["file_path"]

        file_data = await client.get(
            f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        )

    ogg_path = f"/tmp/{uuid.uuid4()}.ogg"
    with open(ogg_path, "wb") as f:
        f.write(file_data.content)

    return ogg_path
