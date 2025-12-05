# telegram_bot/bot_polling.py

import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@dp.message()
async def handle_message(message: types.Message):
    text = message.text or ""
    # Hozircha oddiy test javob
    await message.answer(f"AI javobi test (polling): {text}")


async def main():
    print("🤖 Telegram polling bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
