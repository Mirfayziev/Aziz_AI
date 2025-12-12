import os
import httpx
from fastapi import FastAPI, Request

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
BACKEND_URL = os.environ["BACKEND_URL"]  # https://azizai-production.up.railway.app

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    payload = {
        "user_external_id": str(chat_id),
        "question": text,
        "model_tier": "pro"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"{BACKEND_URL}/assistant-message",
            json=payload
        )
        r.raise_for_status()
        answer = r.json()["answer"]

    # TEXT
    await client.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": answer}
    )

    # 🔊 AUDIO (TTS backenddan)
    audio = await client.post(
        f"{BACKEND_URL}/api/tts",
        json={"text": answer}
    )

    await client.post(
        f"{TELEGRAM_API}/sendVoice",
        data={"chat_id": chat_id},
        files={"voice": audio.content}
    )

    return {"ok": True}
