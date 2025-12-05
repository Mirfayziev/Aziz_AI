# server.py
import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = f"https://focused-benevolence-production.up.railway.app/webhook"

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

app = FastAPI(title="Telegram Bot Webhook")

# --- BOT HANDLERS ---
@dp.message()
async def handle_message(message: types.Message):
    text = message.text or ""
    await message.answer(f"AI javobi test: {text}")


# --- LIFESPAN (startup + shutdown) ---
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Setting webhook...")
    await bot.set_webhook(WEBHOOK_URL)
    yield
    print("Deleting webhook...")
    await bot.delete_webhook()

app.router.lifespan_context = lifespan


# --- TELEGRAM WEBHOOK ROUTE ---
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update.construct(**data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}


@app.get("/")
async def home():
    return {"message": "Telegram bot is running ✔️"}
