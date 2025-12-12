import os
import httpx
from fastapi import FastAPI, Request

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL").rstrip("/")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()


async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )


@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        update = await req.json()
        msg = update.get("message")
        if not msg or "text" not in msg:
            return {"ok": True}

        chat_id = msg["chat"]["id"]
        text = msg["text"]

        # 1️⃣ BACKEND’GA YUBORAMIZ
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{BACKEND_URL}/api/assistant",
                json={
                    "external_id": str(chat_id),
                    "message": text,
                },
            )
            data = r.json()

        # 2️⃣ JAVOBNI TELEGRAM’GA QAYTARAMIZ
        reply = data.get("reply", "Xatolik yuz berdi")
        await send_message(chat_id, reply)

        return {"ok": True}

    except Exception as e:
        print("Telegram webhook error:", e)
        return {"ok": True}
