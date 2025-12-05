import os
import httpx
from aiogram import Bot, Dispatcher, types

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

CHAT_API = os.getenv("AZIZ_BACKEND_CHAT_URL")
AUDIO_API = os.getenv("AZIZ_BACKEND_AUDIO_URL")

@dp.message()
async def handler(msg: types.Message):
    user_text = msg.text

    async with httpx.AsyncClient() as client:
        res = await client.post(CHAT_API, json={"text": user_text})

    ai_text = res.json().get("response", "❌ AI javobi topilmadi")

    await msg.answer(ai_text)
