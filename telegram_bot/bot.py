import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
import asyncio

# ============================
# ENV O'ZGARUVCHILAR
# ============================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN topilmadi")
if not CHAT_URL:
    raise ValueError("AZIZ_BACKEND_CHAT_URL topilmadi")

# ============================
# LOGGING
# ============================

logging.basicConfig(level=logging.INFO)

# ============================
# BOT INIT
# ============================

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ============================
# /start
# ============================

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "✅ <b>Aziz AI ishga tushdi!</b>\n\n"
        "Menga istalgan savolingizni yozing."
    )

# ============================
# ASOSIY CHAT
# ============================

@dp.message()
async def chat_handler(message: Message):
    user_text = message.text
    chat_id = message.chat.id

    payload = {
        "message": user_text,
        "external_id": str(chat_id)
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(CHAT_URL, json=payload) as resp:
                if resp.status != 200:
                    await message.answer(f"⚠️ Backend xatosi: {resp.status}")
                    return

                data = await resp.json()

                if isinstance(data, dict) and "response" in data:
                    reply = data["response"]
                else:
                    reply = str(data)

                await message.answer(reply)

    except Exception as e:
        logging.exception("Xatolik:")
        await message.answer("❌ Server bilan bog‘lanishda xato yuz berdi.")

# ============================
# RUN
# ============================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
