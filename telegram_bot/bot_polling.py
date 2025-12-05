# bot_polling.py
import os
import asyncio
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Polling OK ✔️\nYou said: {message.text}")

async def main():
    print("🤖 Bot polling started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
