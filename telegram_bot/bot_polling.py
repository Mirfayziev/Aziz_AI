import os
import asyncio
import requests
import base64
from aiogram import Bot, Dispatcher, types

# ====== ENV ======
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL", "").strip()
BACKEND_AUDIO_URL = os.getenv("BACKEND_AUDIO_URL", "").strip()
BACKEND_PLANNER_URL = os.getenv("BACKEND_PLANNER_URL", "").strip()


bot = Bot(TOKEN)
dp = Dispatcher()


# ============ MODEL TIER (foydalanuvchi buyruqlariga qarab) ============
def detect_tier(message: types.Message) -> str:
    text = message.text.lower() if message.text else ""
    if text.startswith("/fast"):
        return "fast"
    if text.startswith("/deep"):
        return "deep"
    return "default"


# ============ PLANNER FUNKSIYALARI ============

def is_planner_query(text: str) -> bool:
    if not text:
        return False

    text = text.lower().strip()

    triggers = [
        "bugun", "bugungi reja", "bugungi ishlar",
        "ertaga", "ertangi reja", "ertangi ishlar",
        "haftalik reja", "hafta reja",
        "oylik reja", "oylik strategiya",
        "plan", "reja"
    ]
    return any(t in text for t in triggers)


def call_planner_api(user_id: int, text: str, model_tier: str):
    if not BACKEND_PLANNER_URL:
        return "⚠️ BACKEND_PLANNER_URL o‘rnatilmagan."

    payload = {
        "user_id": user_id,
        "query": text,
        "model_tier": model_tier
    }

    try:
        resp = requests.post(BACKEND_PLANNER_URL, json=payload, timeout=60)
        data = resp.json()
        return data.get("result", "⚠️ Reja qaytmadi.")
    except Exception as e:
        return f"⚠️ Planner API xatosi: {e}"


# ============ ASOSIY HANDLER ============
@dp.message()
async def ai_handler(message: types.Message):

    user_id = int(message.from_user.id)
    model_tier = detect_tier(message)

    # 1) VOICE MESSAGE
    if message.voice:

        if not BACKEND_AUDIO_URL:
            await message.answer("⚠️ BACKEND_AUDIO_URL o‘rnatilmagan.")
            return

        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)

        audio_b64 = base64.b64encode(file_bytes.read()).decode()

        payload = {
            "user_id": user_id,
            "audio_base64": audio_b64,
            "model_tier": model_tier
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

    # 2) PLANNER TRIGGER
    if message.text and is_planner_query(message.text):
        await message.answer("⏳ Reja tuzilmoqda...")

        plan = call_planner_api(
            user_id=user_id,
            text=message.text,
            model_tier=model_tier
        )

        await message.answer(
            f"🗓 **Siz uchun reja tayyor:**\n\n{plan}",
            parse_mode="Markdown"
        )

        return

    # 3) TEXT CHAT — MEMORY + AI
    if not BACKEND_CHAT_URL:
        await message.answer("⚠️ BACKEND_CHAT_URL o‘rnatilmagan.")
        return

    payload = {
        "user_id": user_id,
        "message": message.text,
        "model_tier": model_tier
    }

    try:
        resp = requests.post(BACKEND_CHAT_URL, json=payload, timeout=30)
        data = resp.json()
        reply_text = data.get("reply", "❗ AI javob qaytarmadi.")
    except Exception as e:
        reply_text = f"⚠️ Chat xatosi: {e}"

    await message.answer(reply_text)


# ============ MAIN ============
async def main():
    print("🤖 Bot polling started...")
    print("BACKEND_CHAT_URL =", BACKEND_CHAT_URL)
    print("BACKEND_AUDIO_URL =", BACKEND_AUDIO_URL)
    print("BACKEND_PLANNER_URL =", BACKEND_PLANNER_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
