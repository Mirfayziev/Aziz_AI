import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL")  # Masalan: https://your-backend.onrender.com/api/chat

bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message()
async def ai_chat(message: types.Message):
    user_text = message.text

    payload = {
        "message": user_text,
        "user_id": str(message.from_user.id)
    }

    try:
        response = requests.post(BACKEND_CHAT_URL, json=payload, timeout=15)
        data = response.json()
        answer = data.get("reply", "❗AI javob qaytarmadi.")
    except Exception as e:
        answer = f"⚠️ Xatolik: {e}"

    await message.answer(answer)

async def main():
    print("🤖 AI Polling Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
