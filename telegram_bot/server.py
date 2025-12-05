import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
import asyncio

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

app = FastAPI()


# Webhook handler
@app.post("/webhook")
async def webhook(request: Request):
    json_data = await request.json()
    update = Update(**json_data)
    await dp.feed_update(bot, update)
    return {"ok": True}


# Bot start command
@dp.message()
async def all_messages(message: types.Message):
    await message.answer("AI javobi kelayapti... 🔄")


@app.on_event("startup")
async def on_startup():
    webhook_url = os.getenv("WEBHOOK_URL")
    await bot.set_webhook(webhook_url)
    print("Webhook set:", webhook_url)
