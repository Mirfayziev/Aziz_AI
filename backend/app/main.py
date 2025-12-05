import asyncio
import os
import base64
import requests
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL")
BACKEND_AUDIO_URL = os.getenv("BACKEND_AUDIO_URL")

bot = Bot(TOKEN)
dp = Dispatcher()


# ==== TEXT HANDLER ====
@dp.message()
async def text_handler(message: types.Message):

    if message.voice:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)
        audio_b64 = base64.b64encode(file_bytes.read()).decode()

        payload = {
            "user_external_id": str(message.from_user.id),
            "audio_base64": audio_b64,
            "model_tier": "basic"
        }

        r = requests.post(BACKEND_AUDIO_URL, json=payload, timeout=40)
        data = r.json()

        await message.answer(
            f"🎙 Matn: {data.get('text')}\n\n🤖 Javob: {data.get('reply')}"
        )
        return

    # TEXT → AI chat
    payload = {
        "user_external_id": str(message.from_user.id),
        "message": message.text,
        "model_tier": "basic"
    }
    r = requests.post(BACKEND_CHAT_URL, json=payload, timeout=20)
    data = r.json()

    await message.answer(data.get("reply", "AI javob qaytarmadi."))
    


async def main():
    print("🤖 Bot polling started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
