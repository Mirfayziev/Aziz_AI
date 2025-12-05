from fastapi import FastAPI, Request, BackgroundTasks
import httpx
import os

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_API = f"https://api.telegram.org/bot{TOKEN}"

@app.get("/")
def home():
    return {"status": "running"}

# --- MESSAGE YUBORISH FUNKSIYASI ---
async def send_reply(chat_id: int, text: str):
    payload = {"chat_id": chat_id, "text": text}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(f"{BOT_API}/sendMessage", json=payload)
        except Exception as e:
            print("Telegram send error:", e)


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()

    # Har qanday update kelishi mumkin: message, callback, inline, member change...
    message = (
        data.get("message")
        or data.get("edited_message")
        or data.get("channel_post")
        or data.get("callback_query")
    )

    if not message:
        return {"ok": True}

    # callback_query bo‘lsa chat_id boshqacha bo‘ladi
    if "callback_query" in data:
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        text = data["callback_query"].get("data", "")
    else:
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

    # Backgroundda yuborish — webhook Telegramni kutib o‘tirmaydi
    background_tasks.add_task(send_reply, chat_id, "Bot ishlayapti! 🔥")

    # Webhook doim 200 qaytishi kerak!
    return {"ok": True}
