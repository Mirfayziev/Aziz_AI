import os
import asyncio
import requests
import base64
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL")
BACKEND_AUDIO_URL = os.getenv("BACKEND_AUDIO_URL")

bot = Bot(TOKEN)
dp = Dispatcher()

# ============ MODEL TIER (foydalanuvchi buyruqlariga qarab) ============
def detect_tier(message: types.Message) -> str:
    text = message.text.lower() if message.text else ""

    if text.startswith("/fast"):
        return "fast"
    if text.startswith("/deep"):
        return "deep"
    return "default"   # ChatGPT darajasida ishlovchi asosiy model


# ============ HANDLER ==============
@dp.message()
async def ai_handler(message: types.Message):

    model_tier = detect_tier(message)

    # 1) VOICE MESSAGE (AUDIO)
    if message.voice:

        if not BACKEND_AUDIO_URL:
            await message.answer("⚠️ BACKEND_AUDIO_URL o‘rnatilmagan.")
            return

        # file id olish
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)

        # Base64 ga o‘tkazish
        audio_b64 = base64.b64encode(file_bytes.read()).decode()

        payload = {
            "user_external_id": str(message.from_user.id),
            "audio_base64": audio_b64,
            "model_tier": model_tier   # <<< TIER
        }

        try:
            resp = requests.post(BACKEND_AUDIO_URL, json=payload, timeout=60)
            data = resp.json()

            text = data.get("text", "(matn olinmadi)")
            reply = data.get("reply", "(javob olinmadi)")

            await message.answer(
                f"🎙 *Matn*: {text}\n\n🤖 *AI javobi*: {reply}",
                parse_mode="Markdown"
            )

        except Exception as e:
            await message.answer(f"⚠️ AUDIO xatosi: {e}")

        return

    # 2) TEXT MESSAGE (CHAT)
    if not BACKEND_CHAT_URL:
        await message.answer("⚠️ BACKEND_CHAT_URL o‘rnatilmagan.")
        return

    payload = {
        "user_external_id": str(message.from_user.id),
        "message": message.text,
        "model_tier": model_tier   # <<< TIER
    }

    try:
        resp = requests.post(BACKEND_CHAT_URL, json=payload, timeout=30)
        data = resp.json()
        reply_text = data.get("reply", "❗ AI javob qaytarmadi.")
    except Exception as e:
        reply_text = f"⚠️ Xatolik: {e}"

    await message.answer(reply_text)


# ============ MAIN =============
async def main():
    print("🤖 Bot polling started...")
    print("BACKEND_CHAT_URL =", BACKEND_CHAT_URL)
    print("BACKEND_AUDIO_URL =", BACKEND_AUDIO_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
