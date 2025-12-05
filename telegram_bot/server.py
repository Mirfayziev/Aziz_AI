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
    print("Setting
