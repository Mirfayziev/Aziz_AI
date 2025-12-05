from fastapi import FastAPI, Request
import asyncio
from bot import dp, bot

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    await dp.feed_webhook_update(bot, data)
    return {"ok": True}

@app.get("/")
async def home():
    return {"message": "Telegram bot running ✔️"}
