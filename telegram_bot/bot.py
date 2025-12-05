import os
import httpx
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")
bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message()
async def all_messages(message: types.Message):

    # Foydalanuvchi xabari
    user_text = message.text

    # Backendga yuboramiz
    async with httpx.AsyncClient() as client:
        response = await client.post(
            CHAT_URL,
            json={"message": user_text}
        )

    if response.status_code != 200:
        await message.answer("⚠️ Server javob bermadi, keyinroq urinib ko‘ring.")
        return

    ai_text = response.json().get("reply", "⚠️ AI javobi topilmadi.")

    await message.answer(ai_text)
