from fastapi import FastAPI, Request
import asyncio
from bot import bot, dp  # telegram bot import
import os

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


@app.on_event("startup")
async def on_startup():
    # Set Webhook
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")


@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return {"ok": True}


@app.get("/")
async def root():
    return {"message": "Telegram bot working ✔️"}
