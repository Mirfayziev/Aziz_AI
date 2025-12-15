import os, httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()

    if "message" not in update:
        return JSONResponse({"ok": True})

    message = update["message"]
    chat_id = message["chat"]["id"]

    if "text" not in message:
        return JSONResponse({"ok": True})

    text = message["text"]

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_URL}/assistant-message",
            json={"text": text},
            timeout=30
        )
        r.raise_for_status()
        data = r.json()

    # TEXT
    await client.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": data["text"]}
    )

    # AUDIO
    audio_bytes = bytes.fromhex(data["audio"])
    await client.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice",
        files={"voice": ("answer.ogg", audio_bytes)},
        data={"chat_id": chat_id}
    )

    return JSONResponse({"ok": True})
