import os
import bot as tg_bot
from fastapi import FastAPI, Request
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(title="Aziz AI Telegram Bot")

@app.get("/")
async def root():
    return {"message": "Aziz AI Telegram bot working ✔️"}

@app.post("/telegram-webhook")
async def webhook(request: Request):
    update = await request.json()

    message = update.get("message") or {}
    chat = message.get("chat")
    if not chat:
        return {"ok": True}

    if "text" in message:
        await tg_bot.handle_text_message(message)
    elif "voice" in message:
        await tg_bot.handle_voice_message(message)

    return {"ok": True}
