import os
import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, Update

# Muhit o'zgaruvchilari
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_CHAT_URL = os.getenv("AZIZ_BACKEND_CHAT_URL")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment o'zgaruvchisi topilmadi")

if not BACKEND_CHAT_URL:
    raise RuntimeError("AZIZ_BACKEND_CHAT_URL environment o'zgaruvchisi topilmadi")

# Aiogram obyektlari
bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


# /start komandasi – faqat Aziz uchun chiroyli xush kelibsiz
@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome = (
        "👋 <b>Assalomu alaykum, Aziz!</b>\n\n"
        "Men — <b>Aziz AI</b>, sening shaxsiy sun'iy intellekt yordamching.\n\n"
        "🧠 Men sening odatlaringni, uslublaringni va ehtiyojlaringni asta-sekin o‘rganaman.\n"
        "📌 Mening vazifam:\n"
        "  • Savollaringga inson darajasida javob berish\n"
        "  • Kun tartibi va rejalaringni boshqarish\n"
        "  • Loyihalaring, kodlaring va g‘oyalaringni tartibga solish\n"
        "  • Hayotingni tahlil qilib, foydali xulosalar berish\n\n"
        "Endi istagan savolingni yozishing yoki ovoz yuborishing mumkin. 🔥"
    )
    await message.answer(welcome)


# Oddiy matn – backendga yuborib, AI javobini qaytaramiz
@dp.message(F.text)
async def handle_text(message: Message):
    user_text = message.text.strip()
    user_id = message.from_user.id

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                BACKEND_CHAT_URL,
                json={
                    "user_id": user_id,
                    "message": user_text,
                    "source": "telegram",
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        # Agar backend o'chib qolsa yoki xato bersa
        await message.answer(
            "⚠️ AI backend bilan ulanishda xato yuz berdi.\n"
            "Keyinroq yana urinib ko‘r yoki backend loglarini tekshir. "
            f"\n\nTexnik ma'lumot: <code>{e}</code>"
        )
        return

    # Backend javobini turli ko‘rinishlarda ushlab olishga harakat qilamiz
    ai_answer = (
        data.get("answer")
        or data.get("response")
        or data.get("message")
        or "AI javob qaytarmadi, backenddan ma'lumot topilmadi."
    )

    await message.answer(ai_answer)


async def process_update(update_dict: dict) -> None:
    """
    FastAPI webhook orqali kelgan raw JSON update’ni aiogram’ga uzatish.
    """
    update = Update.model_validate(update_dict)
    await dp.feed_update(bot, update)
