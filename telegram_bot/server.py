from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

BOT_API = f"https://api.telegram.org/bot{TOKEN}"

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    try:
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        if not chat_id:
            return {"ok": True}

        # TEST RESPONSE — HOZIRCHA SHU BO‘LADI
        payload = {
            "chat_id": chat_id,
            "text": "Bot ishlayapti! 🔥"
        }

        async with httpx.AsyncClient() as client:
            await client.post(f"{BOT_API}/sendMessage", json=payload)

        return {"ok": True}

    except Exception as e:
        print("Webhook error:", e)
        return {"ok": False}
