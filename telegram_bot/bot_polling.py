import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL")  # <<< MUHIM

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message()
async def ai_chat(message: types.Message):
    # Debug uchun: env bor-yo‘qligini tekshiramiz
    if not BACKEND_CHAT_URL:
        await message.answer("⚠️ BACKEND_CHAT_URL o‘rnatilmagan. Railway → Bot service → Variables dan tekshiring.")
        return

    user_text = message.text or ""

    payload = {
        "user_external_id": str(message.from_user.id),
        "message": user_text,
        "model_tier": "basic",
    }

    try:
        resp = requests.post(BACKEND_CHAT_URL, json=payload, timeout=15)
        data = resp.json()
        reply_text = data.get("reply", "❗ AI javob qaytarmadi.")
    except Exception as e:
        reply_text = f"⚠️ Xatolik: {e}"

    await message.answer(reply_text)


async def main():
    print("🤖 Bot polling started...")
    print("BACKEND_CHAT_URL =", BACKEND_CHAT_URL)  # LOGDA ANIQ KO‘RASAN
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
