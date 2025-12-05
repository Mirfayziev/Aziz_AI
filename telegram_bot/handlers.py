from aiogram import types
import requests
from config import CHAT_URL, AUDIO_URL

async def handle_text(message: types.Message):
    user_text = message.text

    payload = {
        "message": user_text,
        "user_id": str(message.from_user.id)
    }

    # backend AI bilan gaplashish:
    response = requests.post(CHAT_URL, json=payload).json()

    await message.answer(response.get("reply", "Xatolik yuz berdi."))
